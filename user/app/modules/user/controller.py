import os

# Import flask dependencies
from flask import Blueprint, json, Response, request, wrappers
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

# Import Util Modules
import app.util.crypto as crypto
from app.util.authentication import authenticate_source
from app.util.json_encoder import ComplexEncoder
from app.util.responses import (
    DuplicateError, NotFoundError, ServerError
)

# Import module models (i.e. Organization)
from app.models.user import User
from app.models.chat import Chat

# Import application Database
from app import db

# Define the blueprint: "org", set its url prefix: app.url/org
mod_user = Blueprint("user", __name__, url_prefix="/user")

# Set the route and accepted methods
@mod_user.route("/create-chat/", methods=["POST"])
@authenticate_source()
def create_chat () -> wrappers.Response:
    try:
        data = json.loads(request.json)

        owner = User.query.filter_by(telephone=data["owner"]["telephone"]).first()
        user = User.query.filter_by(id=os.environ["USER_ID"], telephone=data["user"]).one()
        if owner is None:
            owner = User(**data["owner"])

            db.session.add(owner)
            db.session.commit()

        chat = Chat(
            name = data["name"],
            users = [ owner ],
            chat_id = data["chat_id"],
            description = data.get("description", None)
        )

        db.session.add(chat)
        db.session.commit()

        opkey = data["used_keys"][1]
        dh_ratchet_key = data["used_keys"][0]

        pvt_keys = {
            "IK": crypto.load_private_key("id_key"),
            "SPK": crypto.load_private_key("sgn_key"),
            "OPK": crypto.load_private_key(f"{opkey}_opk")
        }
        dh_ratchet = crypto.load_private_key(f"{dh_ratchet_key}_opk")
        user_ratchet = data["dh_ratchet"]
        root_ratchet = crypto.create_chat_encryption(pvt_keys, data["keys"]["pb_keys"], sender=False)

        crypto.save_ratchet(chat.id, "dh_ratchet", dh_ratchet)
        crypto.save_ratchet(chat.id, "user_ratchet", user_ratchet)
        crypto.save_ratchet(chat.id, "root_ratchet", root_ratchet)

        return Response(
            response=json.dumps({
                "status": "ok",
                "data": { "chat_id": chat.id },
                "msg": f"{chat.name} has been created for {user.telephone}"
            }),
            status=200,
            mimetype="application/json"
        )

    except IntegrityError as exc:
        print(exc)

        return DuplicateError

    except NoResultFound as exc:
        raise exc

        print("There was no chat with such ID")
        return NotFoundError

    except Exception as exc:
        raise exc


@mod_user.route("/receive-message/", methods=["POST"])
@authenticate_source()
def receive_message () -> wrappers.Response:
    try:
        data = json.loads(request.json)

        owner = User.query.filter_by(telephone=data["owner"]).one()
        user = User.query.filter_by(id=os.environ["USER_ID"], telephone=data["user"]).one()

        chat_id = data["chat_id"]
        cipher = crypto.encode_b64(data["cipher"])
        pbkey = crypto.load_public_key(data["dh_ratchet"])
        ratchets, _ = crypto.load_ratchets(chat_id)

        msg = crypto.rcv_msg(ratchets, pbkey, cipher)
        print(msg.decode("utf-8") )

        ratchets.pop("rcv_ratchet", None)

        ratchets["user_ratchet"] = data["dh_ratchet"]
        for ratchet_name, ratchet in ratchets.items():
            crypto.save_ratchet(chat_id, ratchet_name, ratchet)

        return Response(
            response=json.dumps({
                "status": "ok",
                "data": {
                    "dh_ratchet": crypto.public_key(ratchets["dh_ratchet"])
                },
                "msg": "Message delivered"
            }, cls=ComplexEncoder),
            status=200,
            mimetype="application/json"
        )

    except Exception as exc:
        raise exc