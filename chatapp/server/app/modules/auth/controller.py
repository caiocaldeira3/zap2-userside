# Import flask dependencies
from flask import Blueprint, json, Response, request, wrappers
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

# Import Util Modules
from app.util.json_encoder import ComplexEncoder
from app.util.responses import AuthorizationError, DuplicateError, NotFoundError, ServerError

# Import module models (i.e. User)
from app.models.user import User
from app.models.device import Device
from app.models.public_keys import OTKey

# Import application Database
from app import db

# Define the blueprint: "auth", set its url prefix: app.url/auth
mod_auth = Blueprint("auth", __name__, url_prefix="/auth")

@mod_auth.route("/signup/", methods=["POST"])
def signup () -> wrappers.Response:
    try:
        data = json.loads(request.json)

        user = User(
            email=data["email"],
            name=data["name"],
            id_key=data["id_key"],
            sgn_key=data["sgn_key"],
            ed_key=data["ed_key"],
            devices=[ Device(address=data["address"]) ],
            otkeys=[
                OTKey(key_id=otkey["id"], otkey=otkey["key"])
                for otkey in data["otkeys"]
            ],
            telephone=data.get("telephone"),
            description=data.get("description", None)
        )

        db.session.add(user)
        db.session.add_all(user.devices)
        db.session.add_all(user.otkeys)
        db.session.commit()

        return Response(
            response=json.dumps({
                "status": "ok",
                "msg": {
                    "user": {
                        "id": user.id,
                        "email": user.email
                    }
                }
            }, cls=ComplexEncoder),
            status=200,
            mimetype="application/json"
        )

    except IntegrityError as exc:
        print(exc)

        return DuplicateError

