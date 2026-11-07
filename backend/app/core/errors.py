"""Central error handling: every error becomes ProblemDetails (RFC 7807).

docs/conventions.md, Error handling: `type` is a stable English code, `detail` is Turkish,
internal details (exception message, stack trace, SQL, paths) never reach the client.
"""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.security_headers import SECURITY_HEADERS

logger = logging.getLogger(__name__)

PROBLEM_JSON = "application/problem+json"

NOT_FOUND_DETAIL = "İstenen adres bulunamadı."
INTERNAL_ERROR_DETAIL = "Beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyin."
VALIDATION_DETAIL = "İstek geçersiz."
HTTP_ERROR_DETAIL = "İstek işlenemedi."


def problem_response(
    status: int,
    type_: str,
    title: str,
    detail: str,
    errors: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {"type": type_, "title": title, "status": status, "detail": detail}
    if errors is not None:
        body["errors"] = errors
    return JSONResponse(body, status_code=status, media_type=PROBLEM_JSON)


async def _http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):
        raise exc
    if exc.status_code == 404:
        return problem_response(404, "not-found", "Not Found", NOT_FOUND_DETAIL)
    return problem_response(exc.status_code, "http-error", "HTTP Error", HTTP_ERROR_DETAIL)


async def _validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):
        raise exc
    errors = [
        {
            "loc": list(e.get("loc", ())),
            "msg": str(e.get("msg", "")),
            "type": str(e.get("type", "")),
        }
        for e in exc.errors()
    ]
    return problem_response(422, "validation-error", "Validation Error", VALIDATION_DETAIL, errors)


async def _unexpected_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    response = problem_response(
        500, "internal-error", "Internal Server Error", INTERNAL_ERROR_DETAIL
    )
    # This handler runs outside user middleware (Starlette ServerErrorMiddleware).
    response.headers.update(SECURITY_HEADERS)
    return response


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.add_exception_handler(Exception, _unexpected_exception_handler)
