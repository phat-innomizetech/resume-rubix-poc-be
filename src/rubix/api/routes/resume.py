from fastapi import APIRouter, status, UploadFile, File, HTTPException, Form

import logging
import tempfile
import shutil

from rubix.schemas.res_base import (
    DataResponse,
    ErrorResponse,
)
from rubix.schemas.res_base import DataResponse
from rubix.services.resume import ResumeProcessor


logging.basicConfig(level=logging.INFO, format="[TIL] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["resume"])


@router.post(
    "/",
    tags=["resume"],
    description="Endpoint to upload resume",
    response_model=DataResponse,
    responses={
        500: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    },
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
def upload(
    file: UploadFile = File(...),
    model_name: str = "dslim/bert-base-NER",
    provider: str = "huggingface",
    prompt: str = None
):
    logger.debug("resume: upload resume")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    try:
        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        logger.info("tmp_path = %s", tmp_path)
        return ResumeProcessor(tmp_path, model_name, provider, prompt).process()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
