# Import flask dependencies
from flask import Blueprint, json, Response, request, wrappers
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.exc import IntegrityError

# Import Util Modules
from app.util.crypto import create_chat_encryption, load_private_key, save_ratchet
from app.util.json_encoder import AlchemyEncoder
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
def create_chat () -> wrappers.Response:
    from app import api

    try:

        data = json.loads(request.json)

        owner = User.query.filter_by(telephone=data["owner"]["telephone"]).first()
        user = User.query.filter_by(id=api.user_id).one()
        if owner is None:
            owner = User(**data["owner"])

            db.session.add(owner)
            db.session.commit()

        chat = Chat(
            name = data["name"],
            users = [ owner, user ],
            description = data.get("description", None)
        )
        db.session.add(chat)
        db.session.commit()

        pvt_keys = {
            "IK": load_private_key("id_key"),
            "SPK": load_private_key("sgn_key"),
            "OTK": load_private_key(data["used_keys"][1])
        }
        dh_ratchet = load_private_key(data["used_keys"][0])
        root_ratchet = create_chat_encryption(pvt_keys, data["keys"]["pb_keys"], sender=False)

        save_ratchet(chat.id, "dh_ratchet", dh_ratchet)
        save_ratchet(chat.id, "root_ratchet", root_ratchet)

        return Response(
            response=json.dumps({
                "status": "ok",
                "msg": "The receiving chat has been created"
            }),
            status=200,
            mimetype="application/json"
        )

    except IntegrityError as exc:
        print(exc)

        return DuplicateError

    except NoResultFound as exc:
        print(exc)

        print("There was no chat with such ID")
        return NotFoundError

    except Exception as exc:
        raise exc
        return ServerError
