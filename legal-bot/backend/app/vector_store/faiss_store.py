"""FAISS vector store implementation."""
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
import faiss

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import RTLD service
try:
    from app.embeddings.rtld_service import get_rtld_service
    RTLD_AVAILABLE = True
except ImportError:
    RTLD_AVAILABLE = False


class FaissVectorStore:
    """FAISS-based vector store with metadata management."""

    def __init__(self, dim: int, index_path: Optional[str] = None, metadata_path: Optional[str] = None):
        """
        Initialize FAISS vector store.

        Args:
            dim: Embedding dimension
            index_path: Path to FAISS index file
            metadata_path: Path to metadata JSONL file
        """
        self.dim = dim
        self.index_path = Path(index_path or settings.FAISS_INDEX_PATH)
        self.metadata_path = Path(metadata_path or settings.FAISS_METADATA_PATH)

        # Check if RTLD is being used
        self.use_rtld = settings.EMBEDDING_PROVIDER == "rtld" and RTLD_AVAILABLE
        self.rtld_service = None

        if self.use_rtld:
            # Use RTLD's built-in FAISS index
            self.rtld_service = get_rtld_service()
            self.index = self.rtld_service.index
            self.metadata_store = self.rtld_service.metadata_store
            self.text_store = self.rtld_service.text_store
            self.dim = self.rtld_service.embedding_dim
            logger.info("Using RTLD service for vector storage")
        else:
            # Metadata storage: list of dicts, indexed by FAISS id
            self.metadata_store: List[Dict] = []
            self.text_store: List[str] = []  # Store chunk text by FAISS id

            # Initialize or load index
            if self.index_path.exists() and self.metadata_path.exists():
                self.load()
            else:
                # Create new IndexFlatIP (inner product) for normalized vectors
                self.index = faiss.IndexFlatIP(dim)
                logger.info(f"Created new FAISS index with dimension {dim}")
    
    def add_documents(
        self,
        documents: List[Dict]
    ) -> List[str]:
        """
        Add documents to the index (Azure-compatible interface).
        
        Args:
            documents: List of document dicts with 'vector', 'content', 'id', etc.
            
        Returns:
            List of document IDs
        """
        if not documents:
            return []
        
        # Extract vectors, texts, and metadata
        vectors_list = []
        texts = []
        metadatas = []
        
        for doc in documents:
            # Extract vector
            if 'vector' in doc and doc['vector']:
                vectors_list.append(doc['vector'])
            else:
                # Skip documents without vectors (like parent chunks in parent-child)
                continue
            
            # Extract text
            text = doc.get('content', doc.get('text', ''))
            texts.append(text)
            
            # Extract metadata
            metadata = {
                'id': doc.get('id', ''),
                'source_name': doc.get('source', doc.get('source_name', '')),
                'page': doc.get('page', 0),
                'subject': doc.get('subject', ''),
                'organization': doc.get('organization', ''),
                'parent_id': doc.get('parent_id'),
                'child_id': doc.get('child_id'),
                'is_config': doc.get('is_config', False),
                'source_type': doc.get('source_type', ''),
            }
            # Add all other fields
            metadata.update({k: v for k, v in doc.items() if k not in ['vector', 'content', 'text']})
            metadatas.append(metadata)
        
        if not vectors_list:
            logger.warning("No vectors found in documents, skipping")
            return []
        
        # Convert to numpy array
        vectors = np.array(vectors_list, dtype=np.float32)
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)
        
        # Add using existing method
        ids = self.add_embeddings(vectors, metadatas, texts)
        
        # Return document IDs
        return [metadatas[i].get('id', f'faiss_{ids[i]}') for i in range(len(ids))]
    
    def add_embeddings(
        self,
        vectors: np.ndarray,
        metadatas: List[Dict],
        texts: List[str]
    ) -> List[int]:
        """
        Add embeddings to the index.
        
        Args:
            vectors: numpy array of shape (N, D) - should be L2-normalized
            metadatas: List of metadata dicts (one per vector)
            texts: List of text chunks (one per vector)
            
        Returns:
            List of FAISS IDs for added vectors
        """
        if len(vectors) != len(metadatas) or len(vectors) != len(texts):
            raise ValueError("vectors, metadatas, and texts must have same length")
        
        if vectors.shape[1] != self.dim:
            raise ValueError(f"Vector dimension {vectors.shape[1]} does not match index dimension {self.dim}")
        
        # Add vectors to FAISS index
        self.index.add(vectors)
        
        # Get the IDs (they're sequential starting from current size)
        start_id = len(self.metadata_store)
        ids = list(range(start_id, start_id + len(vectors)))
        
        # Store metadata and texts
        self.metadata_store.extend(metadatas)
        self.text_store.extend(texts)
        
        logger.info(f"Added {len(vectors)} vectors to index (IDs: {ids[0]}-{ids[-1]})")
        return ids
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        search_text: Optional[str] = None,
        filters: Optional[str] = None
    ) -> List[Tuple[float, Dict]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector as list of floats (will be converted to numpy array)
            top_k: Number of results to return
            search_text: Ignored for FAISS (only used for Azure hybrid search)
            filters: Ignored for FAISS (only used for Azure)
            
        Returns:
            List of tuples: (score, document_dict)
        """
        # Convert list to numpy array
        if isinstance(query_vector, list):
            query_vector = np.array([query_vector], dtype=np.float32)
        elif isinstance(query_vector, np.ndarray):
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
        
        if query_vector.shape[1] != self.dim:
            raise ValueError(f"Query dimension {query_vector.shape[1]} does not match index dimension {self.dim}")
        
        if self.index.ntotal == 0:
            logger.warning("Index is empty, returning no results")
            return []
        
        # Normalize query vector for cosine similarity (IndexFlatIP expects normalized vectors)
        faiss.normalize_L2(query_vector)
        
        # Search in FAISS (returns distances and indices)
        # For IndexFlatIP, higher scores = more similar
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_vector, k)
        
        # Build results with metadata and text in Azure-compatible format
        results = []
        for i, (score, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0:  # FAISS returns -1 for invalid results
                continue
            if idx >= len(self.metadata_store):
                logger.warning(f"Index {idx} out of bounds for metadata store")
                continue
            
            metadata = self.metadata_store[idx].copy()
            text = self.text_store[idx]
            
            # Create document dict in Azure-compatible format
            doc = {
                'id': metadata.get('id', f'faiss_{idx}'),
                'content': text,
                'source': metadata.get('source_name', metadata.get('source', 'unknown')),
                'page': metadata.get('page', 0),
                'subject': metadata.get('subject', ''),
                'parent_id': metadata.get('parent_id'),
                'child_id': metadata.get('child_id'),
                'is_config': metadata.get('is_config', False)
            }
            # Add all other metadata fields
            doc.update(metadata)
            
            results.append((float(score), doc))
        
        logger.info(f"Search returned {len(results)} results")
        return results
    
    def save(self):
        """Save index and metadata to disk."""
        if self.use_rtld:
            # Delegate to RTLD service
            self.rtld_service.save_index()
        else:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            logger.info(f"Saved FAISS index to {self.index_path}")

            # Save metadata as JSONL
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                for i, (meta, text) in enumerate(zip(self.metadata_store, self.text_store)):
                    record = {
                        'faiss_id': i,
                        'metadata': meta,
                        'text': text
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')

            logger.info(f"Saved {len(self.metadata_store)} metadata records to {self.metadata_path}")

    def load(self):
        """Load index and metadata from disk."""
        if self.use_rtld:
            # Delegate to RTLD service
            self.rtld_service.load_index()
            # Update local references
            self.index = self.rtld_service.index
            self.metadata_store = self.rtld_service.metadata_store
            self.text_store = self.rtld_service.text_store
            self.dim = self.rtld_service.embedding_dim
        else:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            self.dim = self.index.d
            logger.info(f"Loaded FAISS index from {self.index_path} (dim={self.dim}, size={self.index.ntotal})")

            # Load metadata
            self.metadata_store = []
            self.text_store = []

            if self.metadata_path.exists():
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        record = json.loads(line.strip())
                        self.metadata_store.append(record['metadata'])
                        self.text_store.append(record['text'])

                logger.info(f"Loaded {len(self.metadata_store)} metadata records from {self.metadata_path}")
            else:
                logger.warning(f"Metadata file {self.metadata_path} not found")
    
    def get_stats(self) -> Dict:
        """Get statistics about the index."""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.dim,
            'index_type': type(self.index).__name__
        }


# Global singleton instance
_vector_store: Optional['FaissVectorStore'] = None


def get_vector_store(dim: int = 1536) -> 'FaissVectorStore':
    """Get or create the global vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = FaissVectorStore(dim=dim)
    return _vector_store

