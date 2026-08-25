"""Standard API error types and handlers."""

from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class BDAError(Exception):
    """Base application error with machine-readable code."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(BDAError):
    def __init__(self, resource: str, identifier: str | None = None) -> None:
        message = f"{resource} not found"
        if identifier:
            message = f"{resource} '{identifier}' not found"
        super().__init__("NOT_FOUND", message, status_code=404)


class UnauthorizedError(BDAError):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__("UNAUTHORIZED", message, status_code=401)


class ForbiddenError(BDAError):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__("FORBIDDEN", message, status_code=403)


class InsufficientEvidenceError(BDAError):
    def __init__(self, message: str = "Insufficient evidence to answer confidently") -> None:
        super().__init__("INSUFFICIENT_EVIDENCE", message, status_code=422)


class ValidationError(BDAError):
    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__("VALIDATION_ERROR", message, status_code=422, details=details)


def error_payload(
    code: str,
    message: str,
    *,
    correlation_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "correlation_id": correlation_id or str(uuid4()),
            "details": details or {},
        }
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BDAError)
    async def bda_error_handler(request: Request, exc: BDAError) -> JSONResponse:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(
                exc.code,
                exc.message,
                correlation_id=correlation_id,
                details=exc.details,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
        code = "HTTP_ERROR"
        if exc.status_code == 404:
            code = "NOT_FOUND"
        elif exc.status_code == 401:
            code = "UNAUTHORIZED"
        elif exc.status_code == 403:
            code = "FORBIDDEN"
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(code, detail, correlation_id=correlation_id),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
        return JSONResponse(
            status_code=422,
            content=error_payload(
                "VALIDATION_ERROR",
                "Request validation failed",
                correlation_id=correlation_id,
                details={"errors": exc.errors()},
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
        return JSONResponse(
            status_code=500,
            content=error_payload(
                "INTERNAL_ERROR",
                "An unexpected error occurred",
                correlation_id=correlation_id,
            ),
        )
