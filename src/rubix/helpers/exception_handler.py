from datetime import datetime
from typing import Optional

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from rubix.schemas.res_base import (
    ErrorResponse,
    ResponseMetadata,
    StatusCode,
)


class CustomException(Exception):
    """Custom exception class with standardized error handling."""

    def __init__(
        self,
        http_code: int = 500,
        code: Optional[str] = None,
        message: str = "Internal Server Error",
        errors: Optional[list[dict]] = None,
        requestId: Optional[str] = None,
    ):
        self.http_code = http_code
        self.code = code or str(http_code)
        self.message = message
        self.errors = errors
        self.requestId = requestId
        super().__init__(message)


async def http_exception_handler(request: Request, exc: CustomException):
    """Handle custom exceptions and return standardized error responses."""
    metadata = ResponseMetadata(
        timestamp=datetime.utcnow().isoformat(), requestId=exc.requestId
    )

    error_response = ErrorResponse.create(
        message=exc.message,
        code=StatusCode(exc.code),
        errors=exc.errors,
        metadata=metadata,
    )

    return JSONResponse(
        status_code=exc.http_code, content=jsonable_encoder(error_response)
    )


async def validation_exception_handler(request: Request, exc):
    """Handle validation exceptions and return standardized error responses."""
    errors = [
        {"loc": err["loc"], "msg": err["msg"], "type": err["type"]}
        for err in exc.errors()
    ]

    error_response = ErrorResponse.create(
        message="Validation Error", code=StatusCode.BAD_REQUEST, errors=errors
    )

    return JSONResponse(status_code=400, content=jsonable_encoder(error_response))


async def fastapi_error_handler(request: Request, exc):
    """Handle FastAPI errors and return standardized error responses."""
    error_response = ErrorResponse.create(
        message="Internal Server Error", code=StatusCode.INTERNAL_ERROR
    )

    return JSONResponse(status_code=500, content=jsonable_encoder(error_response))


def get_message_validation(exc):
    """
    Get the message from validation exception."
    """
    message = ""
    for error in exc.errors():
        message += (
            "/'" + str(error.get("loc")[1]) + "'/" + ": " + error.get("msg") + ", "
        )

    message = message[:-2]

    return message
