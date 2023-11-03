from typing import Union

import app.util.jobs as jobs
from app import api, job_queue, sio
from app.models.chat import Chat
from app.models.user import User
from app.services import chat as chsr
from app.services import user as ussr
from app.util import crypto

ResponseData = dict[str, Union[str, dict[str, str]]]

@sio.on("create-chat")
def handle_create_chat (resp: ResponseData) -> None:
    print(resp["msg"])

    if resp["status"] == "pending":
        data = resp["data"]

        user = ussr.find_with_id(api.user_id)
        owner = ussr.find_with_telephone(data["owner"]["telephone"])

        if owner is None:
            owner = User(
                name=data["owner"]["name"],
                telephone=data["owner"]["telephone"],
                desc=data["owner"]["description"]
            )

            ussr.insert_user(owner)

        chat = Chat(
            back_id=data["owner"]["chat_id"],
            users=[ owner.telephone ],
            name=data["name"],
            desc=data.get("description", "default description")
        )

        chsr.insert_chat(chat)

        print({
            "chat": {
                "name": chat.name,
                "bob-id": chat.back_id,
                "id": chat._id
            }
        })

        opkey = data["user"]["used_keys"][1]
        dh_ratchet_key = data["user"]["used_keys"][0]

        pvt_keys = {
            "IK": crypto.load_private_key("id_key"),
            "SPK": crypto.load_private_key("sgn_key"),
            "OPK": crypto.load_private_key(f"{opkey}_opk")
        }
        dh_ratchet = crypto.load_private_key(f"{dh_ratchet_key}_opk")
        user_ratchet = data["user"]["dh_ratchet"]
        root_ratchet = crypto.create_chat_encryption(
            pvt_keys, data["owner"]["keys"]["pb_keys"], sender=False
        )

        crypto.save_ratchet(chat._id, "dh_ratchet", dh_ratchet)
        crypto.save_ratchet(chat._id, "user_ratchet", user_ratchet)
        crypto.save_ratchet(chat._id, "root_ratchet", root_ratchet)

        try:
            data = {
                "Signed-Message": api.sign_message(),
                "telephone": user.telephone,
                "body": {
                    "owner": {
                        "telephone": data["owner"]["telephone"],
                        "chat_id": data["owner"]["chat_id"]
                    },
                    "user": {
                        "name": user.name,
                        "telephone": user.telephone,
                        "chat_id": str(chat._id),
                        "keys": {
                            "dh_ratchet": crypto.public_key(dh_ratchet),
                            "OPK": crypto.public_key(pvt_keys["OPK"]),
                            "IK": crypto.public_key(pvt_keys["IK"]),
                            "SPK": crypto.public_key(pvt_keys["SPK"])
                        }
                    },
                }
            }
            sio.emit("confirm-create-chat", data)

        except ConnectionRefusedError:
            print(f"Retry to send the confirmation of the creation of the chat {chat._id}")
            job_queue.add_job(api.user_id, 1, jobs.ConfirmCreateChatJob, data=data)

        except Exception as exc:
            print(f"Unkown error happened creating the chat {chat._id}")
            raise exc

@sio.on("confirm-create-chat")
def confirm_create_chat (resp: ResponseData) -> None:
    print(resp["msg"])

    if resp["status"] == "ok":
        data = resp["data"]

        user = ussr.find_with_telephone(data["user"]["telephone"])

        user_name = data["user"]["name"]
        if user.name == "default user" and user.name != user_name:
            ussr.update_user_name(user._id, user_name)

        chsr.update_back_id(
            data["owner"]["chat_id"], data["user"]["chat_id"]
        )
        chat = chsr.find_with_id(data["owner"]["chat_id"])

        eph_key = crypto.load_private_key(f"eph-{chat._id}-{api.user_id}")
        dh_ratchet = crypto.load_private_key(f"dhr-{chat._id}-{api.user_id}")

        user_ratchet = data["user"]["keys"].pop("dh_ratchet")
        user_keys = data["user"]["keys"]
        root_ratchet = crypto.create_chat_encryption(
            { "IK": api.id_key, "EK": eph_key }, pb_keys=user_keys, sender=True
        )

        print({
            "chat": {
                "name": chat.name,
                "bob-id": chat.back_id,
                "id": chat._id,
            }
        })

        crypto.save_ratchet(chat._id, "dh_ratchet", dh_ratchet)
        crypto.save_ratchet(chat._id, "user_ratchet", user_ratchet)
        crypto.save_ratchet(chat._id, "root_ratchet", root_ratchet)

        crypto.clean_chat_keys(chat._id, api.user_id)

@sio.on("message")
def handle_message (resp: ResponseData) -> None:
    print(resp["msg"])

    if resp["status"] == "pending":
        data = resp["data"]

        receiver = ussr.find_with_id(api.user_id)
        chat_id = data["receiver"]["chat_id"]

        cipher = crypto.encode_b64(data["cipher"])
        pbkey = crypto.load_public_key(data["dh_ratchet"])
        ratchets, _ = crypto.load_ratchets(chat_id)

        msg = crypto.rcv_msg(ratchets, pbkey, cipher)
        print("decoded message -> ", msg.decode("utf-8"))

        ratchets.pop("rcv_ratchet", None)

        ratchets["user_ratchet"] = data["dh_ratchet"]
        for ratchet_name, ratchet in ratchets.items():
            crypto.save_ratchet(chat_id, ratchet_name, ratchet)

        try:
            data = {
                "Signed-Message": api.sign_message(),
                "telephone": receiver.telephone,
                "body": {
                    "sender": data["sender"],
                    "receiver": data["receiver"],
                    "dh_ratchet": crypto.public_key(ratchets["dh_ratchet"])
                }
            }
            sio.emit("confirm-message", data)

        except ConnectionRefusedError:
            print("Retry to send the confirmation of the message received")
            job_queue.add_job(api.user_id, 2, jobs.ConfirmMessageJob, data=data, chat_id=chat_id)

        except Exception as exc:
            print("Unkown error happened")
            raise exc

@sio.on("confirm-message")
def handle_confirm_message (resp: ResponseData) -> None:
    print(resp["msg"])

    if resp["status"] == "ok":
        data = resp["data"]
        tmp_ratchets, _ = crypto.load_ratchets(data["sender"]["chat_id"], tmp=True)

        ratchets = { "user_ratchet": data["dh_ratchet"] }
        for key, value in tmp_ratchets.items():
            ratchet_name = key.removeprefix("tmp-")

            crypto.delete_ratchet(data["sender"]["chat_id"], ratchet_name, tmp=True)
            ratchets[ratchet_name] = value

        for ratchet_name, ratchet in ratchets.items():
            crypto.save_ratchet(data["sender"]["chat_id"], ratchet_name, ratchet)