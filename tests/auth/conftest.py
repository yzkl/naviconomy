import pytest
from pydantic import SecretStr

# Set up test objects
TEST_DATA = {
    "username": "test-user",
    "email": "email@email.com",
    "password": SecretStr("strongpassword"),
    "secret_key": SecretStr("strongkey"),
    "algorithm": SecretStr("HS256"),
    "register_payload": {
        "username": "new-user",
        "email": "new@email.com",
        "password": "weakpassword",
    },
}


@pytest.fixture
def testing_data() -> dict:
    return TEST_DATA.copy()
