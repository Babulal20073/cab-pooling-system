from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    OfficeAlreadyExistsError,
    OfficeNotFoundError
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

async def office_already_exists_handler(
    request: Request,
    exc: OfficeAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )
async def office_not_found_handler(
        request:Request,
        exc:OfficeNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={"details":str(exc)}
    )