import base64

from typing import Union
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.backends.openssl.x25519 import _X25519PrivateKey, _X25519PublicKey
from cryptography.hazmat.backends import default_backend

from Crypto.Cipher import AES

class SymmetricRatchet(object):
    def __init__ (self, key: bytes):
        self.state = key

    def next (self, inp: bytes = b"", init_vector: bytes = b"") -> bytes:
        output = hkdf_derive_key(self.state + inp, 80)
        self.state = output[ : 32 ]

        # key, initializing vector
        return output[ 32 : 64 ], output[ 64: ]

def decode_b64 (msg: bytes) -> str:
    return base64.encodebytes(msg).decode("utf-8").strip()

def pad (msg: bytes) -> bytes:
    # pkcs7 padding
    num = 16 - (len(msg) % 16)
    return msg + bytes([num] * num)

def unpad (msg: bytes) -> bytes:
    # remove pkcs7 padding
    return msg[ : -msg[-1] ]

def hkdf_derive_key (input: bytes, length: int) -> bytes:
    hkdf_key = HKDF(
        algorithm=hashes.SHA256(), length=length, salt=b"", info=b"", backend=default_backend()
    )

    return hkdf_key.derive(input)

def sender_x3dh (
    sender_keys: dict[str, _X25519PrivateKey], recv_keys: dict[str, _X25519PublicKey]
) -> bytes:
    dh1 = sender_keys["IK"].exchange(recv_keys["SPK"])
    dh2 = sender_keys["EK"].exchange(recv_keys["IK"])
    dh3 = sender_keys["EK"].exchange(recv_keys["SPK"])
    dh4 = sender_keys["EK"].exchange(recv_keys["OPK"])

    return hkdf_derive_key(dh1 + dh2 + dh3 + dh4, 32)

def receiver_x3dh (
    sender_keys: dict[str, _X25519PublicKey], recv_keys: dict[str, _X25519PrivateKey]
) -> bytes:
    dh1 = recv_keys["SPK"].exchange(sender_keys["IK"])
    dh2 = recv_keys["IK"].exchange(sender_keys["EK"])
    dh3 = recv_keys["SPK"].exchange(sender_keys["EK"])
    dh4 = recv_keys["OPK"].exchange(sender_keys["EK"])

    return hkdf_derive_key(dh1 + dh2 + dh3 + dh4, 32)

def init_root_ratchet (shared_key: bytes) -> SymmetricRatchet:
    return SymmetricRatchet(shared_key)

Ratchet = Union[SymmetricRatchet, X25519PrivateKey]

def dh_ratchet_rotation_receive (
    ratchets: dict[str, Ratchet], pbkey: bytes
) -> None:
    dh_recv = ratchets["dh_ratchet"].exchange(pbkey)
    shared_recv = ratchets["root_ratchet"].next(dh_recv)[0]

    ratchets["rcv_ratchet"] = SymmetricRatchet(shared_recv)

def dh_ratchet_rotation_send (
    ratchets: dict[str, Ratchet], pbkey: bytes
) -> None:
    ratchets["dh_ratchet"] = X25519PrivateKey.generate()
    dh_send = ratchets["dh_ratchet"].exchange(pbkey)
    shared_send = ratchets["root_ratchet"].next(dh_send)[0]

    ratchets["snd_ratchet"] = SymmetricRatchet(shared_send)

def snd_msg (
    ratchets: dict[str, Ratchet], pbkey: bytes, msg: bytes
) -> tuple[bytes, _X25519PublicKey]:
    dh_ratchet_rotation_send(ratchets, pbkey)
    key, init_vector = ratchets["snd_ratchet"].next()
    cipher = AES.new(key, AES.MODE_CBC, init_vector).encrypt(pad(msg))

    return cipher, ratchets["dh_ratchet"].public_key()

def rcv_msg (
    ratchets: dict[str, Ratchet], pbkey: _X25519PublicKey, cipher: bytes
) -> bytes:
    dh_ratchet_rotation_receive(ratchets, pbkey)
    key, init_vector = ratchets["rcv_ratchet"].next()

    return unpad(AES.new(key, AES.MODE_CBC, init_vector).decrypt(cipher))