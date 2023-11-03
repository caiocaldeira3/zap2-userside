import dataclasses as dc

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from app.util.crypto import PrivateKey, PublicKey, SymmetricRatchet


class Keyzeds:
    def private_keys (self) -> dict[str, PrivateKey]:
        return {
            field.name: self.__getattribute__(field.name)
            for field in dc.fields(self)
            if isinstance(self.__getattribute__(field.name), X25519PrivateKey)
        }

    def public_keys (self) -> dict[str, PublicKey]:
        return {
            field.name: self.__getattribute__(field.name).public_key()
            for field in dc.fields(self)
            if isinstance(self.__getattribute__(field.name), X25519PrivateKey)
        }

@dc.dataclass()
class Alice (Keyzeds):
    IK: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)
    EK: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)
    dh_ratchet: X25519PrivateKey = dc.field(default=None)

@dc.dataclass()
class Bob (Keyzeds):
    IK: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)
    SPK: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)
    OPK: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)

    dh_ratchet: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)

@dc.dataclass()
class Eve (Keyzeds):
    IK: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)
    EK: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)
    SPK: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)
    OPK: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)

    dh_ratchet: X25519PrivateKey = dc.field(default_factory=X25519PrivateKey.generate)
