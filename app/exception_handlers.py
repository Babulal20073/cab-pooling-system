from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
)


async def email_already_exists_handler(
    request: Request,
    exc: EmailAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


async def invalid_credentials_handler(
    request: Request,
    exc: InvalidCredentialsError,
):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
    )