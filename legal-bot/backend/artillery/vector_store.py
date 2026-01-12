"""
Artillery FAISS Vector Store for PLAZA-AI
Handles vector storage, search, and persistence with GCS integration
"""

import os
import json
import pickle
import logging
from typing import List, Dict, Optional, Any
import numpy as np
import faiss

# GCP imports (optional)
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ArtilleryVectorStore:
    """
    Artillery FAISS Vector Store for PLAZA-AI.

    Features:
    - FAISS IndexFlatIP for exact cosine similarity search
    - In-memory FAISS index with disk/GCS persistence
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
        description: str = "artillery_legal_documents"
    ):
        """
        Initialize Artillery vector store.

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
        self.index_path = index_path or f"./data/{description}_index.bin"
        self.metadata_path = metadata_path or f"./data/{description}_metadata.pkl"

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

        logger.info(f"🗄️ Artillery Vector Store initialized: {dimension}D, {self.ntotal} vectors")

    @property
    def ntotal(self) -> int:
        """Get total number of vectors in index."""
        return self.index.ntotal

    def add_vectors(
        self,
        embeddings: np.ndarray,
        metadata_list: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add vectors and metadata to the index.

        Args:
            embeddings: Numpy array of shape (n, dimension)
            metadata_list: List of metadata dicts for each vector

        Returns:
            List of chunk IDs added
        """
        if len(embeddings) != len(metadata_list):
            raise ValueError("Number of embeddings must match number of metadata entries")

        if len(embeddings) == 0:
            return []

        # Ensure correct dtype and normalization
        embeddings = np.ascontiguousarray(embeddings.astype('float32'))
        faiss.normalize_L2(embeddings)  # Normalize for cosine similarity

        # Add to FAISS index
        start_idx = self.index.ntotal
        self.index.add(embeddings)

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

        logger.info(f"✅ Added {len(embeddings)} vectors to index (total: {self.ntotal})")
        return chunk_ids

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors with optional metadata filtering.

        Args:
            query_embedding: Query vector of shape (dimension,) or (1, dimension)
            k: Number of results to return
            filters: Metadata filters (e.g., {'offence_number': '123456789'})

        Returns:
            List of result dicts with 'score', 'content', 'metadata', 'chunk_id'
        """
        if self.ntotal == 0:
            return []

        # Ensure query vector is correct shape
        query_embedding = np.array(query_embedding, dtype='float32')
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Normalize query for cosine similarity
        faiss.normalize_L2(query_embedding)

        # Search FAISS index (get more results if filtering)
        search_k = min(k * 3, self.ntotal) if filters else k
        distances, indices = self.index.search(query_embedding, search_k)

        # Process results with filtering
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

    def get_chunks_by_doc_id(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.

        Args:
            doc_id: Document ID

        Returns:
            List of chunks with metadata
        """
        chunks = []
        for metadata in self.metadata:
            if metadata.get('doc_id') == doc_id:
                chunk_id = metadata.get('chunk_id')
                chunks.append({
                    'chunk_id': chunk_id,
                    'content': metadata.get('content', ''),
                    'metadata': metadata
                })

        return chunks

    def delete_document(self, doc_id: str) -> int:
        """
        Mark all chunks of a document as deleted.

        Args:
            doc_id: Document ID to delete

        Returns:
            Number of chunks marked as deleted
        """
        deleted_count = 0
        for metadata in self.metadata:
            if metadata.get('doc_id') == doc_id:
                chunk_id = metadata.get('chunk_id')
                if self.update_metadata(chunk_id, {'deleted': True}):
                    deleted_count += 1

        logger.info(f"🗑️ Marked {deleted_count} chunks as deleted for doc {doc_id}")
        return deleted_count

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        # Calculate document statistics
        doc_ids = set()
        provinces = set()
        offence_numbers = set()

        for metadata in self.metadata:
            if not metadata.get('deleted', False):
                doc_ids.add(metadata.get('doc_id', ''))
                if metadata.get('province'):
                    provinces.add(metadata['province'])
                if metadata.get('offence_number'):
                    offence_numbers.add(metadata['offence_number'])

        return {
            'total_vectors': self.ntotal,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__,
            'description': self.description,
            'gcs_enabled': self.gcs_available,
            'total_documents': len(doc_ids),
            'total_provinces': len(provinces),
            'total_offence_numbers': len(offence_numbers),
            'provinces': sorted(list(provinces)),
            'metadata_entries': len(self.metadata)
        }

    def save(self) -> bool:
        """
        Save index and metadata (to disk or GCS).

        Returns:
            True if save was successful
        """
        try:
            if self.gcs_available:
                # Save to GCS
                storage_client = storage.Client()
                bucket = storage_client.bucket(self.gcs_bucket)

                # Save FAISS index
                blob = bucket.blob(self.gcs_index_path)
                with open(self.index_path, 'wb') as f:
                    faiss.write_index(self.index, f)
                blob.upload_from_filename(self.index_path)

                # Save metadata
                blob = bucket.blob(self.gcs_metadata_path)
                with open(self.metadata_path, 'wb') as f:
                    pickle.dump({
                        'metadata': self.metadata,
                        'id_to_index': self.id_to_index,
                        'next_id': self.next_id,
                        'dimension': self.dimension,
                        'description': self.description
                    }, f)
                blob.upload_from_filename(self.metadata_path)

                logger.info(f"☁️ Saved to GCS: gs://{self.gcs_bucket}")
            else:
                # Save locally
                os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
                faiss.write_index(self.index, self.index_path)

                with open(self.metadata_path, 'wb') as f:
                    pickle.dump({
                        'metadata': self.metadata,
                        'id_to_index': self.id_to_index,
                        'next_id': self.next_id,
                        'dimension': self.dimension,
                        'description': self.description
                    }, f)

                logger.info(f"💾 Saved locally: {self.index_path}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to save index: {e}")
            return False

    def load(self) -> bool:
        """
        Load index and metadata (from disk or GCS).

        Returns:
            True if load was successful
        """
        try:
            # Try GCS first if available
            if self.gcs_available:
                storage_client = storage.Client()
                bucket = storage_client.bucket(self.gcs_bucket)

                # Load index
                index_blob = bucket.blob(self.gcs_index_path)
                if index_blob.exists():
                    index_blob.download_to_filename(self.index_path)
                    self.index = faiss.read_index(self.index_path)

                # Load metadata
                metadata_blob = bucket.blob(self.gcs_metadata_path)
                if metadata_blob.exists():
                    metadata_blob.download_to_filename(self.metadata_path)
                    with open(self.metadata_path, 'rb') as f:
                        data = pickle.load(f)
                        self.metadata = data.get('metadata', [])
                        self.id_to_index = data.get('id_to_index', {})
                        self.next_id = data.get('next_id', self.index.ntotal)

                    logger.info(f"☁️ Loaded from GCS: gs://{self.gcs_bucket}")
                    return True

            # Fall back to local files
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
            logger.error(f"❌ Failed to load index: {e}")
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

            for i, metadata in enumerate(self.metadata):
                if not metadata.get('deleted', False):
                    # Get vector from FAISS index
                    vectors = self.index.get_xb()
                    if i < len(vectors):
                        active_vectors.append(vectors[i])
                        active_metadata.append(metadata)

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
            self.id_to_index = {meta['chunk_id']: i for i, meta in enumerate(active_metadata)}
            self.next_id = len(active_metadata)

            logger.info(f"🔄 Rebuilt index: {self.ntotal} active vectors")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to rebuild index: {e}")
            return False

    def __len__(self) -> int:
        """Get number of vectors in store."""
        return self.ntotal

    def __str__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (f"ArtilleryVectorStore(\n"
                f"  Dimension: {stats['dimension']}\n"
                f"  Vectors: {stats['total_vectors']}\n"
                f"  Documents: {stats['total_documents']}\n"
                f"  Provinces: {stats['total_provinces']}\n"
                f"  Index Type: {stats['index_type']}\n"
                f"  GCS: {stats['gcs_enabled']}\n"
                f")")


# Global store instance
_store_instance = None

def get_artillery_vector_store(
    dimension: int = 384,
    gcs_bucket: Optional[str] = None,
    description: str = "artillery_legal_documents"
) -> ArtilleryVectorStore:
    """Get or create global Artillery vector store instance."""
    global _store_instance
    if _store_instance is None:
        _store_instance = ArtilleryVectorStore(
            dimension=dimension,
            description=description,
            gcs_bucket=gcs_bucket
        )
    return _store_instance