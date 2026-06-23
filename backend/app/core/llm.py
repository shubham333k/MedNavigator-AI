"""
LLM client supporting Google Gemini (primary), OpenAI, and Anthropic.
Configured with medical system prompts for grounded, citation-based responses.
Priority: Gemini → OpenAI → Anthropic
"""

import logging
from functools import lru_cache
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMManager:
    """Manages the LLM client (Gemini, OpenAI, or Anthropic). Gemini is preferred."""

    _instance = None
    _llm = None
    _provider = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _initialize(self):
        """Lazy initialization of the LLM — tries Gemini first, then OpenAI, then Anthropic."""
        if self._llm is None:
            settings = get_settings()

            if settings.google_api_key:
                from google.genai.types import HarmCategory, HarmBlockThreshold
                self._llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=settings.google_api_key,
                    temperature=0.1,
                    max_output_tokens=4096,
                    timeout=60,
                    transport="rest",
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    },
                )
                self._provider = "gemini"
                logger.info("✅ Google Gemini LLM initialized (gemini-2.5-flash)")

            elif settings.openai_api_key:
                self._llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=settings.openai_api_key,
                    temperature=0.1,
                    max_tokens=4096,
                    timeout=60,
                )
                self._provider = "openai"
                logger.info("✅ OpenAI LLM initialized (gpt-4o-mini)")

            elif settings.anthropic_api_key:
                self._llm = ChatAnthropic(
                    model="claude-3-haiku-20240307",
                    anthropic_api_key=settings.anthropic_api_key,
                    temperature=0.1,
                    max_tokens=4096,
                    timeout=60,
                )
                self._provider = "anthropic"
                logger.info("✅ Anthropic Claude LLM initialized")

            else:
                logger.warning(
                    "No LLM API key found. Set GOOGLE_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY in .env"
                )

    @property
    def provider(self) -> str:
        """Which LLM provider is active."""
        self._initialize()
        return self._provider or "none"

    @property
    def model(self) -> Any:
        """Get the LLM model instance."""
        self._initialize()
        if self._llm is None:
            raise RuntimeError(
                "LLM not initialized. Please set GOOGLE_API_KEY (free), OPENAI_API_KEY, "
                "or ANTHROPIC_API_KEY in your backend/.env file."
            )
        return self._llm

    def invoke(self, messages: list) -> str:
        """Invoke the LLM with a list of messages."""
        response = self.model.invoke(messages)
        return response.content

    def stream(self, messages: list):
        """Stream LLM responses for real-time output."""
        for chunk in self.model.stream(messages):
            if chunk.content:
                yield chunk.content


@lru_cache()
def get_llm_manager() -> LLMManager:
    """Get singleton LLM manager."""
    return LLMManager()
