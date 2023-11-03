import pytest
from cryptography.exceptions import InvalidSignature

from app.util.crypto import encode_b64, sign_message

from . import Alice, Eve


@pytest.mark.parametrize(
    "expected", [
        b"teste", b"expected espacos", b"dezesseis caract", b"ms@ $imb0los",
        b"It's me Mario"
    ]
)
def test_signed_message_can_be_verified_with_public_key (expected: str) -> None:
    alice = Alice()

    signed_message = sign_message(alice.SGN_KEY, expected)
    alice.SGN_KEY.public_key().verify(
        signature=encode_b64(signed_message), data=expected
    )

@pytest.mark.parametrize(
    "expected", [
        b"teste", b"expected espacos", b"dezesseis caract", b"ms@ $imb0los",
        b"It's me Mario"
    ]
)
def test_eve_cant_fake_alice_signature (expected: str) -> None:
    alice = Alice()
    eve = Eve()

    with pytest.raises(InvalidSignature):
        signed_message = sign_message(eve.SGN_KEY, expected)
        alice.SGN_KEY.public_key().verify(
            signature=encode_b64(signed_message), data=expected
        )