import os

from typing import Callable
from functools import wraps
from flask import json, request, Response, wrappers

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
            if request.headers["Param-Auth"] == os.environ["SECRET_KEY"]:
                return f(*args, **kwargs)

            else:
                return unauthorized_request()

        return decorated

    return wrapper