"""
OpenAI Embedding Fallback for when Sentence Transformers fails
"""
import logging
import numpy as np
from typing import List, Union
from app.core.openai_client_unified import get_openai_client
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService:
    """
    OpenAI Embedding Service as fallback when Sentence Transformers fails.
    Uses OpenAI's text-embedding-ada-002 model.
    """
    
    def __init__(self):
        """Initialize OpenAI embedding service."""
        self.client = get_openai_client()
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.dimension = 1536  # text-embedding-ada-002 dimension
        logger.info(f"OpenAI Embedding Service initialized (model: {self.model}, dim: {self.dimension})")
    
    def embed_text(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Embed text using OpenAI API.
        
        Args:
            texts: Single text string or list of texts
        
        Returns:
            Numpy array of shape (N, 1536) where N is number of texts
        """
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return np.array([]).reshape(0, self.dimension)
        
        try:
            # Call OpenAI embeddings API
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            # Extract embeddings
            embeddings = np.array([d.embedding for d in response.data], dtype=np.float32)
            
            logger.debug(f"✅ OpenAI embeddings generated: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ OpenAI embedding failed: {e}")
            raise
    
    def get_sentence_embedding_dimension(self) -> int:
        """Get embedding dimension."""
        return self.dimension


def get_openai_embedding_service() -> OpenAIEmbeddingService:
    """Get or create OpenAI embedding service instance."""
    return OpenAIEmbeddingService()
