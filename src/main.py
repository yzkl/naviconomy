from contextlib import asynccontextmanager
from typing import Callable

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from api.routes.router import base_router
from auth.dependencies import get_current_active_user
from auth.routes import auth_router
from config.constants import API_PREFIX, VERSION
from config.settings import settings
from core.log import setup_logging
from database.session import sessionmanager
from database.tables import create_tables
from exceptions.exceptions import (
    AuthenticationFailed,
    EntityAlreadyExistsError,
    EntityDoesNotExistError,
    InvalidAccountError,
    InvalidTokenError,
    NaviconomyApiError,
    RegistrationFailed,
    RelatedEntityDoesNotExistError,
    ServiceError,
)

setup_logging(settings.debug)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if sessionmanager.engine is not None:
        await create_tables(sessionmanager)

    yield

    if sessionmanager.engine is not None:
        sessionmanager.close()


app = FastAPI(
    title=settings.project_name,
    debug=settings.debug,
    version=VERSION,
    lifespan=lifespan,
)
app.include_router(
    base_router, prefix=API_PREFIX, dependencies=Depends(get_current_active_user)
)
app.include_router(auth_router, prefix=API_PREFIX)


@app.get("/")
def read_root() -> Response:
    return Response("The server is running.")


def create_exception_handler(
    status_code: int, initial_message: str
) -> Callable[[Request, NaviconomyApiError], JSONResponse]:
    detail = {"message": initial_message}

    async def exception_handler(_: Request, exc: NaviconomyApiError) -> JSONResponse:
        if exc.message:
            detail["message"] = exc.message
        if exc.name:
            detail["message"] = f"{detail['message']} [{exc.name}]"

        return JSONResponse(
            status_code=status_code, content={"detail": detail["message"]}
        )

    return exception_handler


app.add_exception_handler(
    exc_class_or_status_code=EntityDoesNotExistError,
    handler=create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND, initial_message="Entity not found."
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=EntityAlreadyExistsError,
    handler=create_exception_handler(
        status_code=status.HTTP_409_CONFLICT, initial_message="Entity already exists."
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=RelatedEntityDoesNotExistError,
    handler=create_exception_handler(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        initial_message="Related entity not found.",
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=RegistrationFailed,
    handler=create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_message="Username or email is already in use.",
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=AuthenticationFailed,
    handler=create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_message="Invalid username or password.",
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=InvalidTokenError,
    handler=create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_message="Invalid or expired token.",
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=InvalidAccountError,
    handler=create_exception_handler(
        status_code=status.HTTP_403_FORBIDDEN,
        initial_message="Account exists, but has been disabled or deactivated.",
    ),
)

app.add_exception_handler(
    exc_class_or_status_code=ServiceError,
    handler=create_exception_handler(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        initial_message="A service seems to be down. Please try again later.",
    ),
)
