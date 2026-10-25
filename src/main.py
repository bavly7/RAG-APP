from fastapi import FastAPI
from routes import base
from routes import data
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager

app = FastAPI()

"""@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()
    
    Outdated 
    """
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB connection
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]
    
    yield  # Application runs while yielded
    
    # Shutdown: Close DB connection
    app.mongo_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)

