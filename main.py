"""
GuardianAI Aegis Runtime - Main Application Entrypoint

This module bootstraps the FastAPI application, mounts middlewares, registers exception
handlers, establishes the startup/shutdown lifecycles, and loads versioned routers.
"""

import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import AegisError, AuthenticationError, PolicyViolationError, ResourceNotFoundError
from app.api.v1.router import router as v1_router
from app.services.database_service import DatabaseService
from app.events.subscriber import setup_subscribers
from app.services.embedding_service import embedding_service
from app.services.detection_service import detection_service

# Initialize logging configuration immediately
setup_logging()
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handles application startup and shutdown lifecycles gracefully.
    """
    logger.info("Initializing Aegis Runtime lifecycle startup sequences...")
    try:
        # 1. Wire up Pub/Sub event subscriber channels
        setup_subscribers()

        # 2. Build database schemas if they do not exist
        await DatabaseService.create_tables()

        # 3. Eager load embedding model and pre-generate vector caches
        embedding_service.initialize()
        detection_service.initialize()

        logger.info("Aegis Runtime startup sequences completed successfully.")
        yield
    finally:
        logger.info("Initiating Aegis Runtime shutdown lifecycle...")
        # Perform any cleanup steps (e.g. database pool shutdown) if necessary
        logger.info("Aegis Runtime shutdown lifecycle completed.")


def create_app() -> FastAPI:
    """
    FastAPI Application Factory.
    """
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        version="0.2.0",
        lifespan=lifespan
    )

    # 1. Configure CORS Middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Custom HTTP Execution Tracing Middleware
    @application.middleware("http")
    async def request_lifecycle_middleware(request: Request, call_next: Any) -> Response:
        # Retrieve or generate Request correlation ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()
        logger.info("HTTP IN: %s %s | ID: %s", request.method, request.url.path, request_id)

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            logger.exception("Internal application crash caught in middleware: %s", exc)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "message": "An unhandled server exception occurred.",
                        "details": {"error_type": type(exc).__name__, "message": str(exc)}
                    }
                }
            )

        process_time_ms = (time.perf_counter() - start_time) * 1000

        # Inject tracing headers into response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"

        logger.info(
            "HTTP OUT: %s %s | Status: %d | Latency: %.2fms | ID: %s",
            request.method,
            request.url.path,
            response.status_code,
            process_time_ms,
            request_id
        )
        return response

    # 3. Custom Exceptions Translation Mapping
    @application.exception_handler(AegisError)
    async def aegis_exception_handler(request: Request, exc: AegisError) -> JSONResponse:
        logger.error("Aegis Exception caught on %s: %s (%s)", request.url.path, exc.message, exc.error_code)

        # Map domain exceptions to standard HTTP response codes
        status_code = status.HTTP_400_BAD_REQUEST
        if isinstance(exc, AuthenticationError):
            status_code = status.HTTP_401_UNAUTHORIZED
        elif isinstance(exc, PolicyViolationError):
            status_code = status.HTTP_403_FORBIDDEN
        elif isinstance(exc, ResourceNotFoundError):
            status_code = status.HTTP_404_NOT_FOUND

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    # 4. Mount versioned API routes
    application.include_router(v1_router, prefix="/api/v1")

    # 5. Base Root welcome route
    @application.get("/", tags=["General"])
    async def root_welcome() -> dict:
        """
        Server root welcomes clients and links to Swagger documentation.
        """
        return {
            "message": "Welcome to GuardianAI Aegis Runtime (Phase 1 Infrastructure)",
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc"
            }
        }

    return application


# Expose ASGI application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    # Execute application locally matching settings parameters
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
