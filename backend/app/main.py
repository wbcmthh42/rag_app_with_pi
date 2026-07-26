from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.chat import router as chat_router
from app.api.schemas.chat import ErrorResponse
from app.observability.logging import configure_logging

configure_logging()

app = FastAPI(title="Conversational Barbie PDF Assistant API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router, prefix="/api/v1")


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    if isinstance(exc.detail, dict) and {"error_code", "message"}.issubset(exc.detail.keys()):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    error = ErrorResponse(error_code="internal_error", message=str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=error.model_dump())


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_: Request, exc: RequestValidationError):
    message = exc.errors()[0].get("msg", "Invalid request.") if exc.errors() else "Invalid request."
    error = ErrorResponse(error_code="invalid_request", message=message)
    return JSONResponse(status_code=400, content=error.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    error = ErrorResponse(error_code="internal_error", message=str(exc))
    return JSONResponse(status_code=500, content=error.model_dump())
