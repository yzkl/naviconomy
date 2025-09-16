from datetime import datetime, timedelta, timezone

import jwt
import pytest
from bcrypt import checkpw
from pydantic import SecretStr

from auth.models import TokenData
from auth.utils import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from config.settings import settings
from exceptions.exceptions import InvalidTokenError

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


def test_get_password_hash_returns_valid_hash(testing_data) -> None:
    hashed_password = get_password_hash(testing_data["password"])

    assert isinstance(hashed_password, str)
    assert hashed_password != testing_data["password"]
    assert checkpw(
        testing_data["password"].get_secret_value().encode(), hashed_password.encode()
    )


def test_get_password_hash_randomness(testing_data) -> None:
    hash1 = get_password_hash(testing_data["password"])
    hash2 = get_password_hash(testing_data["password"])

    assert hash1 != hash2


def test_verify_password_returns_False_for_incorrect_password(testing_data) -> None:
    hashed_password = get_password_hash(testing_data["password"])
    wrong_password = SecretStr("wrongpassword")

    assert not verify_password(wrong_password, hashed_password)


def test_verify_password_returns_False_for_invalid_hash(testing_data) -> None:
    invalid_hash = "not a hash"

    assert not verify_password(testing_data["password"], invalid_hash)


def test_verify_password_regular(testing_data) -> None:
    hashed_password = get_password_hash(testing_data["password"])

    assert verify_password(testing_data["password"], hashed_password)


def test_create_access_token_returns_decodeable_token(testing_data) -> None:
    token = create_access_token(testing_data["token_payload"])
    decoded = jwt.decode(
        token, SECRET_KEY.get_secret_value(), ALGORITHM.get_secret_value()
    )

    assert decoded["sub"] == testing_data["username"]
    assert "exp" in decoded


def test_create_access_token_with_default_expiration(testing_data) -> None:
    token = create_access_token(testing_data["token_payload"])
    decoded = jwt.decode(
        token, SECRET_KEY.get_secret_value(), ALGORITHM.get_secret_value()
    )

    assert decoded["exp"] == int(
        (datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp()
    )


def test_create_access_token_with_custom_expiration(testing_data) -> None:
    token = create_access_token(testing_data["token_payload"], timedelta(minutes=45))
    decoded = jwt.decode(
        token, SECRET_KEY.get_secret_value(), ALGORITHM.get_secret_value()
    )

    assert decoded["exp"] == int(
        (datetime.now(timezone.utc) + timedelta(minutes=45)).timestamp()
    )


def test_create_access_token_preserves_payload(testing_data) -> None:
    testing_data["token_payload"].update({"role": "admin"})
    token = create_access_token(testing_data["token_payload"])
    decoded = jwt.decode(
        token, SECRET_KEY.get_secret_value(), ALGORITHM.get_secret_value()
    )

    for key in testing_data["token_payload"]:
        assert decoded[key] == testing_data["token_payload"][key]


def test_verify_token_raises_InvalidTokenError_for_invalid_token() -> None:
    invalid_token = "not a token"
    with pytest.raises(InvalidTokenError):
        verify_token(invalid_token)


def test_verify_token_raises_InvalidTokenError_for_expired_token(testing_data) -> None:
    expired_token = create_access_token(
        testing_data["token_payload"], now_fn=lambda: datetime(2025, 1, 1)
    )
    with pytest.raises(InvalidTokenError):
        verify_token(expired_token)


def test_verify_token_raises_InvalidTokenError_for_missing_sub_claim() -> None:
    test_payload = {"role": "admin"}
    missing_claim_token = create_access_token(test_payload)
    with pytest.raises(InvalidTokenError):
        verify_token(missing_claim_token)


# @patch("auth.utils.SECRET_KEY")
def test_verify_token_regular(testing_data) -> None:
    token = create_access_token(testing_data["token_payload"])
    verified = verify_token(token)

    assert isinstance(verified, TokenData)
    assert verified.username == testing_data["token_payload"]["sub"]
