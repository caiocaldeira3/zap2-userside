import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from app.models.user import User

def decode_b64 (msg: bytes) -> str:
    return base64.encodebytes(msg).decode("utf-8").strip()

def encode_b64 (msg: str) -> bytes:
    return base64.b64decode(msg)

def verify_signed_message (telephone: str, msg: str) -> bool:
    try:
        user = User.query.filter_by(telephone=telephone).one()
        ed_pbkey = Ed25519PublicKey.from_public_bytes(
            encode_b64(user.ed_key)
        )
        ed_pbkey.verify(signature=encode_b64(msg), data=b"It's me, Mario")

        return True

    except:
        return False