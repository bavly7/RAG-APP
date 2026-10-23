from fastapi import FastAPI , APIRouter , Depends , UploadFile,status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
from controllers import DataController , ProjectController
from models import ResponseSignal
import aiofiles
import logging
logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix = "/api/v1/data",
    tags = ["api_v1" ,"data"]
)

@data_router.post("/upload/{project_id}")
async def upload_data(project_id : str , file : UploadFile
                    ,app_sett:Settings=Depends(get_settings)):
    datac_controller=DataController()
    is_valid , Signal= datac_controller.validation_upload_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content ={
                "signal" : Signal
                }
        )
    
    project_dir_path =ProjectController().project_path(project_id = project_id)
    file_path = datac_controller.generate_unique_filepath(
        orig_filename=file.filename,
        project_path=project_dir_path
    )
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_sett.FILE_CHUNCK_SIZE):
                await f.write(chunk)
    except Exception as e:

        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            }
        )