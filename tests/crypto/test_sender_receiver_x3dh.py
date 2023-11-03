import pytest

from app.util.crypto import receiver_x3dh, sender_x3dh

from . import Alice, Bob


def test_senderx3dh_success () -> None:
    alice = Alice()
    bob = Bob()

    assert sender_x3dh(alice.private_keys(), bob.public_keys())

def test_senderx3dh_require_sender_private_keys () -> None:
    alice = Alice()
    bob = Bob()

    with pytest.raises(AttributeError):
        sender_x3dh(alice.public_keys(), bob.public_keys())

def test_senderx3dh_require_receiver_public_keys () -> None:
    alice = Alice()
    bob = Bob()

    with pytest.raises(TypeError):
        sender_x3dh(alice.private_keys(), bob.private_keys())

def test_senderx3dh_order_is_important () -> None:
    alice = Alice()
    bob = Bob()

    with pytest.raises(KeyError):
        sender_x3dh(bob.private_keys(), alice.public_keys())

def test_receiverx3dh_success () -> None:
    alice = Alice()
    bob = Bob()

    assert receiver_x3dh(alice.public_keys(), bob.private_keys())

def test_receiverx3dh_require_receiver_private_keys () -> None:
    alice = Alice()
    bob = Bob()

    with pytest.raises(AttributeError):
        receiver_x3dh(alice.public_keys(), bob.public_keys())

def test_receiverx3dh_require_sender_public_keys () -> None:
    alice = Alice()
    bob = Bob()

    with pytest.raises(TypeError):
        receiver_x3dh(alice.private_keys(), bob.private_keys())

def test_receiverx3dh_order_is_important () -> None:
    alice = Alice()
    bob = Bob()

    with pytest.raises(KeyError):
        receiver_x3dh(bob.public_keys(), alice.private_keys())

def test_senderx3dh_equals_to_receiverx3dh () -> None:
    alice = Alice()
    bob = Bob()

    sender = sender_x3dh(alice.private_keys(), bob.public_keys())
    receiver = receiver_x3dh(alice.public_keys(), bob.private_keys())

    assert sender == receiver