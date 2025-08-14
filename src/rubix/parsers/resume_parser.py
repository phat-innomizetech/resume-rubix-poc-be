import logging
from math import log
from typing import Any, Dict, Union, Optional
from transformers import pipeline
from langchain_google_genai import ChatGoogleGenerativeAI
from rubix.core.config import settings
from rubix.constants.prompt import DEFAULT_PROMPT
from rubix.helpers.convert_ner import ner_to_resume_schema

logging.basicConfig(level=logging.INFO, format="[Rubix] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

class ResumeParser:
    """
    Unified wrapper:
      - provider='huggingface'  -> token-classification (NER). Input: raw text. Output: list[entities]
      - provider='google'       -> chat LLM. Input: formatted prompt. Output: str (content)
      - provider='openresume'   -> not implemented yet.
    """

    def __init__(self, model_name: str, provider: str, prompt: Optional[str] = None):
        self.model_name = model_name
        self.provider = provider  # 'huggingface' | 'google' | 'openresume'
        self._prompt = prompt  # only used by LLM-style providers
        self._choose_model()

    def _choose_model(self) -> None:
        if self.provider == "huggingface":
            logger.info("Calling HuggingFace provider (token-classification)")
            self._model = pipeline("token-classification", model=self.model_name)

        elif self.provider == "google":
            logger.info("Calling Google provider (chat)")
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY is not set")
            self._model = ChatGoogleGenerativeAI(model=self.model_name, google_api_key=api_key)
            if self._prompt is None:
                self._prompt = DEFAULT_PROMPT  # must contain `{text}`

        elif self.provider == "openresume":
            logger.info("Calling OpenResume provider (not implemented)")
            raise NotImplementedError("provider='openresume' not implemented yet")

        else:
            raise ValueError(f"Provider '{self.provider}' isn't supported.")

    def parse(self, text: str) -> Union[str, Dict[str, Any], list]:
        """
        Returns:
          - huggingface: list of aggregated NER entities (dicts)
          - google: str (LLM content)
        """
        logger.info("parse text")
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if self.provider == "huggingface":
            ner_text = self._model(text)
            return ner_to_resume_schema(ner_text)

        elif self.provider == "google":
            input_text = self._prompt.format(text=text) if self._prompt else text
            msg = self._model.invoke(input_text)
            return getattr(msg, "content", str(msg))

        raise RuntimeError("Invalid provider state")