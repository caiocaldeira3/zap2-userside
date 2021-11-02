from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from crypto import *

class keyzeds (object):
    def private_keys (self) -> dict[str, PrivateKeys]:
        return self.__dict__

    def public_keys (self) -> dict[str, PublicKeys]:
        return {
            attr: self.__getattribute__(attr).public_key()
            for attr in self.__dict__.keys()
            if isinstance(self.__getattribute__(attr), X25519PrivateKey)
        }

class Bob(keyzeds):
    def __init__(self):
        # generate Bob's keys
        self.IK = X25519PrivateKey.generate()
        self.SPK = X25519PrivateKey.generate()
        self.OPK = X25519PrivateKey.generate()

        self.dh_ratchet = X25519PrivateKey.generate()

class Alice(keyzeds):
    def __init__(self):
        # generate Alice's keys
        self.IK = X25519PrivateKey.generate()
        self.EK = X25519PrivateKey.generate()

        self.dh_ratchet = None

al = Alice()
bob = Bob()

sk = sender_x3dh(al.private_keys(), bob.public_keys())
sk_ = receiver_x3dh(al.public_keys(), bob.private_keys())

rta = init_root_ratchet(sk)
rtb = init_root_ratchet(sk_)

ratchets_alice = {
    "root_ratchet": rta
}
ratchets_bob = {
    "root_ratchet": rtb,
    "dh_ratchet": bob.dh_ratchet
}

print(
    "The order of operation is important.\nThe " +
    "first message sent must be from alice, or else " +
    "it wont be able to decrypt the messages."
)

while True:
    sender = input("who's sending? [alice, bob] (exit to leave)\n")
    if sender == "exit":
        break

    message = input("write the message (up to 16 characters)\n")
    if sender == "alice":
        ratchets_sender = ratchets_alice
        ratchets_receiver = ratchets_bob
    else:
        ratchets_sender = ratchets_bob
        ratchets_receiver = ratchets_alice

    cipher, snd_pbkey = snd_msg(
        ratchets_sender, ratchets_receiver["dh_ratchet"].public_key(), bytes(message, encoding="utf-8")
    )
    print(f"encrypted message: {decode_b64(cipher)}")

    msg = rcv_msg(ratchets_receiver, snd_pbkey, cipher)
    print(f"decrypted_message: {str(msg)}")

    if sender == "alice":
        ratchets_alice = ratchets_sender
        ratchets_bob = ratchets_receiver
    else:
        ratchets_alice = ratchets_receiver
        ratchets_bob = ratchets_sender