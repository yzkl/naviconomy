from datetime import datetime, timedelta, timezone
from typing import Callable

import jwt
from bcrypt import checkpw, gensalt, hashpw
from pydantic import SecretStr

from auth.models import TokenData
from config.settings import settings
from exceptions.exceptions import InvalidTokenError

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm


def get_password_hash(password: SecretStr) -> str:
    """Generate a bcrpyt hash from a password.

    A random salt is automatically generated and applied during hasing.
    The resulting hash is returned as a UTF-8 encoded string.

    Parameters
    ----------
    password : SecretStr
        The password to hash.

    Returns
    -------
    str
        A bcrypt hash of the password, encoded as a UTF-8 string.
    """
    return hashpw(password.get_secret_value().encode(), gensalt()).decode()


def verify_password(plain_password: SecretStr, hashed_password: str) -> bool:
    """Verify whether a plaintext password matches a bcrypt hash.

    Parameters
    ----------
    plain_password : SecretStr
        The secret-wrapped plaintext password to verify.

    hashed_password: str
        The bcrypt hash to compare against.

    Returns
    -------
    bool
        True if the password matches the hash, False otherwise.
    """
    try:
        return checkpw(
            plain_password.get_secret_value().encode(),
            hashed_password.encode(),
        )
    except (TypeError, ValueError):
        return False


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
    now_fn: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> str:
    """Create a JSON Web Token (JWT) signed with the project's secret key and algorithm.

    If no expiration interval is provided, the token will expire 15 minutes after creation.
    The token's expiration timestamp is generated in UTC.

    Parameters
    ----------
    data : dict
        The data to encode into the JWT. This will be copied and updated with an expiration timestamp.

    expires_delta : timedelta, optional
        Time until the token expires. Defaults to 15 minutes.

    now_fn : Callable[[], datetime], optional
        Function that returns the current UTC time. Defaults to `datetime.now(timezone.utc)`.
        Primarily intended for testing purposes, allowing for the injection of a fixed time for deterministic token outputs.
    """
    to_encode = data.copy()
    now = now_fn()
    expire = now + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(
        to_encode, SECRET_KEY.get_secret_value(), ALGORITHM.get_secret_value()
    )
    return encoded_token


def verify_token(token: str) -> TokenData:
    """Verify and decode a JSON Web Token (JWT) using the project's secret key and algorithm.

    Returns a `TokenData` pydantic model containing the username extracted from the token.

    Parameters
    ----------
    token : str
        The JWT to verify and decode.

    Returns
    -------
    TokenData
        A pydantic model containing the data extracted from the token's `sub` claim.

    Raises
    ------
    InvalidTokenError
        If the token is invalid, expired, or missing a `sub` claim.
    """
    try:
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except jwt.PyJWTError:
        raise InvalidTokenError("Invalid or expired token.")
    if not username:
        raise InvalidTokenError("Missing a 'sub' claim in token.")
    return TokenData(username)
