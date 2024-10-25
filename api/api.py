from fastapi import FastAPI
from services.search_service_handler import search_router

app = FastAPI()

# Include search router for modularized endpoints
app.include_router(search_router)
