"""Embedding service for text vectorization using OpenAI, Azure OpenAI, or Sentence Transformers."""
import numpy as np
from typing import List, Optional, Dict, Tuple
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")

# Try to import RTLD service
try:
    from app.embeddings.rtld_service import get_rtld_service, RTLDService
    RTLD_AVAILABLE = True
except ImportError:
    RTLD_AVAILABLE = False
    logger.warning("RTLD service not available. RTLD embedding provider disabled.")


class EmbeddingService:
    """Service for generating embeddings using OpenAI, Azure OpenAI, or Sentence Transformers."""
    
    def __init__(self):
        """Initialize embedding service."""
        self.embedding_provider = settings.EMBEDDING_PROVIDER
        self.embedding_dimension = settings.EMBEDDING_DIMENSIONS

        # Initialize RTLD service if selected
        self.rtld_service = None
        if self.embedding_provider == "rtld":
            if not RTLD_AVAILABLE:
                raise ImportError(
                    "RTLD service not available. Make sure rtld_service.py is properly imported."
                )
            logger.info("Initializing RTLD embedding service")
            self.rtld_service = get_rtld_service()
            self.embedding_dimension = self.rtld_service.embedding_dim
            # Update settings for consistency
            settings.EMBEDDING_DIMENSIONS = self.embedding_dimension

        # Initialize Sentence Transformer if selected
        self.sentence_model = None
        if self.embedding_provider == "sentence_transformers":
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError(
                    "sentence-transformers not installed. Install with: pip install sentence-transformers"
                )
            model_name = settings.SENTENCE_TRANSFORMER_MODEL
            logger.info(f"Loading Sentence Transformer model: {model_name}")
            self.sentence_model = SentenceTransformer(model_name)
            # Get actual dimension from model
            self.embedding_dimension = self.sentence_model.get_sentence_embedding_dimension()
            logger.info(f"Sentence Transformer dimension: {self.embedding_dimension}")
            # Update settings for consistency
            settings.EMBEDDING_DIMENSIONS = self.embedding_dimension
    
    def embed_texts(
        self,
        texts: List[str],
        organization: Optional[str] = None,
        subject: Optional[str] = None
    ) -> np.ndarray:
        """
        Generate embeddings for texts using OpenAI or Azure OpenAI.
        
        Args:
            texts: List of text strings to embed
            organization: Optional organization name for content formatting
            subject: Optional subject for content formatting
            
        Returns:
            numpy array of shape (N, D)
        """
        if not texts:
            return np.array([], dtype=np.float32).reshape(0, self.embedding_dimension)
        
        # Format content if organization/subject provided
        if organization or subject:
            formatted_texts = []
            for text in texts:
                parts = []
                if organization:
                    parts.append(f"Organization: {organization}")
                if subject:
                    parts.append(f"Subject: {subject}")
                parts.append(f"context: {text}")
                formatted_texts.append(", ".join(parts))
            texts = formatted_texts
        
        # Get embeddings based on provider
        if self.embedding_provider == "rtld":
            # Use RTLD service (multi-modal, unified embeddings)
            if self.rtld_service is None:
                raise RuntimeError("RTLD service not initialized")
            vectors, _ = self.rtld_service.embed_text(texts)
        elif self.embedding_provider == "sentence_transformers":
            # Use Sentence Transformers (local, free, fast)
            if self.sentence_model is None:
                raise RuntimeError("Sentence Transformer model not initialized")
            vectors = self.sentence_model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True  # Normalize for cosine similarity
            )
            vectors = np.array(vectors, dtype=np.float32)
        else:
            # Use OpenAI or Azure OpenAI
            from app.core.openai_client_unified import get_embeddings
            vectors = get_embeddings(texts)
        
        logger.info(f"Generated {len(texts)} embeddings with dimension {vectors.shape[1]} using {self.embedding_provider}")
        return vectors
    
    def embed_text(
        self,
        text: str,
        organization: Optional[str] = None,
        subject: Optional[str] = None
    ) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed
            organization: Optional organization name
            subject: Optional subject

        Returns:
            numpy array of shape (1, D)
        """
        return self.embed_texts([text], organization=organization, subject=subject)

    def embed_file(
        self,
        file_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Generate embeddings for a file (document, image, table, etc.)

        Args:
            file_path: Path to the file
            content_type: Type of content ('text', 'image', 'table', 'document', 'auto')
            metadata: Additional metadata

        Returns:
            Tuple of (embeddings array, chunk texts, chunk ids)
        """
        if self.embedding_provider != "rtld":
            raise NotImplementedError("File embedding is only supported with RTLD provider")

        if self.rtld_service is None:
            raise RuntimeError("RTLD service not initialized")

        from app.embeddings.rtld_service import EmbeddingRequest
        request = EmbeddingRequest(
            file_path=file_path,
            content_type=content_type or "auto",
            metadata=metadata
        )

        response = self.rtld_service.embed(request)
        embeddings = np.array(response.embeddings, dtype=np.float32) if response.embeddings else np.array([], dtype=np.float32).reshape(0, self.embedding_dimension)

        return embeddings, response.chunk_texts, response.chunk_ids

    def embed_image(
        self,
        image_path: str,
        metadata: Optional[Dict] = None
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Generate embeddings for an image

        Args:
            image_path: Path to the image file
            metadata: Additional metadata

        Returns:
            Tuple of (embeddings array, descriptions)
        """
        if self.embedding_provider != "rtld":
            raise NotImplementedError("Image embedding is only supported with RTLD provider")

        if self.rtld_service is None:
            raise RuntimeError("RTLD service not initialized")

        return self.rtld_service.embed_image(image_path)


# Global singleton instance
_embedding_service: Optional['EmbeddingService'] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service

