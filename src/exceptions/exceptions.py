class NaviconomyApiError(Exception):
    """Base excpetion class for the Naviconomy API."""

    def __init__(
        self, message: str = "Service is unavailable.", name: str = "NaviconomyApi"
    ):
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)


class ServiceError(NaviconomyApiError):
    """External service or DB failure."""

    pass


class EntityAlreadyExistsError(NaviconomyApiError):
    """Entity already exists."""

    pass


class EntityDoesNotExistError(NaviconomyApiError):
    """Entity not found."""

    pass


class RegistrationFailed(NaviconomyApiError):
    """Registration failed."""

    pass


class AuthenticationFailed(NaviconomyApiError):
    """Invalid username or password."""

    pass


class InvalidTokenError(NaviconomyApiError):
    """Invalid or expired token."""

    pass


class InvalidAccountError(NaviconomyApiError):
    """Account has been disabled or deactivated."""

    pass
