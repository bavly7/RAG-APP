from fastapi import FastAPI , APIRouter , Depends , UploadFile,status
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings,Settings
from controllers import DataController , ProjectController , ProcessController
from models import ResponseSignal
import aiofiles
import logging
logger = logging.getLogger('uvicorn.error')
from .schemes.data import ProcessRequest

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
    file_path , file_id= datac_controller.generate_unique_filepath(
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
                "file_id" : file_id
            }
        )

@data_router.post("/process/{project_id}")
async def process_endpoint(project_id:str , process_request :ProcessRequest):
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    process_controller = ProcessController(project_id=project_id)
    file_content = process_controller.get_file_content(file_id = file_id)
    file_chunks = process_controller.process_file_content(
        file_id=file_id,
        file_content=file_content,
        chunk_size=chunk_size ,
        overlap_size=overlap_size
    )
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value
            }
        )

    return file_chunks

