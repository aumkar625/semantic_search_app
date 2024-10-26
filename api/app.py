# app.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from services.search_service_handler import search_router
import services.logger_base  # Ensure logging is configured

import logging

logger = logging.getLogger(__name__)

app = FastAPI()

# Include search router for modularized endpoints
app.include_router(search_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


@app.get("/")
async def root():
    return {"message": "Semantic Search API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
