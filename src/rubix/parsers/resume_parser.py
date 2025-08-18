"""
Resume parsing module with support for multiple AI providers.

This module provides a unified interface for parsing resume documents using
different AI providers and models. It supports HuggingFace NER models,
Google's Generative AI, and resume_parser_pro for extracting structured
information from resume text.
"""

import logging
from typing import Any, Dict, Union
from transformers import pipeline
from langchain_google_genai import ChatGoogleGenerativeAI
from resume_parser_pro import ResumeParser as OpenParser

from rubix.core.config import settings
from rubix.constants.prompt import DEFAULT_PROMPT
from rubix.helpers.response_processing import ner_to_resume_schema, extract_json_content


logging.basicConfig(level=logging.INFO, format="[Rubix] %(name)s - %(message)s")
logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Unified resume parser supporting multiple AI providers and models.

    This class provides a consistent interface for parsing resume documents
    regardless of the underlying AI provider. It automatically handles
    model initialization, text processing, and result formatting based on
    the specified provider.

    Supported providers:
        - 'huggingface': Uses token-classification (NER) models
        - 'google': Uses Google's Generative AI (chat LLM)
        - 'resume_parser_pro': Uses the resume_parser_pro library

    Attributes:
        model_name (str): Name of the AI model to use for parsing
        provider (str): The AI provider ('huggingface', 'google', 'resume_parser_pro')
        _prompt (Optional[str]): Prompt template for LLM-style providers
        _model: The initialized model instance for the chosen provider
    """

    def __init__(self, model_name: str, provider: str, prompt: str = ""):
        """
        Initialize the ResumeParser with the specified model and provider.

        Args:
            model_name (str): Name of the AI model to use for parsing
            provider (str): The AI provider to use ('huggingface', 'google', 'resume_parser_pro')
            prompt (str): Custom prompt template for LLM providers.
                                   If None, uses DEFAULT_PROMPT for Google provider.

        Raises:
            ValueError: If the provider is not supported or if GEMINI_API_KEY is missing for Google provider
        """
        self.model_name = model_name
        self.provider = provider  # 'huggingface' | 'google' | 'resume_parser_pro'
        self._prompt = prompt  # only used by LLM-style providers
        self._choose_model()

    def _choose_model(self) -> None:
        """
        Initialize the appropriate model based on the chosen provider.

        This method sets up the model instance for the specified provider:
        - HuggingFace: Creates a token-classification pipeline
        - Google: Creates a ChatGoogleGenerativeAI instance
        - resume_parser_pro: No model initialization needed (handled in parse method)

        Raises:
            ValueError: If the provider is not supported or if GEMINI_API_KEY is missing
        """
        if self.provider == "huggingface":
            logger.info("Calling HuggingFace provider (token-classification)")
            self._model = pipeline("token-classification", model=self.model_name)

        elif self.provider == "google":
            logger.info("Calling Google provider (chat)")
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY is not set")
            self._model = ChatGoogleGenerativeAI(
                model=self.model_name, google_api_key=api_key
            )
            if not self._prompt:
                self._prompt = DEFAULT_PROMPT  # must contain `{text}`

        elif self.provider == "resume_parser_pro":
            logger.info("Calling OpenResume provider")

        else:
            raise ValueError(f"Provider '{self.provider}' isn't supported.")

    def parse(self, text: str) -> Union[str, Dict[str, Any]]:
        """
        Parse resume text using the initialized model and provider.

        This method processes the input text according to the chosen provider:
        - HuggingFace: Uses NER to extract entities and converts to resume schema
        - Google: Uses LLM with prompt to generate structured content
        - resume_parser_pro: Uses the OpenParser library for parsing

        Args:
            text (str): The resume text to parse

        Returns:
            Union[str, Dict[str, Any], list]: Parsed resume data in the format:
                - HuggingFace: List of aggregated NER entities (dicts)
                - Google: String containing LLM-generated content
                - resume_parser_pro: Dictionary with parsed resume data

        Raises:
            TypeError: If text is not a string
            RuntimeError: If the provider is unsupported
            Exception: Various exceptions from the underlying models
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if self.provider.lower() == "huggingface":
            try:
                logger.info("HuggingFace parser is processing")
                ner_text = self._model(text)
                return ner_to_resume_schema(ner_text)
            except Exception as e:
                logger.error("HuggingFace parser error %s", e)
                raise RuntimeError("HuggingFace parser error %s", e)

        elif self.provider.lower() == "google":
            try:
                logger.info("Google's API parser is processing")
                input_text = self._prompt.format(text=text) if self._prompt else text
                msg = self._model.invoke(input_text)
                content = getattr(msg, "content", str(msg))
                return extract_json_content(content)
            except Exception as e:
                logger.error("Google's API parser error %s", e)
                raise RuntimeError("Google's API parser error %s", e)

        elif self.provider.lower() == "resume_parser_pro":
            try:
                logger.info("resume_parser_pro is processing")
                parser = OpenParser(text)
                data = parser.parse()
                return data
            except Exception as e:
                logger.error("resume_parser_pro error %s", e)
                raise RuntimeError("resume_parser_pro error %s", e)
        else:
            logger.error("Unsupported provider, %s", self.provider)
            raise RuntimeError(f"Provider {self.provider} is unsupported")
