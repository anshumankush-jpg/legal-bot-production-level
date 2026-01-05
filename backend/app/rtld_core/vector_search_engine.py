"""
Vector search engine that combines embedding and retrieval
"""

import logging
from typing import List, Dict, Any, Optional

from .schemas import VectorSearchEngine, Chunk, SearchResult
from .ingestion.embeddings import RTLDTextEmbeddingModel
from .vector_search_db import FAISSVectorSearchDatabase

logger = logging.getLogger(__name__)


class RTLDVectorSearchEngine(VectorSearchEngine):
    """
    RTLD-based vector search engine combining embeddings and FAISS retrieval
    """

    def __init__(
        self,
        default_index_name: str = "documents",
        embedding_model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the vector search engine

        Args:
            default_index_name: Default index name for documents
            embedding_model_name: Name of the embedding model to use
        """
        self.default_index_name = default_index_name
        self.embedding_model = RTLDTextEmbeddingModel(text_model_name=embedding_model_name)
        self.vector_db = FAISSVectorSearchDatabase()

        # Ensure default index exists
        self.vector_db.ensure_index(default_index_name, self.embedding_model.get_dimension())

        logger.info("RTLD Vector Search Engine initialized")

    def index_documents(
        self,
        index_name: str,
        chunks: List[Chunk],
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """
        Index documents with their embeddings

        Args:
            index_name: Name of the index
            chunks: List of document chunks
            embeddings: Pre-computed embeddings (optional)
        """
        if not chunks:
            return

        # Generate embeddings if not provided
        if embeddings is None:
            texts = [chunk.text for chunk in chunks]
            embeddings = self.embedding_model.embed_texts(texts)

        # Prepare metadata
        metadatas = []
        for i, chunk in enumerate(chunks):
            metadata = {
                **chunk.metadata,
                'id': chunk.id,
                'text': chunk.text,
                'source_file': chunk.source_file,
                'page': chunk.page,
                'chunk_index': chunk.chunk_index,
                'embedding_index': i
            }
            metadatas.append(metadata)

        # Index in vector database
        self.vector_db.upsert_documents(index_name, embeddings, metadatas)

        logger.info(f"Indexed {len(chunks)} documents in '{index_name}'")

    def search(
        self,
        query: str,
        k: int = 10,
        index_name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Search for relevant chunks

        Args:
            query: Search query string
            k: Number of results to return
            index_name: Index to search (uses default if None)
            filters: Optional metadata filters

        Returns:
            List of relevant chunks
        """
        if index_name is None:
            index_name = self.default_index_name

        # Embed query
        query_embedding = self.embedding_model.embed_text(query)

        # Search vector database
        search_results = self.vector_db.query(index_name, query_embedding, k, filters)

        # Extract chunks from results
        chunks = [result.chunk for result in search_results]

        logger.info(f"Search for '{query}' returned {len(chunks)} results from '{index_name}'")
        return chunks

    def search_with_scores(
        self,
        query: str,
        k: int = 10,
        index_name: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for relevant chunks with similarity scores

        Args:
            query: Search query string
            k: Number of results to return
            index_name: Index to search (uses default if None)
            filters: Optional metadata filters

        Returns:
            List of SearchResult objects with scores
        """
        if index_name is None:
            index_name = self.default_index_name

        # Embed query
        query_embedding = self.embedding_model.embed_text(query)

        # Search vector database
        return self.vector_db.query(index_name, query_embedding, k, filters)

    def get_index_stats(self, index_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about an index"""
        if index_name is None:
            index_name = self.default_index_name
        return self.vector_db.get_index_stats(index_name)


# Global instance
_vector_search_engine: Optional[RTLDVectorSearchEngine] = None


def get_vector_search_engine() -> RTLDVectorSearchEngine:
    """Get or create the global vector search engine instance"""
    global _vector_search_engine
    if _vector_search_engine is None:
        _vector_search_engine = RTLDVectorSearchEngine()
    return _vector_search_engine