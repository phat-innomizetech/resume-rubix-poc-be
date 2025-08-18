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
    """
    A service class for processing resume documents using different AI providers.

    This class orchestrates the resume processing pipeline by coordinating
    between document loading, parsing, and response formatting. It supports
    multiple AI providers including Google and HuggingFace models.

    Attributes:
        file_path (str): Path to the resume file to be processed
        loader (ResumeLoader): Instance responsible for loading document content
        parser (ResumeParser): Instance responsible for parsing document content
        provider (str): The AI provider to use for processing (e.g., 'google', 'huggingface')
    """

    def __init__(
        self,
        file_path: str,
        model_name: str,
        provider: str,
        prompt: str,
        # config: dict = None
    ):
        """
        Initialize the ResumeProcessor with the necessary components.

        Args:
            file_path (str): Path to the resume file to be processed
            model_name (str): Name of the AI model to use for parsing
            provider (str): The AI provider to use (e.g., 'google', 'huggingface')
            prompt (str): The prompt template to use for parsing the resume
        """
        self.file_path = file_path
        self.loader = ResumeLoader(file_path=self.file_path)
        self.parser = ResumeParser(model_name, provider, prompt)
        self.provider = provider

    def process(self) -> DataResponse:
        """
        Process the resume document and return structured data.

        This method handles the complete resume processing pipeline:
        1. For non-Google/HuggingFace providers: Direct file parsing
        2. For Google/HuggingFace providers: Document loading followed by parsing

        Returns:
            DataResponse: A response object containing either:
                - Success: Parsed resume data (raw text or structured ResumeSchema)
                - Error: Error message if processing fails

        Raises:
            Exception: Various exceptions can be raised during processing,
                      which are caught and returned as error responses
        """
        logger.info("Running Resume Processor with provider %s", self.provider)
        if self.provider not in ["google", "huggingface"]:
            try:
                parsed_text = self.parser.parse(self.file_path)
                return DataResponse.success(data=parsed_text)
            except Exception as e:
                logger.error("Error in Parser, detail: %s", e)
                return DataResponse.error(
                    message=str(e),
                )
        try:
            raw_text = self.loader.get_doc()
            parsed_text = self.parser.parse(raw_text)
            return DataResponse.success(data=ResumeSchema.model_validate(parsed_text))
        except Exception as e:
            logger.error("Error in ResumeProcessor, detail: %s", e)
            return DataResponse.error(
                message=str(e),
            )
