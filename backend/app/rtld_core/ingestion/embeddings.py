"""Embedding generation for RTLD system."""

import logging
from typing import List, Dict, Any, Optional
from ..schemas import EmbeddingModel
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    """Abstract embedding provider."""

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        raise NotImplementedError

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        results = self.embed_texts([text])
        return results[0] if results else []

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        raise NotImplementedError


class SentenceTransformerProvider(EmbeddingProvider):
    """SentenceTransformer-based embedding provider."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with SentenceTransformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded SentenceTransformer model: {model_name} (dim={self.dimension})")
        except ImportError:
            raise ImportError("sentence-transformers not installed")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using SentenceTransformer."""
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        return embeddings.tolist()

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


class OpenAIProvider(EmbeddingProvider):
    """OpenAI embedding provider."""

    def __init__(self, model_name: str = "text-embedding-ada-002", api_key: Optional[str] = None):
        """Initialize OpenAI provider."""
        self.model_name = model_name
        self.api_key = api_key
        self.dimension = 1536 if "ada" in model_name else 1536  # Default dimension

        if not api_key:
            import os
            self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key required")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI."""
        try:
            from openai import OpenAI
            # Only pass api_key - proxies and other unsupported args are not allowed
            client = OpenAI(api_key=self.api_key)

            response = client.embeddings.create(
                input=texts,
                model=self.model_name
            )

            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            # Return zero embeddings as fallback
            return [[0.0] * self.dimension] * len(texts)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


class EmbeddingService:
    """Unified embedding service supporting multiple providers."""

    def __init__(self, provider: str = "sentence_transformers", **kwargs):
        """Initialize embedding service."""
        self.provider_name = provider

        if provider == "sentence_transformers":
            self.provider = SentenceTransformerProvider(**kwargs)
        elif provider == "openai":
            self.provider = OpenAIProvider(**kwargs)
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")

        logger.info(f"Initialized embedding service with provider: {provider}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return self.provider.embed_texts(texts)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        return self.provider.embed_text(text)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.provider.get_dimension()

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate embeddings for chunk objects."""
        texts = [chunk.get('text', '') for chunk in chunks]
        return self.embed_texts(texts)


class RTLDTextEmbeddingModel(EmbeddingProvider):
    """RTLD text embedding model using SentenceTransformers."""

    def __init__(self, text_model_name: str = "all-MiniLM-L6-v2"):
        """Initialize RTLD text embedding model."""
        self.service = EmbeddingService(provider="sentence_transformers", model_name=text_model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        return self.service.embed_texts(texts)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        return self.service.embed_text(text)

    def get_dimension(self) -> int:
        """Get embedding dimension."""
        return self.service.get_dimension()


# Global instance
_embedding_model: Optional[RTLDTextEmbeddingModel] = None


def get_embedding_model() -> RTLDTextEmbeddingModel:
    """Get or create the global embedding model instance."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = RTLDTextEmbeddingModel()
    return _embedding_model