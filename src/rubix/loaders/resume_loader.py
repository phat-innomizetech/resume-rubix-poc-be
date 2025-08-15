"""
PDF document loader for resume processing.

This module provides functionality to load and extract text content from PDF
resume documents. It uses PyPDF for PDF processing and includes comprehensive
error handling for various file and processing issues.
"""

import logging
import os
from pypdf import PdfReader
from pypdf.errors import PdfReadError, FileNotDecryptedError

logging.basicConfig(level=logging.INFO, format="[Rubix] %(name)s - %(message)s")
logger = logging.getLogger(__name__)


class ResumeLoader:
    """
    PDF document loader for extracting text from resume files.

    This class handles the loading and text extraction from PDF resume documents.
    It provides error handling for common PDF processing issues and validates
    file existence and format before processing.

    Attributes:
        file_path (str): Path to the PDF file to be loaded
        document (str): Extracted text content from the PDF
    """

    def __init__(self, file_path: str):
        """
        Initialize the ResumeLoader with a PDF file path.

        Args:
            file_path (str): Path to the PDF file to be loaded and processed

        Raises:
            FileNotFoundError: If the specified file does not exist
            ValueError: If the file path is empty or invalid
            Exception: Various PDF processing errors (handled and logged)
        """
        if not file_path:
            raise ValueError("File path cannot be empty")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        self.file_path = file_path
        self.document = self._load_doc()

    def _load_doc(self) -> str:
        """
        Extract all text from the PDF file with comprehensive error handling.

        This method reads the PDF file and extracts text from all pages,
        handling various PDF processing errors gracefully.

        Returns:
            str: Concatenated text from all pages of the PDF

        Raises:
            PdfReadError: If the PDF file is corrupted or cannot be read
        """
        logger.info("Loading document from: %s", self.file_path)

        try:
            reader = PdfReader(self.file_path)

            # Check if PDF is encrypted
            if reader.is_encrypted:
                logger.error("PDF file is password-protected: %s", self.file_path)
                raise FileNotDecryptedError("PDF file is password-protected")

            text = []
            total_pages = len(reader.pages)
            logger.info("Processing %d pages", total_pages)

            for page_num, page in enumerate(reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
                        logger.debug("Extracted text from page %d", page_num)
                    else:
                        logger.warning("No text extracted from page %d", page_num)
                except PdfReadError as e:
                    logger.error(
                        "Error extracting text from page %d: %s", page_num, str(e)
                    )
                    # Continue processing other pages even if one fails
                    continue

            if not text:
                logger.warning("No text content extracted from PDF: %s", self.file_path)
                return ""

            extracted_text = "\n".join(text).strip()
            logger.info(
                "Successfully extracted %d characters from PDF", len(extracted_text)
            )
            return extracted_text

        except PdfReadError as e:
            logger.error("Failed to read PDF file %s: %s", self.file_path, str(e))
            raise PdfReadError(f"Invalid or corrupted PDF file: {str(e)}") from e

    def get_doc(self) -> str:
        """
        Get the extracted PDF text content.

        Returns the previously extracted text content from the PDF document.
        This method provides a simple interface to access the processed document.

        Returns:
            str: The extracted document text as a string

        Raises:
            RuntimeError: If the document was not successfully loaded
        """
        logger.info("Retrieving document content")

        if not hasattr(self, "document") or self.document is None:
            logger.error("Document not properly loaded")
            raise RuntimeError("Document was not successfully loaded")

        return self.document
