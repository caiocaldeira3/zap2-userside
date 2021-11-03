import os

from typing import Callable
from functools import wraps
from flask import json, request, Response, wrappers

from app.util.crypto import verify_signed_message

def unauthorized_request () -> wrappers.Response:
    return Response(
        response=json.dumps({
            "status": "failed",
            "msg": "It wasn't possible to authenticate the session"
        }),
        status=403,
        mimetype="application/json"
    )

def authenticate_source () -> wrappers.Response:
    def wrapper (f: Callable) -> wrappers.Response:
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.headers["Param-Auth"] == os.environ["CHAT_SECRET"]:
                return f(*args, **kwargs)

            else:
                return unauthorized_request()

        return decorated

    return wrapper

def authenticate_user () -> wrappers.Response:
    def wrapper (f: Callable) -> wrappers.Response:
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                telephone = json.loads(request.json)["telephone"]
                sgn_message = request.headers["Signed-Message"]

                if verify_signed_message(telephone, sgn_message):
                    return f(*args, **kwargs)

                else:
                    return unauthorized_request()

            except Exception as exc:
                return unauthorized_request()

        return decorated

    return wrapper