"""
Production-ready error handling middleware
"""

import logging
from typing import Union
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """Centralized error handling for production"""
    
    @staticmethod
    async def handle_error(request: Request, exc: Exception) -> JSONResponse:
        """Handle all exceptions and return appropriate responses"""
        
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Log the error
        logger.error(
            "Unhandled exception",
            extra={
                "request_id": request_id,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "url": str(request.url),
                "method": request.method
            }
        )
        
        # Determine error response
        if isinstance(exc, HTTPException):
            return ErrorHandlerMiddleware._handle_http_exception(exc, request_id)
        elif isinstance(exc, RequestValidationError):
            return ErrorHandlerMiddleware._handle_validation_error(exc, request_id)
        elif isinstance(exc, StarletteHTTPException):
            return ErrorHandlerMiddleware._handle_starlette_exception(exc, request_id)
        else:
            return ErrorHandlerMiddleware._handle_generic_exception(exc, request_id)
    
    @staticmethod
    def _handle_http_exception(exc: HTTPException, request_id: str) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "message": exc.detail,
                "request_id": request_id,
                "status_code": exc.status_code
            },
            headers={"X-Request-ID": request_id}
        )
    
    @staticmethod
    def _handle_validation_error(exc: RequestValidationError, request_id: str) -> JSONResponse:
        """Handle request validation errors"""
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "message": "Invalid request data",
                "details": exc.errors(),
                "request_id": request_id,
                "status_code": 422
            },
            headers={"X-Request-ID": request_id}
        )
    
    @staticmethod
    def _handle_starlette_exception(exc: StarletteHTTPException, request_id: str) -> JSONResponse:
        """Handle Starlette HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Exception",
                "message": exc.detail,
                "request_id": request_id,
                "status_code": exc.status_code
            },
            headers={"X-Request-ID": request_id}
        )
    
    @staticmethod
    def _handle_generic_exception(exc: Exception, request_id: str) -> JSONResponse:
        """Handle generic exceptions"""
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "request_id": request_id,
                "status_code": 500
            },
            headers={"X-Request-ID": request_id}
        )


def setup_error_handlers(app):
    """Setup global error handlers for FastAPI app"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return await ErrorHandlerMiddleware.handle_error(request, exc)
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return await ErrorHandlerMiddleware.handle_error(request, exc)
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
        return await ErrorHandlerMiddleware.handle_error(request, exc)
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return await ErrorHandlerMiddleware.handle_error(request, exc)
