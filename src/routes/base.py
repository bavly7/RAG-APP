from fastapi import FastAPI , APIRouter , Depends
import os
from helpers.config import get_settings , Settings
base_router = APIRouter(
    prefix = "/api/v1" ,
    tags = ["api_v1"]
)

@base_router.get("/")
async def welcome(app_sett : Settings=Depends(get_settings)):
    # app_sett = get_settings()
    name = app_sett.APP_NAME
    version = app_sett.VERSION
    return {
        "name" : name,
        "version":version
    }