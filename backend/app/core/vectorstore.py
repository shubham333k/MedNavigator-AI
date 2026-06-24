"""
ChromaDB vector store integration.
Manages collections, document insertion, and semantic search.
"""

import logging
from typing import List, Optional, Dict, Any
from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma

from app.config import get_settings
from app.core.embeddings import get_embedding_manager

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages ChromaDB vector store operations."""

    _instance = None
    _client = None
    _collection = None
    _langchain_store = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_client(self) -> chromadb.ClientAPI:
        """Get or create ChromaDB client."""
        if self._client is None:
            settings = get_settings()
            try:
                # Try connecting to ChromaDB server (Docker)
                self._client = chromadb.HttpClient(
                    host=settings.chroma_host,
                    port=settings.chroma_port,
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
                self._client.heartbeat()
                logger.info(f"Connected to ChromaDB server at {settings.chroma_host}:{settings.chroma_port}")
            except Exception:
                # Fallback to persistent local storage
                logger.info("ChromaDB server not available, using local persistent storage")
                self._client = chromadb.PersistentClient(
                    path=settings.chroma_data_path if hasattr(settings, 'chroma_data_path') else "./chroma_data",
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
        return self._client

    def _get_collection(self):
        """Get or create the medical knowledge collection."""
        if self._collection is None:
            settings = get_settings()
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=settings.chroma_collection,
                metadata={"description": "Medical knowledge base for RAG"},
            )
        return self._collection

    def get_langchain_store(self) -> Chroma:
        """Get LangChain-compatible Chroma store for RAG chains."""
        if self._langchain_store is None:
            settings = get_settings()
            embedding_manager = get_embedding_manager()

            try:
                self._langchain_store = Chroma(
                    client=self._get_client(),
                    collection_name=settings.chroma_collection,
                    embedding_function=embedding_manager.model,
                )
            except Exception as e:
                logger.warning(f"Failed to connect to ChromaDB server: {e}")
                self._langchain_store = Chroma(
                    persist_directory=settings.chroma_data_path if hasattr(settings, 'chroma_data_path') else "./chroma_data",
                    collection_name=settings.chroma_collection,
                    embedding_function=embedding_manager.model,
                )

        return self._langchain_store

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> int:
        """Add documents to the vector store."""
        embedding_manager = get_embedding_manager()
        embeddings = embedding_manager.embed_documents(texts)

        collection = self._get_collection()
        collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

        logger.info(f"Added {len(texts)} documents to vector store")
        return len(texts)

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Perform semantic search."""
        embedding_manager = get_embedding_manager()
        query_embedding = embedding_manager.embed_query(query)

        collection = self._get_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        return results

    def count(self) -> int:
        """Get the total number of documents in the collection."""
        try:
            collection = self._get_collection()
            return collection.count()
        except Exception:
            return 0

    def delete_collection(self):
        """Delete the entire collection (use with caution)."""
        settings = get_settings()
        client = self._get_client()
        try:
            client.delete_collection(settings.chroma_collection)
            self._collection = None
            self._langchain_store = None
            logger.info(f"Deleted collection: {settings.chroma_collection}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")


@lru_cache()
def get_vectorstore() -> VectorStoreManager:
    """Get singleton vector store manager."""
    return VectorStoreManager()
