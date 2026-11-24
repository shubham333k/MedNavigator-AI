"""
LLM client supporting Anthropic Claude (primary), OpenAI GPT-4o, and Google Gemini.

Priority (blueprint §4.3):
  1. Anthropic Claude 3.5 Sonnet — preferred for HIPAA BAA-covered deployments
  2. OpenAI GPT-4o             — BAA-covered alternative
  3. Google Gemini 3.8 Flash   — free-tier fallback for local development

Configure API keys in backend/.env (see .env.example for instructions).
"""

import logging
from functools import lru_cache
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMManager:
    """
    Manages the active LLM client.

    Provider priority follows the blueprint (§4.3):
      Claude 3.5 Sonnet → GPT-4o → Gemini 3.8 Flash
    """

    _instance = None
    _llm = None
    _provider: str | None = None
    _model_name: str | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _initialize(self):
        """
        Lazy initialisation — tries providers in blueprint-defined order.
        Raises RuntimeError if no API key is configured.
        """
        if self._llm is not None:
            return

        settings = get_settings()

        # ── 1. Anthropic Claude 3.5 Sonnet (blueprint primary, HIPAA BAA) ──
        if not settings.google_api_key and settings.anthropic_api_key:
            try:
                from langchain_anthropic import ChatAnthropic

                self._llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    anthropic_api_key=settings.anthropic_api_key,
                    temperature=0.1,
                    max_tokens=4096,
                    timeout=60,
                )
                self._provider = "anthropic"
                self._model_name = "claude-3-5-sonnet-20241022"
                logger.info("✅ Anthropic Claude 3.5 Sonnet LLM initialized (primary — blueprint §4.3)")
                return
            except Exception as e:
                logger.warning(f"Anthropic init failed: {e}. Falling back to next provider.")

        # ── 2. OpenAI GPT-4o (blueprint alternative, HIPAA BAA) ─────────────
        if not settings.google_api_key and settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI

                self._llm = ChatOpenAI(
                    model="gpt-4o",
                    api_key=settings.openai_api_key,
                    temperature=0.1,
                    max_tokens=4096,
                    timeout=60,
                )
                self._provider = "openai"
                self._model_name = "gpt-4o"
                logger.info("✅ OpenAI GPT-4o LLM initialized (blueprint §4.3 alternative)")
                return
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}. Falling back to next provider.")

        # ── 3. Google Gemini 3.8 Flash (free-tier fallback) ─────────────────
        if settings.google_api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from google.genai.types import HarmCategory, HarmBlockThreshold

                self._llm = ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    google_api_key=settings.google_api_key,
                    temperature=0.1,
                    max_output_tokens=4096,
                    timeout=60,
                    max_retries=1,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    },
                )
                self._provider = "gemini"
                self._model_name = settings.gemini_model
                logger.info("Configured Google Gemini model: %s", settings.gemini_model)
                logger.info(
                    "✅ Google Gemini 3.8 Flash LLM initialized (fallback — "
                    "NOTE: no HIPAA BAA; use Claude or GPT-4o in production)"
                )
                return
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}.")

        logger.warning(
            "⚠️  No LLM API key found. "
            "Set ANTHROPIC_API_KEY (recommended), OPENAI_API_KEY, or GOOGLE_API_KEY in .env"
        )

    # ── Public properties ────────────────────────────────────────────────────

    @property
    def provider(self) -> str:
        """Which LLM provider is active (e.g. 'anthropic', 'openai', 'gemini')."""
        self._initialize()
        return self._provider or "none"

    @property
    def model_name(self) -> str:
        """The active model identifier string."""
        self._initialize()
        return self._model_name or "unknown"

    @property
    def provider_display(self) -> str:
        """Human-readable provider + model string for dashboards and health checks."""
        self._initialize()
        if self._provider and self._model_name:
            return f"{self._provider}/{self._model_name}"
        return "not configured"

    @property
    def model(self) -> Any:
        """Get the LangChain LLM instance."""
        self._initialize()
        if self._llm is None:
            raise RuntimeError(
                "LLM not initialized. Set ANTHROPIC_API_KEY (recommended for HIPAA), "
                "OPENAI_API_KEY, or GOOGLE_API_KEY in backend/.env"
            )
        return self._llm

    # ── Inference methods ────────────────────────────────────────────────────

    def invoke(self, messages: list) -> str:
        """Invoke the LLM with a list of LangChain messages and return the text content."""
        try:
            response = self.model.invoke(messages)
        except Exception as exc:
            error_text = str(exc)
            if getattr(exc, "status_code", None) == 429 or "429" in error_text:
                raise RuntimeError(
                    "LLM provider quota or rate limit reached (HTTP 429). "
                    "Wait and retry, or configure another provider."
                ) from exc
            if (
                getattr(exc, "status_code", None) == 401
                or "Incorrect API key" in error_text
                or "API key not valid" in error_text
                or "API_KEY_INVALID" in error_text
            ):
                raise RuntimeError(
                    "LLM provider authentication failed (HTTP 401). "
                    "Check the configured API key in backend/.env."
                ) from exc
            if (
                getattr(exc, "status_code", None) in {503, 504}
                or "UNAVAILABLE" in error_text
                or "DEADLINE_EXCEEDED" in error_text
            ):
                raise RuntimeError(
                    "Gemini is temporarily unavailable or timed out. "
                    "Please retry in a moment."
                ) from exc
            raise
        return self._content_to_text(response.content)

    def stream(self, messages: list):
        """Stream LLM response chunks for real-time output."""
        for chunk in self.model.stream(messages):
            text = self._content_to_text(chunk.content)
            if text:
                yield text

    @staticmethod
    def _content_to_text(content: Any) -> str:
        """Normalize LangChain text or structured provider content to plain text."""
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, str):
                    parts.append(block)
                elif isinstance(block, dict):
                    text = block.get("text")
                    if isinstance(text, str):
                        parts.append(text)
                else:
                    text = getattr(block, "text", None)
                    if isinstance(text, str):
                        parts.append(text)
            return "".join(parts)

        return str(content)


@lru_cache()
def get_llm_manager() -> LLMManager:
    """Return the singleton LLM manager."""
    return LLMManager()
