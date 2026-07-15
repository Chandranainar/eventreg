from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details=None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


def error_payload(code: str, message: str, details=None) -> dict:
    payload = {"success": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload


async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(exc.code, exc.message, exc.details),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_payload("VALIDATION_ERROR", "Validation failed.", exc.errors()),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    code = "HTTP_ERROR"
    message = "The request could not be completed."
    if exc.status_code == 401:
        code = "AUTHENTICATION_REQUIRED"
        message = "Please sign in to continue."
    elif exc.status_code == 403:
        code = "FORBIDDEN"
        message = "You do not have permission to perform this action."
    elif exc.status_code == 404:
        code = "NOT_FOUND"
        message = "The requested resource was not found."
    elif isinstance(exc.detail, dict):
        code = exc.detail.get("code", code)
        message = exc.detail.get("message", message)
    elif isinstance(exc.detail, str):
        message = exc.detail
    return JSONResponse(status_code=exc.status_code, content=error_payload(code, message))


async def api_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, IntegrityError):
        return JSONResponse(
            status_code=409,
            content=error_payload("DUPLICATE_RECORD", "A duplicate record already exists."),
        )
    return JSONResponse(
        status_code=500,
        content=error_payload("INTERNAL_SERVER_ERROR", "An unexpected error occurred."),
    )
