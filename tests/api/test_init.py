import base64
from unittest.mock import patch

import pytest
import socketio
from bson import ObjectId
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from socketio.exceptions import ConnectionError

from app.models.user import User
from app.util import config
from app.util.api import Api


def test_headers_client () -> None:
    api = Api()

    assert api.headers_client == { "Param-Auth": config.CHAT_SECRET }

def test_headers_user_equal_to_client_on_init () -> None:
    api = Api()

    assert api.headers_client == api.headers_user

def test_no_login_default_values () -> None:
    api = Api()

    assert api.user_id is None
    assert api.id_key is None
    assert api.sgn_key is None
    assert api.ed_key is None

def test_login_and_invalid_config_user_id () -> None:
    config.USER_ID = -1

    with pytest.raises(ValueError):
        Api(True)

def test_valid_login_update_headers () -> None:
    config.USER_ID = ObjectId()

    with (
        patch("app.util.crypto.load_private_key") as mock_load_pvt_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.find_with_id") as mock_find_user,
        patch.object(socketio.Client, "connect") as mock_connect
    ):
        mock_sign_message.return_value = True
        mock_find_user.return_value = User("test", "test", "test")

        api = Api(True)

        expected = {
            "Param-Auth": config.CHAT_SECRET,
            "Signed-Message": True
        }

        assert api.headers_user == expected

def test_valid_login_correct_method_calls () -> None:
    config.USER_ID = ObjectId()

    with (
        patch("app.util.crypto.load_private_key") as mock_load_pvt_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.find_with_id") as mock_find_user,
        patch.object(socketio.Client, "connect") as mock_connect
    ):
        mock_find_user.return_value = User("test", "test", "test")

        Api(True)

        mock_load_pvt_key.assert_called()
        mock_sign_message.assert_called_once()
        mock_find_user.assert_called_once()
        mock_connect.assert_called_once()

def test_login_raised_error_call_setdown_user () -> None:
    config.USER_ID = ObjectId()

    with (
        patch("app.util.crypto.load_private_key") as mock_load_pvt_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.find_with_id") as mock_find_user,
        patch.object(socketio.Client, "connect") as mock_connect,
        patch.object(Api, "_setdown_user") as mock_setdown,
        patch.object(socketio.Client, "disconnect") as mock_disconnect
    ):
        mock_find_user.side_effect=Exception

        Api(True)

        mock_load_pvt_key.assert_called()
        mock_sign_message.assert_called_once()
        mock_find_user.assert_called_once()
        mock_connect.assert_not_called()
        mock_setdown.assert_called_once()
        mock_disconnect.assert_not_called()

def test_login_raised_error_reset_user () -> None:
    config.USER_ID = ObjectId()

    with (
        patch("app.util.crypto.load_private_key") as mock_load_pvt_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.find_with_id") as mock_find_user,
        patch.object(socketio.Client, "connect") as mock_connect
    ):
        mock_load_pvt_key.return_value = False
        mock_find_user.side_effect=Exception

        api = Api(True)

        assert api.user_id is None
        assert api.id_key is None
        assert api.sgn_key is None
        assert api.ed_key is None

def test_login_raised_error_reset_header () -> None:
    config.USER_ID = ObjectId()

    with (
        patch("app.util.crypto.load_private_key") as mock_load_pvt_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.find_with_id") as mock_find_user,
        patch.object(socketio.Client, "connect") as mock_connect
    ):
        mock_sign_message.return_value = True
        mock_find_user.side_effect=Exception

        api = Api(True)

        assert api.headers_client == api.headers_user

def test_api_attrs_after_logout () -> None:
    config.USER_ID = ObjectId()

    with (
        patch("app.util.crypto.load_private_key") as mock_load_pvt_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.find_with_id") as mock_find_user,
        patch.object(socketio.Client, "connect") as mock_connect,
        patch.object(socketio.Client, "disconnect") as mock_disconnect
    ):
        mock_find_user.return_value = User("test", "test", "test")

        api = Api(True)
        api.logout()

        assert api.user_id is None
        assert api.id_key is None
        assert api.sgn_key is None
        assert api.ed_key is None

def test_api_method_calls_after_logout () -> None:
    config.USER_ID = ObjectId()

    with (
        patch("app.util.crypto.load_private_key") as mock_load_pvt_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.find_with_id") as mock_find_user,
        patch.object(socketio.Client, "connect") as mock_connect,
        patch.object(socketio.Client, "disconnect") as mock_disconnect
    ):
        mock_find_user.return_value = User("test", "test", "test")

        api = Api(True)
        api.logout()

        mock_disconnect.assert_called_once()

def test_api_signup () -> None:
    pvt_key = X25519PrivateKey.generate()

    with (
        patch("app.util.crypto.generate_private_key") as mock_generate_private_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.insert_user") as mock_insert_user,
        patch("app.util.config.update_user_id") as mock_update_user_id,
        patch.object(socketio.Client, "connect") as mock_connect
    ):
        mock_generate_private_key.return_value = pvt_key

        api = Api()
        api.signup("name", "telephone", "password")

        assert isinstance(api.user_id, ObjectId)
        assert api.id_key == pvt_key
        assert api.sgn_key == pvt_key
        assert api.ed_key == pvt_key

def test_api_signup_connect_parameters () -> None:
    pvt_key = X25519PrivateKey.generate()
    pub_key = base64.encodebytes(
        pvt_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    ).decode("utf-8").strip()

    with (
        patch("app.util.crypto.generate_private_key") as mock_generate_private_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.insert_user") as mock_insert_user,
        patch("app.util.config.update_user_id") as mock_update_user_id,
        patch.object(socketio.Client, "connect") as mock_connect
    ):
        mock_generate_private_key.return_value = pvt_key

        api = Api()
        api.signup("name", "telephone", "password")

        mock_connect.assert_called_once_with(
            "http://0.0.0.0:5000",
            auth={
                "name": "name",
                "telephone": "telephone",
                "id_key": pub_key,
                "sgn_key": pub_key,
                "ed_key": pub_key,
                "opkeys": [ {
                    "id": idx,
                    "key": pub_key
                } for idx in range(1, 11) ]
            },
            headers={ "Param-Auth": config.CHAT_SECRET }
        )

def test_api_signup_user_headers () -> None:
    pvt_key = X25519PrivateKey.generate()

    with (
        patch("app.util.crypto.generate_private_key") as mock_generate_private_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.insert_user") as mock_insert_user,
        patch("app.util.config.update_user_id") as mock_update_user_id,
        patch.object(socketio.Client, "connect") as mock_connect
    ):
        mock_sign_message.return_value = True
        mock_generate_private_key.return_value = pvt_key

        api = Api()
        api.signup("name", "telephone", "password")

        assert api.headers_user == {
            "Param-Auth": config.CHAT_SECRET,
            "Signed-Message": True
        }

def test_api_signup_rollback () -> None:
    pvt_key = X25519PrivateKey.generate()

    with (
        patch("app.util.crypto.generate_private_key") as mock_generate_private_key,
        patch("app.util.crypto.sign_message") as mock_sign_message,
        patch("app.services.user.insert_user") as mock_insert_user,
        patch("app.services.user.delete_user") as mock_delete_user,
        patch.object(socketio.Client, "connect") as mock_connect
    ):
        mock_generate_private_key.return_value = pvt_key
        mock_connect.side_effect = ConnectionError

        api = Api()
        api.signup("name", "telephone", "password")

        assert api.user_id is None
        assert api.id_key is None
        assert api.sgn_key is None
        assert api.ed_key is None
        mock_delete_user.assert_called_once()