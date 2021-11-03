import os

# Import flask dependencies
from flask import Blueprint, json, Response, request, wrappers
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

# Import Util Modules
from app.util.json_encoder import ComplexEncoder
from app.util.authentication import authenticate_source, authenticate_user
from app.util.responses import DuplicateError, NotFoundError, ServerError

# Import module models (i.e. User)
from app.models.user import User
from app.models.device import Device
from app.models.public_keys import OPKey

# Import application Database
from app import db

# Define the blueprint: "auth", set its url prefix: app.url/auth
mod_auth = Blueprint("auth", __name__, url_prefix="/auth")

@mod_auth.route("/ping/", methods=["PUT"])
@authenticate_source()
@authenticate_user()
def ping () -> wrappers.Response:
    return Response(
        response=json.dumps({
            "status": "ok",
            "msg": "Session authenticated"
        }, cls=ComplexEncoder),
        status=200,
        mimetype="application/json"
    )

@mod_auth.route("/signup/", methods=["POST"])
@authenticate_source()
def signup () -> wrappers.Response:
    try:
        data = json.loads(request.json)

        user = User(
            name=data["name"],
            id_key=data["id_key"],
            sgn_key=data["sgn_key"],
            ed_key=data["ed_key"],
            devices=[ Device(address=data["address"]) ],
            opkeys=[
                OPKey(key_id=opkey["id"], opkey=opkey["key"])
                for opkey in data["opkeys"]
            ],
            telephone=data.get("telephone"),
            email=data.get("email", None),
            description=data.get("description", None)
        )

        db.session.add(user)
        db.session.add_all(user.devices)
        db.session.add_all(user.opkeys)
        db.session.commit()

        return Response(
            response=json.dumps({
                "status": "ok",
                "data": {
                    "user": {
                        "id": user.id,
                        "telephone": user.telephone
                    }
                },
                "msg": "User created"
            }, cls=ComplexEncoder),
            status=200,
            mimetype="application/json"
        )

    except IntegrityError as exc:
        return DuplicateError

