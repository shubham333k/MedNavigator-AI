"""
Embedding model manager.
Uses a configurable BGE model locally via sentence-transformers.
"""

import logging
from typing import List
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from app.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages the embedding model lifecycle."""

    _instance = None
    _embeddings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _initialize(self):
        """Lazy initialization of the embedding model."""
        if self._embeddings is None:
            settings = get_settings()
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                device = "cpu"

            logger.info(
                "Loading embedding model %s on %s. The first run may download "
                "the model and can take several minutes.",
                settings.embedding_model,
                device,
            )
            self._embeddings = HuggingFaceEmbeddings(
                model_name=settings.embedding_model,
                model_kwargs={"device": device},
                encode_kwargs={
                    "normalize_embeddings": True,
                    "batch_size": 32,
                },
            )
            logger.info("✅ Embedding model loaded successfully")

    @property
    def model(self) -> HuggingFaceEmbeddings:
        """Get the embedding model instance."""
        self._initialize()
        return self._embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        self._initialize()
        return self._embeddings.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        self._initialize()
        return self._embeddings.embed_documents(texts)


@lru_cache()
def get_embedding_manager() -> EmbeddingManager:
    """Get singleton embedding manager."""
    return EmbeddingManager()
