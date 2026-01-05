"""
FAISS Vector Store for PLAZA-AI
Handles vector storage, search, and persistence with GCS integration
"""

import os
import json
import pickle
import tempfile
import logging
from typing import List, Dict, Optional, Any, Tuple, Union
from pathlib import Path
import numpy as np
import faiss

# GCP imports (optional)
try:
    from google.cloud import storage
    from google.cloud import firestore
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """
    FAISS-based vector store for PLAZA-AI.

    Features:
    - IndexFlatIP for exact cosine similarity search
    - In-memory FAISS index with disk persistence
    - GCS integration for cloud storage
    - Metadata management and filtering
    - Batch operations for efficiency
    """

    def __init__(
        self,
        dimension: int = 384,
        index_path: Optional[str] = None,
        metadata_path: Optional[str] = None,
        gcs_bucket: Optional[str] = None,
        gcs_index_path: str = "faiss_index.bin",
        gcs_metadata_path: str = "metadata.pkl",
        description: str = "legal_documents"
    ):
        """
        Initialize FAISS vector store.

        Args:
            dimension: Vector dimension (384 for unified space)
            index_path: Local path for FAISS index
            metadata_path: Local path for metadata
            gcs_bucket: GCS bucket name for cloud persistence
            gcs_index_path: Path in GCS bucket for index
            gcs_metadata_path: Path in GCS bucket for metadata
            description: Description of the index
        """
        self.dimension = dimension
        self.description = description

        # Local paths
        self.index_path = index_path or f"./data/faiss_{description}_index.bin"
        self.metadata_path = metadata_path or f"./data/faiss_{description}_metadata.pkl"

        # GCS configuration
        self.gcs_bucket = gcs_bucket
        self.gcs_index_path = gcs_index_path
        self.gcs_metadata_path = gcs_metadata_path
        self.gcs_available = GCS_AVAILABLE and gcs_bucket is not None

        # Initialize FAISS index (IndexFlatIP for cosine similarity)
        self.index = faiss.IndexFlatIP(dimension)

        # Metadata storage
        self.metadata: List[Dict[str, Any]] = []
        self.id_to_index: Dict[str, int] = {}  # chunk_id -> FAISS index position
        self.next_id = 0

        # Ensure local directories exist
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.metadata_path), exist_ok=True)

        # Load existing index if available
        self.load()

        logger.info(f"🗄️ FAISS Vector Store initialized: {dimension}D, {self.ntotal} vectors")

    @property
    def ntotal(self) -> int:
        """Get total number of vectors in index."""
        return self.index.ntotal

    def _ensure_normalized(self, vectors: np.ndarray) -> np.ndarray:
        """
        Ensure vectors are L2 normalized for cosine similarity.

        Args:
            vectors: Input vectors

        Returns:
            L2 normalized vectors
        """
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1.0, norms)
        return vectors / norms

    def add_vectors(
        self,
        vectors: np.ndarray,
        metadata_list: List[Dict[str, Any]],
        normalize: bool = True
    ) -> List[str]:
        """
        Add vectors to the index.

        Args:
            vectors: Numpy array of shape (n, dimension)
            metadata_list: List of metadata dicts for each vector
            normalize: Whether to L2 normalize vectors

        Returns:
            List of chunk IDs added
        """
        if len(vectors) != len(metadata_list):
            raise ValueError("Number of vectors must match number of metadata entries")

        if len(vectors) == 0:
            return []

        # Ensure correct dtype and contiguity
        vectors = np.ascontiguousarray(vectors.astype('float32'))

        # Normalize for cosine similarity
        if normalize:
            vectors = self._ensure_normalized(vectors)

        # Add to FAISS index
        start_idx = self.index.ntotal
        self.index.add(vectors)

        # Store metadata
        chunk_ids = []
        for i, metadata in enumerate(metadata_list):
            chunk_id = metadata.get('chunk_id', f'chunk_{start_idx + i}')
            chunk_ids.append(chunk_id)

            # Add vector index to metadata
            metadata_copy = metadata.copy()
            metadata_copy['vector_index'] = start_idx + i

            self.metadata.append(metadata_copy)
            self.id_to_index[chunk_id] = start_idx + i

        self.next_id = self.index.ntotal

        logger.info(f"✅ Added {len(vectors)} vectors to index (total: {self.ntotal})")
        return chunk_ids

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        normalize_query: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query vector of shape (dimension,) or (1, dimension)
            k: Number of results to return
            filters: Metadata filters (e.g., {'offence_number': '123456789'})
            normalize_query: Whether to normalize query vector

        Returns:
            List of result dicts with 'score', 'metadata', etc.
        """
        if self.ntotal == 0:
            return []

        # Ensure query vector is correct shape
        query_vector = np.array(query_vector, dtype='float32')
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        elif query_vector.ndim > 2:
            raise ValueError("Query vector must be 1D or 2D")

        # Normalize query for cosine similarity
        if normalize_query:
            query_vector = self._ensure_normalized(query_vector)

        # Search FAISS index
        search_k = min(k * 3, self.ntotal) if filters else k  # Get more for filtering
        distances, indices = self.index.search(query_vector, search_k)

        # Process results
        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for invalid results
                continue

            metadata = self.metadata[idx].copy()

            # Apply filters
            if filters:
                match = True
                for key, value in filters.items():
                    if metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            # Create result
            result = {
                'score': float(score),
                'content': metadata.get('content', ''),
                'metadata': metadata,
                'chunk_id': metadata.get('chunk_id', f'chunk_{idx}')
            }
            results.append(result)

            # Stop when we have enough results
            if len(results) >= k:
                break

        return results

    def get_vector_by_id(self, chunk_id: str) -> Optional[np.ndarray]:
        """
        Get vector by chunk ID.

        Args:
            chunk_id: Chunk ID to retrieve

        Returns:
            Vector as numpy array or None if not found
        """
        if chunk_id not in self.id_to_index:
            return None

        idx = self.id_to_index[chunk_id]

        # Reconstruct vector from FAISS index (for IndexFlatIP)
        # This is a simplified approach - in production you might want to store vectors separately
        if hasattr(self.index, 'get_xb'):  # For some FAISS index types
            vectors = self.index.get_xb()
            if idx < len(vectors):
                return vectors[idx]

        return None

    def get_metadata_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata by chunk ID.

        Args:
            chunk_id: Chunk ID to retrieve

        Returns:
            Metadata dict or None if not found
        """
        if chunk_id not in self.id_to_index:
            return None

        idx = self.id_to_index[chunk_id]
        return self.metadata[idx] if idx < len(self.metadata) else None

    def update_metadata(self, chunk_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update metadata for a chunk.

        Args:
            chunk_id: Chunk ID to update
            updates: Dictionary of updates to apply

        Returns:
            True if update was successful
        """
        if chunk_id not in self.id_to_index:
            return False

        idx = self.id_to_index[chunk_id]
        if idx < len(self.metadata):
            self.metadata[idx].update(updates)
            return True

        return False

    def delete_by_id(self, chunk_id: str) -> bool:
        """
        Delete a vector by chunk ID.

        Note: FAISS doesn't support deletion, so this marks as deleted in metadata.
        For production, consider rebuilding the index periodically.

        Args:
            chunk_id: Chunk ID to delete

        Returns:
            True if marked as deleted
        """
        return self.update_metadata(chunk_id, {'deleted': True})

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            'total_vectors': self.ntotal,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__,
            'description': self.description,
            'gcs_enabled': self.gcs_available,
            'metadata_entries': len(self.metadata)
        }

    def save(self, save_to_gcs: bool = True) -> bool:
        """
        Save index and metadata to disk (and optionally GCS).

        Args:
            save_to_gcs: Whether to also save to GCS

        Returns:
            True if save was successful
        """
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)

            # Save metadata
            metadata_data = {
                'metadata': self.metadata,
                'id_to_index': self.id_to_index,
                'next_id': self.next_id,
                'dimension': self.dimension,
                'description': self.description
            }

            with open(self.metadata_path, 'wb') as f:
                pickle.dump(metadata_data, f)

            logger.info(f"💾 Saved index to {self.index_path}")

            # Save to GCS if enabled
            if save_to_gcs and self.gcs_available:
                self._save_to_gcs()

            return True

        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            return False

    def load(self, load_from_gcs: bool = True) -> bool:
        """
        Load index and metadata from disk (or GCS).

        Args:
            load_from_gcs: Whether to try loading from GCS first

        Returns:
            True if load was successful
        """
        # Try GCS first if enabled
        if load_from_gcs and self.gcs_available:
            if self._load_from_gcs():
                return True

        # Load from local files
        try:
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)

            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data.get('metadata', [])
                    self.id_to_index = data.get('id_to_index', {})
                    self.next_id = data.get('next_id', self.index.ntotal)

            logger.info(f"📂 Loaded index with {self.ntotal} vectors")
            return True

        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False

    def _save_to_gcs(self) -> bool:
        """Save index and metadata to GCS."""
        if not self.gcs_available:
            return False

        try:
            client = storage.Client()
            bucket = client.bucket(self.gcs_bucket)

            # Upload index
            index_blob = bucket.blob(self.gcs_index_path)
            index_blob.upload_from_filename(self.index_path)

            # Upload metadata
            metadata_blob = bucket.blob(self.gcs_metadata_path)
            metadata_blob.upload_from_filename(self.metadata_path)

            logger.info(f"☁️ Saved to GCS: gs://{self.gcs_bucket}")
            return True

        except Exception as e:
            logger.error(f"Failed to save to GCS: {e}")
            return False

    def _load_from_gcs(self) -> bool:
        """Load index and metadata from GCS."""
        if not self.gcs_available:
            return False

        try:
            client = storage.Client()
            bucket = client.bucket(self.gcs_bucket)

            # Download index
            index_blob = bucket.blob(self.gcs_index_path)
            if index_blob.exists():
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    index_blob.download_to_file(tmp)
                    tmp.flush()
                    self.index = faiss.read_index(tmp.name)
                    os.unlink(tmp.name)

            # Download metadata
            metadata_blob = bucket.blob(self.gcs_metadata_path)
            if metadata_blob.exists():
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    metadata_blob.download_to_file(tmp)
                    tmp.flush()
                    with open(tmp.name, 'rb') as f:
                        data = pickle.load(f)
                        self.metadata = data.get('metadata', [])
                        self.id_to_index = data.get('id_to_index', {})
                        self.next_id = data.get('next_id', self.index.ntotal)
                    os.unlink(tmp.name)

            logger.info(f"☁️ Loaded from GCS: gs://{self.gcs_bucket}")
            return True

        except Exception as e:
            logger.error(f"Failed to load from GCS: {e}")
            return False

    def rebuild_index(self) -> bool:
        """
        Rebuild the FAISS index from current metadata.
        Useful after many deletions or for optimization.

        Returns:
            True if rebuild was successful
        """
        try:
            # Collect all active vectors and metadata
            active_vectors = []
            active_metadata = []

            for i, meta in enumerate(self.metadata):
                if not meta.get('deleted', False):
                    # Get vector from FAISS index
                    vectors = self.index.get_xb()
                    if i < len(vectors):
                        active_vectors.append(vectors[i])
                        active_metadata.append(meta)

            if not active_vectors:
                # Create empty index
                self.index = faiss.IndexFlatIP(self.dimension)
                self.metadata = []
                self.id_to_index = {}
                self.next_id = 0
                return True

            # Rebuild index
            vectors_array = np.array(active_vectors, dtype='float32')
            self.index = faiss.IndexFlatIP(self.dimension)
            self.index.add(vectors_array)

            # Update metadata and mappings
            self.metadata = active_metadata
            self.id_to_index = {meta['chunk_id']: i for i, meta in enumerate(active_metadata)}
            self.next_id = len(active_metadata)

            logger.info(f"🔄 Rebuilt index: {self.ntotal} active vectors")
            return True

        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            return False

    def __len__(self) -> int:
        """Get number of vectors in store."""
        return self.ntotal

    def __str__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (f"FAISSVectorStore(\n"
                f"  Dimension: {stats['dimension']}\n"
                f"  Vectors: {stats['total_vectors']}\n"
                f"  Index Type: {stats['index_type']}\n"
                f"  GCS: {stats['gcs_enabled']}\n"
                f"  Description: {stats['description']}\n"
                f")")


# Global store instance
_store_instance = None

def get_vector_store(
    dimension: int = 384,
    description: str = "legal_documents",
    gcs_bucket: Optional[str] = None
) -> FAISSVectorStore:
    """Get or create global vector store instance."""
    global _store_instance
    if _store_instance is None:
        _store_instance = FAISSVectorStore(
            dimension=dimension,
            description=description,
            gcs_bucket=gcs_bucket
        )
    return _store_instance