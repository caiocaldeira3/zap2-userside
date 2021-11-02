import os
import json
import dotenv
import requests

from pathlib import Path

base_path = Path(__file__).resolve().parent.parent.parent
dotenv.load_dotenv(base_path / ".env", override=False)

from app.util.json_encoder import ComplexEncoder

from app import db
from app.models.user import User
from app.models.public_keys import OTKey

headers_server = {
    "Param-Auth": os.environ["SECRET_KEY"]
}

def create_chat (owner: User, user: User, otkeys: list[OTKey], data: dict) -> None:
    for device in user.devices:
        response = requests.post(
            url=f"{device.address}/user/create-chat/",
            headers=headers_server,
            json=json.dumps({
                "owner": {
                    "name": owner.name,
                    "telephone": owner.telephone,
                    "description": owner.description
                },
                "used_keys": [ otkeys[0].key_id, otkeys[1].key_id ],
                "users": user,
                "name": data.pop("name"),
                "keys": {
                    "pb_keys": {
                        "IK": owner.id_key,
                        "EK": data.pop("EK")
                    }
                }
                **data
            }, cls=ComplexEncoder)
        )

        json_response = response.json()
        if json_response["status"] == "ok":
            print(json_response["data"])