import os
import json
import dotenv
import requests
import dataclasses as dc

from pathlib import Path
from werkzeug.security import generate_password_hash
from cryptography.hazmat.backends.openssl.x25519 import _X25519PrivateKey

base_path = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(base_path / ".env", override=False)

from app import db
from app.models.user import User
from app.util.json_encoder import ComplexEncoder
from app.util.crypto import generate_private_key, load_private_key, clean_keys, public_key

@dc.dataclass()
class Api:

    base_url: str = dc.field(init=False, default="http://192.168.1.34:8080")
    headers_client: dict = dc.field(init=False, default_factory=lambda: {
        "Param-Auth": os.environ["CHAT_SECRET"]
    })
    headers_user: dict = dc.field(init=False, default=None)

    user_id: int = dc.field(init=False, default=None)
    id_key: _X25519PrivateKey = dc.field(init=False, default=None)
    sgn_key: _X25519PrivateKey = dc.field(init=False, default=None)

    def signup (
        self, name: str, email: str, telephone: str, password: str, description: str = None
    ) -> None:
        self.id_key = generate_private_key("id_key")
        self.sgn_key = generate_private_key("sgn_key")

        id_key = public_key(self.id_key)
        sgn_key = public_key(self.sgn_key)
        otkeys = [
            { "id": idx, "key": public_key(generate_private_key(f"{idx}_otk")) }
            for idx in range(1, 51)
        ]

        try:
            response = requests.post(
                url=f"{self.base_url}/auth/signup/",
                headers=self.headers_client,
                json=json.dumps({
                    key: value
                    for key, value in vars().items()
                    if key not in [ "self", "password" ] and value is not None
                }, cls=ComplexEncoder)
            )
            resp_json = response.json()

            if resp_json["status"] == "ok":
                user = User(
                    email=email,
                    name=name,
                    telephone=telephone,
                    server_id=resp_json["user"]["id"],
                    password=generate_password_hash(password),
                    description=description
                )
                db.session.add(user)
                db.session.commit()

                self.user_id = user.id
                self.headers_user = {
                    "signed-message": id_key.sign(b"that's me wario")
                } | self.headers_client

        except Exception as exc:
            clean_keys()
            raise exc

    def create_chatroom (
        self, name: str, users: list[str], description: str = None
    ) -> None:
        try:
            owner = User.query.filter_by(id=self.user_id).one()
            response = requests.post(
                url=f"{self.base_url}/user/create-chat/",
                headers=self.headers_user,
                json=json.dumps({
                    "name": name,
                    "owner": owner.telephone,
                    "users": users
                })
            )
            resp_json = response.json()

        except:
            pass