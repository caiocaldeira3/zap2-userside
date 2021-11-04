# Import flask dependencies
from flask import Blueprint, json, Response, request, wrappers
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.exc import IntegrityError

# Import Util Modules
from app.util import api
from app.util.authentication import authenticate_source, authenticate_user
from app.util.json_encoder import AlchemyEncoder, ComplexEncoder
from app.util.responses import (
    DuplicateError, NotFoundError, ServerError
)

# Import module models (i.e. Organization)
from app.models.public_keys import OPKey
from app.models.user import User

# Import application Database
from app import db

# Define the blueprint: "org", set its url prefix: app.url/org
mod_user = Blueprint("user", __name__, url_prefix="/user")

# Set the route and accepted methods
@mod_user.route("/user-info/<int:user_id>/",  methods=["GET"])
def user_info_id (user_id: int) -> wrappers.Response:
    try:
        query = User.query.filter_by(id=user_id).one()

        return Response(
            response=json.dumps(query, cls=AlchemyEncoder),
            status=200,
            mimetype="application/json"
        )

    except MultipleResultsFound:
        print("There was more than one user with such ID")
        return ServerError

    except NoResultFound:
        print("There was no user with such ID")
        return NotFoundError

    except Exception:
        return ServerError

# Set the route and accepted methods
@mod_user.route("/user-info/",  methods=["PUT"])
def user_info () -> wrappers.Response:
    try:
        data = request.json
        data = { key: data[key] for key in data.keys() if key == "telephone" or key == "email" }

        query = User.query.filter_by(
            **data
        ).one()

        return Response(
            response=json.dumps(query, cls=AlchemyEncoder),
            status=200,
            mimetype="application/json"
        )

    except MultipleResultsFound:
        print("There was more than one user with such data")
        return ServerError

    except NoResultFound:
        print("There was no user with such data")
        return NotFoundError

    except Exception as exc:
        print(exc)
        return ServerError

@mod_user.route("/update-user/<int:user_id>/", methods=["PUT"])
def update_user (user_id: int) -> wrappers.Response:
    try:
        data = request.json
        data.pop("password", None)

        stmt = db.update(User).where(User.id == user_id).values(**data)

        with db.engine.connect() as connection:
            result = connection.execute(stmt)
            query = User.query.filter_by(id=user_id).one()

            return Response(
                response=json.dumps(query, cls=AlchemyEncoder),
                status=200,
                mimetype="application/json"
            )

    except MultipleResultsFound:
        return ServerError

    except NoResultFound:
	    return NotFoundError

    except Exception as exc:
        print(exc)

        return ServerError

@mod_user.route("/user-info/<int:user_id>/chat-list/", methods=["GET"])
def chat_list (user_id: int) -> wrappers.Response:
    try:
        query = User.query.filter_by(id=user_id).one().chats

        return Response(
            response=json.dumps(query, cls=AlchemyEncoder),
            status=200,
            mimetype="application/json"
        )

    except NoResultFound:
        print("There was no user with such ID")

        return NotFoundError

    except Exception as exc:
        print(exc)

        return ServerError

@mod_user.route("/create-chat/", methods=["POST"])
@authenticate_source()
@authenticate_user()
def create_chat () -> wrappers.Response:
    try:
        data = json.loads(request.json)
        owner = User.query.filter_by(telephone=data["telephone"]).one()
        users = User.query.filter(User.telephone.in_(data["users"])).all()

        if len(users) == 0:
            raise Exception

        data.pop("telephone", None)
        data.pop("users", None)

        return_data = []
        for user in users:
            opkeys = user.opkeys[ : 2 ]
            chat_data = api.create_chat(owner, user, opkeys, data)
            if chat_data is None:
                raise Exception

            return_data.append({
                "name": user.name,
                "telephone": user.telephone,
                "keys": {
                    "dh_ratchet": opkeys[0].opkey,
                    "OPK": opkeys[1].opkey,
                    "IK": user.id_key,
                    "SPK": user.sgn_key
                },
                **chat_data,
            })

        return Response(
            response=json.dumps({
                "status": "ok",
                "data": return_data,
                "msg": "Create chat message delivered."
            }, cls=ComplexEncoder),
            status=200,
            mimetype="application/json"
        )

    except Exception as exc:
        raise exc
        return ServerError

    except IntegrityError as exc:
        print(exc)
        raise exc

        return DuplicateError

    except NoResultFound as exc:
        print(exc)

        print("There was no chat with such ID")
        return NotFoundError

@mod_user.route("/send-message/", methods=["POST"])
@authenticate_source()
@authenticate_user()
def send_message () -> wrappers.Response:
    try:
        data = json.loads(request.json)
        users = User.query.filter(User.telephone.in_(data["users"])).all()

        if len(users) == 0:
            raise Exception

        data["owner"] = data.pop("telephone", None)
        data.pop("users", None)

        dh_ratchets = []
        for user in users:
            dh_ratchets.append(api.send_message(user, data))

        return Response(
            response=json.dumps({
                "status": "ok",
                "data": { "dh_ratchets": dh_ratchets},
                "msg": "Chat message delivered."
            }, cls=ComplexEncoder),
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