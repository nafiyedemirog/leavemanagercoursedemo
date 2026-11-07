"""Application setup: routers, error handlers, security headers, static frontend."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import health
from app.core.errors import register_error_handlers
from app.core.security_headers import SecurityHeadersMiddleware

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "public"


def create_app() -> FastAPI:
    # Interactive API docs load assets from a CDN, which the CSP (default-src 'self') blocks;
    # they stay off until a spec asks for them.
    app = FastAPI(title="Leave Manager", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(SecurityHeadersMiddleware)
    register_error_handlers(app)
    app.include_router(health.router, prefix="/api")
    # Mounted last: everything not matched above is a static file or a 404.
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    return app


app = create_app()
