from bcrypt import gensalt, hashpw
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
