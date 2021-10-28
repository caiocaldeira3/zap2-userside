# Import flask dependencies
from flask import Blueprint, json, Response, request, wrappers
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

# Import Util Modules
from app.util.json_encoder import AlchemyEncoder
from app.util.responses import (
    NotFoundError, ServerError
)

# Import module models (i.e. Chat)
from app.models.chat import Chat
from app.models.user import User

# Import application Database
from app import db

# Define the blueprint: "chat", set its url prefix: app.url/org
mod_chat = Blueprint("chat", __name__, url_prefix="/chat")

@mod_chat.route("/",  methods=["GET"])
def list_chats () -> wrappers.Response:
    try:
        query = Chat.query.all()

        return Response(
            response=json.dumps(query, cls=AlchemyEncoder),
            status=200,
            mimetype="application/json"
        )

    except Exception as exc:
        print(exc)
        return ServerError

# Set the route and accepted methods
@mod_chat.route("/chat-info/<int:chat_id>/",  methods=["GET"])
def chat_info (chat_id: int) -> wrappers.Response:
    try:
        query = Chat.query.filter_by(chat_id=chat_id).one()

        return Response(
            response=json.dumps(query, cls=AlchemyEncoder),
            status=200,
            mimetype="application/json"
        )

    except MultipleResultsFound:
        print("There was more than one chat with such ID")
        return ServerError

    except NoResultFound:
        print("There was no chat with such ID")
        return NotFoundError

    except Exception:
        return ServerError

@mod_chat.route("/chat-info/<int:chat_id>/user-list/", methods=["GET"])
def user_list (chat_id: int) -> wrappers.Response:
    try:
        chat = Chat.query.filter_by(chat_id=chat_id).one()
        query = chat.users.all()

        return Response(
            response=json.dumps(query, cls=AlchemyEncoder),
            status=200,
            mimetype="application/json"
        )

    except NoResultFound:
        print("There was no chat with such ID")
        return NotFoundError

    except Exception as exc:
        return ServerError

@mod_chat.route("/<int:chat_id>/add-user/<int:user_id>/", methods=["PUT"])
def add_user (chat_id: int, user_id: int) -> wrappers.Response:
    try:
        chat = Chat.query.filter_by(chat_id=chat_id).one()
        user = User.query.filter_by(user_id=user_id).one()

        chat.users.append(user)
        db.session.add(chat)
        db.session.commit()

        chat = Chat.query.filter_by(chat_id=chat_id).one()
        query = chat.users.all()

        return Response(
            response=json.dumps(query, cls=AlchemyEncoder),
            status=200,
            mimetype="application/json"
        )

    except NoResultFound:
        print("There was no chat with such ID")
        return NotFoundError

    except Exception as exc:
        print(exc)

        return ServerError