"""Vector store implementations with automatic selection."""
import logging
from typing import Union

from app.core.config import settings
from app.vector_store.faiss_store import FaissVectorStore as FaissStore

logger = logging.getLogger(__name__)

# Try to import optional vector stores
try:
    from app.vector_store.azure_search_store import AzureSearchVectorStore as AzureStore
    AZURE_SEARCH_AVAILABLE = True
except ImportError:
    AZURE_SEARCH_AVAILABLE = False
    logger.debug("Azure Search not available")

try:
    from app.vector_store.pinecone_store import PineconeVectorStore as PineconeStore
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.debug("Pinecone not available")


# Global singleton instance
_vector_store = None


def get_vector_store(dim: int = None) -> Union[FaissStore, 'AzureStore', 'PineconeStore']:
    """
    Get or create the global vector store instance.
    
    Supports multiple vector stores:
    - FAISS: Local, free, file-based (default)
    - Pinecone: Cloud, free tier available, scalable
    - Azure AI Search: Enterprise, requires Azure subscription
    
    Set VECTOR_STORE in .env to choose: "faiss", "pinecone", or "azure"
    
    Args:
        dim: Vector dimension (optional, defaults to settings.EMBEDDING_DIMENSIONS)
    
    Returns:
        Vector store instance based on configuration
    """
    global _vector_store
    
    if _vector_store is not None:
        return _vector_store
    
    # Use provided dimension or default from settings
    if dim is None:
        dim = settings.EMBEDDING_DIMENSIONS
    
    vector_store_type = settings.VECTOR_STORE.lower()
    
    # Pinecone (cloud, free tier available)
    if vector_store_type == "pinecone":
        if not PINECONE_AVAILABLE:
            logger.error("Pinecone selected but not installed. Run: pip install pinecone-client")
            logger.info("Falling back to FAISS")
            vector_store_type = "faiss"
        elif not settings.PINECONE_API_KEY:
            logger.error("Pinecone selected but PINECONE_API_KEY not set in .env")
            logger.info("Falling back to FAISS")
            vector_store_type = "faiss"
        else:
            logger.info(f"✅ Using Pinecone as vector store (index: {settings.PINECONE_INDEX_NAME})")
            _vector_store = PineconeStore(
                dimension=dim,
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT,
                index_name=settings.PINECONE_INDEX_NAME
            )
            return _vector_store
    
    # Azure AI Search (enterprise)
    elif vector_store_type == "azure":
        if not AZURE_SEARCH_AVAILABLE:
            logger.error("Azure Search selected but not available")
            logger.info("Falling back to FAISS")
            vector_store_type = "faiss"
        elif not settings.USE_AZURE_SEARCH or not settings.AZURE_SEARCH_ENDPOINT:
            logger.error("Azure Search selected but not configured properly")
            logger.info("Falling back to FAISS")
            vector_store_type = "faiss"
        else:
            logger.info("✅ Using Azure AI Search as vector store")
            _vector_store = AzureStore()
            return _vector_store
    
    # FAISS (default - local, free)
    if vector_store_type == "faiss" or _vector_store is None:
        logger.info(f"✅ Using FAISS as vector store (local, dimension: {dim})")
        _vector_store = FaissStore(dim=dim)
    
    return _vector_store
