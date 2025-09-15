from bcrypt import checkpw, gensalt, hashpw
from pydantic import SecretStr


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
        checkpw(
            plain_password.get_secret_value().encode(),
            hashed_password.encode(),
        )
    except (TypeError, ValueError):
        return False
