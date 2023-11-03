import pytest

from app.util.crypto import create_chat_encryption, rcv_msg, snd_msg

from . import Alice, Bob, Eve


@pytest.fixture
def create_chat () -> tuple[Alice, Bob]:
    alice = Alice()
    bob = Bob()

    alice.ratchet.root_ratchet = create_chat_encryption(
        alice.private_keys(), bob.public_keys(), True
    )
    bob.ratchet.root_ratchet = create_chat_encryption(
        bob.private_keys(), alice.public_keys(), False
    )

    yield alice, bob

@pytest.mark.parametrize(
    "msg", [
        b"teste", b"msg espacos", b"dezesseis caract", b"ms@ $imb0los"
    ]
)
def test_send_message_ciphers_initial_message (
     msg: bytes, create_chat: pytest.fixture
) -> None:
    alice, bob = create_chat
    alice: Alice
    bob: Bob

    ciphered_msg, _ = snd_msg(
        alice.ratchets(), bob.ratchet.dh_ratchet.public_key(), msg
    )

    assert ciphered_msg != msg

@pytest.mark.parametrize(
    "msg1", [
        b"teste", b"msg espacos", b"dezesseis caract", b"ms@ $imb0los"
    ]
)
@pytest.mark.parametrize(
    "msg2", [
        b"teste", b"msg espacos", b"dezesseis caract", b"ms@ $imb0los"
    ]
)
def test_send_message_next_ratchet_independent_of_messages (
    msg1: str, msg2: str, create_chat: pytest.fixture
) -> None:
    alice, bob = create_chat
    alice: Alice
    bob: Bob

    _, snd_ratchet_pbkey1 = snd_msg(
        alice.ratchets(), bob.ratchet.dh_ratchet.public_key(), msg1
    )

    _, snd_ratchet_pbkey2 = snd_msg(
        alice.ratchets(), bob.ratchet.dh_ratchet.public_key(), msg2
    )

    assert snd_ratchet_pbkey1 != snd_ratchet_pbkey2

@pytest.mark.parametrize(
    "expected", [
        b"teste", b"msg espacos", b"dezesseis caract", b"ms@ $imb0los"
    ]
)
def test_bob_can_decode_alice_message (
     expected: bytes, create_chat: pytest.fixture
) -> None:
    alice, bob = create_chat
    alice: Alice
    bob: Bob

    ciphered_msg, alice_pb_ratchet = snd_msg(
        alice.ratchets(), bob.ratchet.dh_ratchet.public_key(), expected
    )

    msg = rcv_msg(bob.ratchets(), alice_pb_ratchet, ciphered_msg)

    assert msg == expected

@pytest.mark.parametrize(
    "expected", [
        b"teste", b"msg espacos", b"dezesseis caract", b"ms@ $imb0los"
    ]
)
def test_eve_cant_eavesdrop (
    expected: bytes, create_chat: pytest.fixture
) -> None:
    alice, bob = create_chat
    alice: Alice
    bob: Bob
    eve = Eve()

    eve.ratchet.root_ratchet = create_chat_encryption(
        eve.private_keys(), alice.public_keys(), False
    )

    ciphered_msg, alice_pb_ratchet = snd_msg(
        alice.ratchets(), bob.ratchet.dh_ratchet.public_key(), expected
    )

    msg = rcv_msg(eve.ratchets(), alice_pb_ratchet, ciphered_msg)

    assert msg != expected

@pytest.mark.parametrize(
    "expected", [
        b"teste", b"msg espacos", b"dezesseis caract", b"ms@ $imb0los"
    ]
)
def test_eve_cant_fake_alice (
    expected: bytes, create_chat: pytest.fixture
) -> None:
    _, bob = create_chat
    bob: Bob
    eve = Eve()

    eve.ratchet.root_ratchet = create_chat_encryption(
        eve.private_keys(), bob.public_keys(), True
    )

    ciphered_msg, eve_pb_ratchet = snd_msg(
        eve.ratchets(), bob.ratchet.dh_ratchet.public_key(), expected
    )

    msg = rcv_msg(bob.ratchets(), eve_pb_ratchet, ciphered_msg)

    assert msg != expected