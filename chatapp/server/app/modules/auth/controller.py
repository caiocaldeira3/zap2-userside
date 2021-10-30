# Import flask dependencies
from flask import Blueprint, json, Response, request, wrappers
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

# Import Util Modules
from app.util.json_encoder import AlchemyEncoder
from app.util.responses import AuthorizationError, DuplicateError, NotFoundError, ServerError

# Import password / encryption helper tools
from werkzeug.security import check_password_hash, generate_password_hash

# Import module models (i.e. User)
from app.models.user import User

# Import application Database
from app import db

# Define the blueprint: "auth", set its url prefix: app.url/auth
mod_auth = Blueprint("auth", __name__, url_prefix="/auth")

# Set the route and accepted methods
@mod_auth.route("/signin/", methods=["PUT"])
def signin () -> wrappers.Response:
    try:
        data = request.json
        user = User.query.filter_by(email=data["email"]).one()

        if user and check_password_hash(user.password, data["password"]):
            return Response(
                response=json.dumps({
                    "user": user.user_id,
                    "name": user.name
                }),
                status=200,
                mimetype="application/json"
            )

        else:
            return AuthorizationError

    except MultipleResultsFound:
        return ServerError

    except NoResultFound:
	    return NotFoundError

    except Exception as exc:
        print(exc)

        return AuthorizationError

@mod_auth.route("/signup/", methods=["POST"])
def signup () -> wrappers.Response:
    try:
        data = request.json

        stmt = db.insert(User).values(
            email=data["email"],
            name=data["name"],
            password=generate_password_hash(data["password"]),
            telephone=data.get("telephone"),
            description=data.get("description", None)
        )

        with db.engine.connect() as connection:
            result = connection.execute(stmt)
            query = User.query.filter_by(user_id=result.lastrowid).one()

            return Response(
                response=json.dumps(query, cls=AlchemyEncoder),
                status=200,
                mimetype="application/json"
            )

    except IntegrityError as exc:
        print(exc)

        return DuplicateError

    except Exception as exc:
        print(exc)

        return ServerError

