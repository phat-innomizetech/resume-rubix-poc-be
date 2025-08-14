import logging
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO, format="[Rubix] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

class ResumeLoader:
    def __init__(self, file_path: str):
        """
        Load a PDF resume file.

        :param file_path: Path to the PDF file.
        :param config: Optional configuration dictionary (currently unused, 
                       included for API compatibility).
        """
        self.file_path = file_path
        # self.config = config or {}
        self.document = self._load_doc()

    def _load_doc(self) -> str:
        """
        Extract all text from the PDF file.

        :return: Concatenated text of all pages.
        """
        logger.info("Load document")
        reader = PdfReader(self.file_path)
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return "\n".join(text).strip()

    def get_doc(self) -> str:
        """
        Get the extracted PDF text.

        :return: Extracted document text as a string.
        """
        logger.info("Get document")
        return self.document