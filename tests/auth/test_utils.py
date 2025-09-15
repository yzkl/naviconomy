from bcrypt import checkpw
from pydantic import SecretStr

from auth.utils import get_password_hash, verify_password


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
