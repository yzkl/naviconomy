from bcrypt import checkpw

from auth.utils import get_password_hash


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
