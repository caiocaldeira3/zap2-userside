import asyncio
import dataclasses as dc
import time
from enum import Enum, auto

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from socketio.exceptions import ConnectionError
from werkzeug.security import generate_password_hash

from app import job_queue, sio
from app.models.chat import Chat
from app.models.user import User
from app.services import chat as chsr
from app.services import user as ussr
from app.util import config, crypto, jobs


class ConnectionResults (Enum):
    SUCESSFUL   = auto()
    RETRY       = auto()
    FAILED      = auto()

@dc.dataclass()
class Api:
    base_url: str = dc.field(init=False, default="http://0.0.0.0:5000")
    headers_client: dict = dc.field(init=False, default=None)
    headers_user: dict = dc.field(init=False, default=None)

    user_id: int = dc.field(init=False, default=None)
    id_key: X25519PrivateKey = dc.field(init=False, default=None)
    sgn_key: X25519PrivateKey = dc.field(init=False, default=None)
    ed_key: Ed25519PrivateKey = dc.field(init=False, default=None)

    def __init__ (self, logged_in: bool = False) -> None:
        self.headers_client = {
            "Param-Auth": config.CHAT_SECRET
        }
        self.headers_user = self.headers_client

        if logged_in and config.USER_ID != -1:
            self.login()

        elif logged_in:
            print("Api has not any session stored")
            raise ValueError

    def _setup_user (self) -> None:
        self.user_id = config.USER_ID
        self.id_key = crypto.load_private_key("id_key")
        self.sgn_key = crypto.load_private_key("sgn_key")
        self.ed_key = crypto.load_private_key("ed_key")

        self._update_header_user()

    def _setdown_user (self) -> None:
        self.user_id = None
        self.id_key = None
        self.sgn_key = None
        self.ed_key = None

        self._update_header_user(logout=True)

    def _update_header_user (self, logout: bool = False) -> None:
        if logout:
            self.headers_user.pop("Signed-Message", None)

        else:
            self.headers_user = {
                "Signed-Message": crypto.sign_message(self.ed_key)
            } | self.headers_client

    def sign_message (self) -> str:
        return crypto.sign_message(self.ed_key)

    def logout (self) -> None:
        self._setdown_user()

        try:
            sio.disconnect()

        except:
            pass

    def login (self) -> ConnectionResults:
        try:
            self._setup_user()
            user = ussr.find_with_id(self.user_id)

            sio.connect(
                self.base_url,
                auth={ "telephone": user.telephone },
                headers=self.headers_user
            )

            return ConnectionResults.SUCESSFUL

        except ConnectionError as exc:
            self._setdown_user()

            return ConnectionResults.FAILED

        except Exception as exc:
            print(exc)

            self._setdown_user()
            return ConnectionResults.FAILED

    def signup (self, name: str, telephone: str, password: str) -> ConnectionResults:
        self.id_key = crypto.generate_private_key("id_key")
        self.sgn_key = crypto.generate_private_key("sgn_key")
        self.ed_key = crypto.generate_private_key("ed_key", sgn_key=True)

        id_key = crypto.public_key(self.id_key)
        sgn_key = crypto.public_key(self.sgn_key)
        ed_key = crypto.public_key(self.ed_key)
        opkeys = [
            { "id": idx, "key": crypto.public_key(crypto.generate_private_key(f"{idx}_opk")) }
            for idx in range(1, 11)
        ]

        try:
            user = User(
                name=name,
                telephone=telephone,
                password=generate_password_hash(password)
            )
            ussr.insert_user(user)

            self.user_id = user._id

            sio.connect(
                self.base_url,
                auth={
                    "name": name,
                    "telephone": telephone,
                    "id_key": id_key,
                    "sgn_key": sgn_key,
                    "ed_key": ed_key,
                    "opkeys": opkeys
                }, headers=self.headers_client
            )

            self._update_header_user()
            config.update_user_id(self.user_id)

            return ConnectionResults.SUCESSFUL

        except ConnectionError as exc:
            ussr.delete_user(user.telephone)
            print(exc)

            self._setdown_user()

            return ConnectionResults.FAILED

    def create_chat (
        self, name: str, users: list[str], description: str = None
    ) -> ConnectionResults:
        try:
            owner = ussr.find_with_id(self.user_id)

            chat = Chat(
                name=name,
                users=users,
                desc=description
            )
            chsr.insert_chat(chat)

            eph_key = crypto.generate_private_key(f"eph-{chat._id}-{self.user_id}")
            dh_ratchet = crypto.generate_private_key(f"dhr-{chat._id}-{self.user_id}")

            data = {
                "Signed-Message": self.sign_message(),
                "telephone": owner.telephone,
                "body": {
                    "owner": {
                        "telephone": owner.telephone,
                        "chat_id": str(chat._id)
                    },
                    "name": name,
                    "users": users,
                    "dh_ratchet": crypto.public_key(dh_ratchet),
                    "EK": crypto.public_key(eph_key)
                },
            }
            sio.emit("create-chat", data=data)

            return ConnectionResults.SUCESSFUL

        except ConnectionRefusedError:
            print("Retry creating the chatroom")
            job_queue.add_job(self.user_id, 1, jobs.CreateChatJob, data=data, chat_id=chat._id)

            return ConnectionResults.RETRY

        except Exception as exc:
            print(exc)

            return ConnectionResults.FAILED

    def send_message (self, chat_id: int, msg: str, debug: bool = False) -> ConnectionResults:
        try:
            owner = ussr.find_with_id(self.user_id)
            chat = chsr.find_with_id(chat_id)

            ratchets, pbkey = crypto.load_ratchets(chat_id)
            bmsg = bytes(msg, encoding="utf-8")
            cipher, new_ratchet_pbkey = crypto.snd_msg(
                ratchets, pbkey, bmsg
            )

            if debug:
                print(f"encoded message -> {cipher}")

            data = {
                "Signed-Message": self.sign_message(),
                "telephone": owner.telephone,
                "body": {
                    "sender": {
                        "telephone": owner.telephone,
                        "chat_id": str(chat._id)
                    },
                    "receiver": {
                        "telephone": chat.users[0],
                        "chat_id": str(chat.back_id)
                    },
                    "cipher": crypto.decode_b64(cipher),
                    "dh_ratchet": new_ratchet_pbkey
                }
            }
            sio.send(data)

            ratchets.pop("snd_ratchet", None)
            ratchets.pop("user_ratchet", None)
            for ratchet_name, ratchet in ratchets.items():
                crypto.save_ratchet(chat_id, ratchet_name, ratchet, tmp=True)

            return ConnectionResults.SUCESSFUL

        except ConnectionRefusedError:
            job_queue.add_job(self.user_id, 2, jobs.SendMessageJob, data, chat._id)

            return ConnectionResults.RETRY

        except Exception as exc:
            print(exc)

            return ConnectionResults.FAILED

    async def _job_handler (self) -> None:
        while True:
            if self.user_id != -1:
                job_queue.resolve_jobs(self.user_id)
                time.sleep(5)

    def job_handler (self) -> None:
        asyncio.run(self._job_handler())

