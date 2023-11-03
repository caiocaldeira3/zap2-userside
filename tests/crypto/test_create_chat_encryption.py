from unittest.mock import patch

from app.util.crypto import create_chat_encryption

from . import Alice, Bob


def test_create_chat_encryption_calls_sender_x3dh_for_sender () -> None:
    alice = Alice()
    bob = Bob()

    with (
        patch("app.util.crypto.sender_x3dh") as send_method,
        patch("app.util.crypto.receiver_x3dh") as rcv_method
    ):
        create_chat_encryption(
            alice.private_keys(), bob.public_keys(), True
        )

        send_method.assert_called_once()
        rcv_method.assert_not_called()

def test_create_chat_encryption_calls_receiver_x3dh_for_receiver () -> None:
    alice = Alice()
    bob = Bob()

    with (
        patch("app.util.crypto.sender_x3dh") as send_method,
        patch("app.util.crypto.receiver_x3dh") as rcv_method
    ):
        create_chat_encryption(
            bob.private_keys(), alice.public_keys(), False
        )

        send_method.assert_not_called()
        rcv_method.assert_called_once()

def test_root_ratchet_after_next_equal_for_alice_and_bob () -> None:
    alice = Alice()
    bob = Bob()

    ratchet_alice = create_chat_encryption(
        alice.private_keys(), bob.public_keys(), True
    )
    ratchet_bob = create_chat_encryption(
        bob.private_keys(), alice.public_keys(), False
    )

    assert ratchet_alice.next() == ratchet_bob.next()

def test_root_ratchet_after_next_state_equal_for_alice_and_bob () -> None:
    alice = Alice()
    bob = Bob()

    ratchet_alice = create_chat_encryption(
        alice.private_keys(), bob.public_keys(), True
    )
    ratchet_bob = create_chat_encryption(
        bob.private_keys(), alice.public_keys(), False
    )

    ratchet_alice.next()
    ratchet_bob.next()

    assert ratchet_alice.state == ratchet_bob.state