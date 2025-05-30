from fileinput import filename
import logging
import tempfile

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, status
from socialink.libs.b2 import b2_upload_file

logger = logging.getLogger(__name__)

router = APIRouter()

CHUNK_SIZE = 1024 * 1024


@router.post("/upload", status_code=201)
async def upload_file(file: UploadFile):
    try:
        with tempfile.NamedTemporaryFile() as temp_file:
            file_name = temp_file.name
            logger.info(f"Saving Uploaded file to {file_name}")
            async with aiofiles.open(file_name, "wb") as f:
                while chunck := await file.read(CHUNK_SIZE):
                    await f.write(chunck)

            file_url = b2_upload_file(local_file=filename, file_name=file.filename)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There wan error uploading the file",
        )

    return {"detail": f"Successfully uploaded {file.filename}", "file_url": file_url}
