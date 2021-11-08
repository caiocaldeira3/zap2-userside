# Import flask dependencies
from flask import Blueprint, json, Response, request, wrappers
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

# Import Util Modules
# from app.util.json_encoder import AlchemyEncoder
# from app.util.responses import AuthorizationError, DuplicateError, NotFoundError, ServerError

# Import module models (i.e. User)
# from app.models.user import User

# Import application Database
from app import db

# Define the blueprint: "auth", set its url prefix: app.url/auth
mod_auth = Blueprint("auth", __name__, url_prefix="/auth")