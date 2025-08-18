"""
Resume processing API routes.

This module provides FastAPI routes for resume upload and processing functionality.
It handles file uploads, validation, and coordinates with the resume processing service
to extract structured information from PDF resume documents.
"""

import logging
import tempfile
import shutil

from fastapi import APIRouter, status, UploadFile, File, HTTPException

from rubix.schemas.res_base import (
    DataResponse,
    ErrorResponse,
)
from rubix.services.resume_processor import ResumeProcessor


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
    prompt: str = "",
) -> DataResponse:
    """
    Upload and process a resume PDF file.

    This endpoint accepts a PDF resume file and processes it using the specified
    AI model and provider to extract structured resume information. The file is
    temporarily saved to disk, processed, and then cleaned up automatically.

    Args:
        file (UploadFile): The PDF resume file to be processed. Must be a valid PDF file.
        model_name (str, optional): The AI model name to use for processing.
                                   Defaults to "dslim/bert-base-NER".
        provider (str, optional): The AI provider to use for processing.
                                 Supported values: "huggingface", "google", "resume_parser_pro".
                                 Defaults to "huggingface".
        prompt (str, optional): Custom prompt template for LLM-style providers.
                               Only used when provider is "google".
                               Defaults to None.

    Returns:
        DataResponse: A response object containing either:
            - Success: Parsed resume data (structured or raw text depending on provider)
            - Error: Error message if processing fails

    Raises:
        HTTPException:
            - 400: If the uploaded file is not a PDF
            - 500: If there's an error during file processing or resume parsing

    Example:
        ```python
        # Upload a resume with default settings
        response = await upload(file=pdf_file)

        # Upload with custom model and provider
        response = await upload(
            file=pdf_file,
            model_name="custom-ner-model",
            provider="google",
            prompt="Extract the following information: {text}"
        )
        ```
    """
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
