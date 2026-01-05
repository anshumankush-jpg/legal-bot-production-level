"""Pinecone vector store implementation."""
import logging
from typing import List, Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

try:
    from pinecone.grpc import PineconeGRPC as Pinecone
    from pinecone import ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not installed. Run: pip install pinecone")


class PineconeVectorStore:
    """Pinecone-based vector store for document embeddings."""
    
    def __init__(self, dimension: int = 1536, api_key: str = None, environment: str = "us-east-1", index_name: str = "legal-docs"):
        """
        Initialize Pinecone vector store.
        
        Args:
            dimension: Embedding dimension (1536 for OpenAI, 384 for sentence-transformers)
            api_key: Pinecone API key
            environment: Pinecone environment/region
            index_name: Name of the Pinecone index
        """
        if not PINECONE_AVAILABLE:
            raise ImportError("Pinecone is not installed. Run: pip install pinecone")
        
        if not api_key:
            raise ValueError("Pinecone API key is required")
        
        self.dimension = dimension
        self.index_name = index_name
        self.environment = environment
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=api_key)
        
        # Create index if it doesn't exist
        self._ensure_index_exists()
        
        # Connect to index
        self.index = self.pc.Index(self.index_name)
        
        logger.info(f"✅ Pinecone initialized: {self.index_name} (dimension: {dimension}, region: {environment})")
    
    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist."""
        try:
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=self.environment
                    )
                )
                # Wait for index to be ready
                time.sleep(5)
                logger.info(f"✅ Index created: {self.index_name}")
            else:
                logger.info(f"Index already exists: {self.index_name}")
        except Exception as e:
            logger.error(f"Error ensuring index exists: {e}")
            raise
    
    def add_documents(
        self,
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to Pinecone.
        
        Args:
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts (must be JSON-serializable)
            ids: Optional list of IDs (will generate if not provided)
            
        Returns:
            List of document IDs
        """
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in range(len(embeddings))]
        
        # Prepare vectors for upsert
        vectors = []
        for id_, embedding, metadata in zip(ids, embeddings, metadatas):
            # Ensure metadata is JSON-serializable
            clean_metadata = self._clean_metadata(metadata)
            vectors.append({
                "id": id_,
                "values": embedding,
                "metadata": clean_metadata
            })
        
        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            try:
                self.index.upsert(vectors=batch)
                logger.info(f"✅ Upserted batch {i//batch_size + 1} ({len(batch)} vectors)")
            except Exception as e:
                logger.error(f"Error upserting batch: {e}")
                raise
        
        logger.info(f"✅ Added {len(vectors)} documents to Pinecone")
        return ids
    
    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Clean metadata to ensure it's JSON-serializable for Pinecone."""
        clean = {}
        for key, value in metadata.items():
            # Pinecone supports: strings, numbers, booleans, lists of strings
            if isinstance(value, (str, int, float, bool)):
                clean[key] = value
            elif isinstance(value, list):
                # Convert list items to strings
                clean[key] = [str(v) for v in value if v is not None]
            elif value is not None:
                # Convert other types to string
                clean[key] = str(value)
        return clean
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of results with metadata and scores
        """
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter_dict,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results.matches:
                formatted_results.append({
                    "id": match.id,
                    "score": float(match.score),
                    "metadata": match.metadata
                })
            
            logger.info(f"Found {len(formatted_results)} results from Pinecone")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []
    
    def delete_all(self):
        """Delete all vectors from the index."""
        try:
            self.index.delete(delete_all=True)
            logger.info("🗑️ Deleted all documents from Pinecone")
        except Exception as e:
            logger.error(f"Error deleting from Pinecone: {e}")
            raise
    
    def delete_by_ids(self, ids: List[str]):
        """Delete specific documents by ID."""
        try:
            self.index.delete(ids=ids)
            logger.info(f"🗑️ Deleted {len(ids)} documents from Pinecone")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_documents": stats.total_vector_count,  # Use total_documents for consistency
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                "total_documents": 0,
                "dimension": self.dimension,
                "error": str(e)
            }
