import os
import sys
import json
import dotenv
import requests
import fileinput
import regex as re
import dataclasses as dc

from pathlib import Path
from werkzeug.security import generate_password_hash
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

base_path = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(base_path / ".env", override=False)

from app.models.user import User
from app.models.chat import Chat

from app import db
from app.util.json_encoder import ComplexEncoder
from app.util.crypto import create_chat_encryption, decode_b64, generate_private_key, load_private_key, clean_keys, public_key, save_ratchet, sign_message

@dc.dataclass()
class Api:

    base_url: str = dc.field(init=False, default="http://192.168.1.34:8080")
    headers_client: dict = dc.field(init=False, default=None)
    headers_user: dict = dc.field(init=False, default=None)
    device_url: str = dc.field(
        init=False,
        default=f"http://192.168.1.32:{sys.argv[1] if len(sys.argv) >= 2 else 3030}"
    )

    user_id: int = dc.field(init=False, default=None)
    id_key: X25519PrivateKey = dc.field(init=False, default=None)
    sgn_key: X25519PrivateKey = dc.field(init=False, default=None)
    ed_key: Ed25519PrivateKey = dc.field(init=False, default=None)

    def __init__ (self, logged_in: str) -> None:
        if logged_in == "logged_in" and os.environ["USER_ID"] != -1:
            self.user_id = os.environ["USER_ID"]
            self.id_key = load_private_key("id_key")
            self.sgn_key = load_private_key("sgn_key")
            self.ed_key = load_private_key("ed_key")

        elif logged_in == "logged_in":
            print("Api has not any session stored")
            raise Exception

        self.headers_client = {
            "Param-Auth": os.environ["CHAT_SECRET"]
        }

    def _update_enviroment (self, key: str, value: str) -> None:
        environ_regex = re.compile(f"(?<={key}=).*")

        with fileinput.FileInput(".env", inplace=True, backup=".bak") as env:
            for line in env:
                print(environ_regex.sub(f"{value}", line), end="")

    def update_header_user (self) -> None:
        self.headers_user = {
            "signed-message": sign_message(self.ed_key)
        } | self.headers_client

    def signup (
        self, name: str, telephone: str, password: str,
        description: str = None, email: str = None
    ) -> None:
        self.id_key = generate_private_key("id_key")
        self.sgn_key = generate_private_key("sgn_key")
        self.ed_key = generate_private_key("ed_key", sgn_key=True)

        address = self.device_url
        id_key = public_key(self.id_key)
        sgn_key = public_key(self.sgn_key)
        ed_key = public_key(self.ed_key)
        opkeys = [
            { "id": idx, "key": public_key(generate_private_key(f"{idx}_opk")) }
            for idx in range(1, 11)
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
                    name=name,
                    telephone=telephone,
                    password=generate_password_hash(password),
                    email=email,
                    description=description
                )
                db.session.add(user)
                db.session.commit()

                self.user_id = user.id
                self.update_header_user()
                self._update_enviroment("USER_ID", self.user_id)

                return resp_json["data"]

        except Exception as exc:
            clean_keys()
            raise exc

    def create_chat (
        self, name: str, users: list[str], description: str = None
    ) -> None:
        try:
            owner = User.query.filter_by(id=self.user_id).one()
            eph_key = generate_private_key()

            response = requests.post(
                url=f"{self.base_url}/user/create-chat/",
                headers=self.headers_user,
                json=json.dumps({
                    "name": name,
                    "owner": owner.telephone,
                    "users": users,
                    "EK": public_key(eph_key)
                })
            )

            resp_json = response.json()
            if resp_json["status"] == "ok":
                data = resp_json["data"][0]

                user = User.query.filter_by(telephone=data["telephone"]).first()
                if user is None:
                    user = User(name=data["name"], telephone=data["telephone"])

                    db.session.add(owner)
                    db.session.commit()

                chat = Chat(
                    name = data["name"],
                    users = [ owner, user ],
                    description = data.get("description", None)
                )
                db.session.add(chat)
                db.session.commit()

                user_ratchet = data["keys"].pop("dh_ratchet")
                user_keys = data["keys"]
                root_ratchet = create_chat_encryption(
                    { "IK": self.id_key, "EK": eph_key }, pb_keys=user_keys, sender=True
                )

                save_ratchet(chat.id, "root_ratchet", root_ratchet)
                save_ratchet(chat.id, "user_ratchet", user_ratchet)

                return chat.id

        except Exception as exc:
            raise exc