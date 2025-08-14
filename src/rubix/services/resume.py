"""
A flexible PDF parsing utility with a pluggable parser method.

This module defines the PDFParser class, which allows a user to
pass in any callable function (e.g., from a library or a model)
to handle the actual parsing logic.
"""

import logging
from rubix.schemas.res_base import (
    DataResponse,
)
from rubix.schemas.resume import ResumeSchema
from rubix.loaders.resume_loader import ResumeLoader
from rubix.parsers.resume_parser import ResumeParser

logging.basicConfig(level=logging.INFO, format="[Rubix] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

class ResumeProcessor:
    def __init__(
        self,
        file_path: str,
        model_name: str,
        provider: str,
        prompt: str,
        # config: dict = None
    ):
        self.file_path = file_path
        self.loader = ResumeLoader(file_path=self.file_path)
        self.parser = ResumeParser(model_name, provider, prompt=prompt)

    def process(self):
        try:
            logger.info("Run resume processing pipeline")
            raw_text = self.loader.get_doc()
            parsed_text = self.parser.parse(raw_text).content
            return DataResponse.success(data=ResumeSchema.model_validate(parsed_text))
        except Exception as e:
            logger.error(f"Resume processing pipeline - {e}")
            return DataResponse.error(
                message=str(e),
            )
