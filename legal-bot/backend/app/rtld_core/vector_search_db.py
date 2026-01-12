"""
Vector search database implementation using FAISS
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import faiss
import numpy as np

from .schemas import VectorSearchDatabase, SearchResult, Chunk

logger = logging.getLogger(__name__)


class FAISSVectorSearchDatabase(VectorSearchDatabase):
    """
    FAISS-based vector search database
    """

    def __init__(
        self,
        index_dir: str = "./data/rtld_faiss",
        default_dim: int = 384
    ):
        """
        Initialize FAISS vector database

        Args:
            index_dir: Directory to store index files
            default_dim: Default embedding dimension
        """
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.default_dim = default_dim

        # In-memory indices and metadata
        self.indices: Dict[str, faiss.Index] = {}
        self.metadata: Dict[str, List[Dict[str, Any]]] = {}
        self.texts: Dict[str, List[str]] = {}

        # Load existing indices
        self._load_all_indices()

    def ensure_index(self, index_name: str, dim: int) -> None:
        """Ensure an index exists for the given name and dimension"""
        if index_name not in self.indices:
            logger.info(f"Creating new FAISS index: {index_name} (dim={dim})")
            self.indices[index_name] = faiss.IndexFlatIP(dim)
            self.metadata[index_name] = []
            self.texts[index_name] = []

    def upsert_documents(
        self,
        index_name: str,
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """
        Add or update documents in the index

        Args:
            index_name: Name of the index
            vectors: List of embedding vectors
            metadatas: List of metadata dictionaries (must include 'text' field)
        """
        if not vectors:
            return

        # Ensure index exists
        dim = len(vectors[0])
        self.ensure_index(index_name, dim)

        # Convert to numpy array
        vectors_np = np.array(vectors, dtype=np.float32)

        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors_np)

        # Add to FAISS index
        self.indices[index_name].add(vectors_np)

        # Store metadata and texts
        for metadata in metadatas:
            self.metadata[index_name].append(metadata)
            self.texts[index_name].append(metadata.get('text', ''))

        logger.info(f"Added {len(vectors)} vectors to index '{index_name}'")

        # Save to disk
        self._save_index(index_name)

    def query(
        self,
        index_name: str,
        query_vector: List[float],
        k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors

        Args:
            index_name: Name of the index to search
            query_vector: Query embedding vector
            k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of SearchResult objects
        """
        if index_name not in self.indices:
            logger.warning(f"Index '{index_name}' not found")
            return []

        index = self.indices[index_name]
        if index.ntotal == 0:
            return []

        # Convert query to numpy
        query_np = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(query_np)

        # Search
        k_search = min(k, index.ntotal)
        distances, indices = index.search(query_np, k_search)

        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx < 0:  # FAISS returns -1 for invalid results
                continue

            if idx >= len(self.metadata[index_name]):
                logger.warning(f"Index {idx} out of bounds for metadata")
                continue

            # Get metadata and text
            metadata = self.metadata[index_name][idx]
            text = self.texts[index_name][idx]

            # Apply filters if provided
            if filters and not self._matches_filters(metadata, filters):
                continue

            # Create chunk object
            chunk = Chunk(
                id=metadata.get('id', f"{index_name}_{idx}"),
                text=text,
                metadata=metadata,
                source_file=metadata.get('source_file', ''),
                page=metadata.get('page'),
                chunk_index=metadata.get('chunk_index')
            )

            results.append(SearchResult(
                chunk=chunk,
                score=float(score)
            ))

        logger.info(f"Search in '{index_name}' returned {len(results)} results")
        return results

    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches the given filters"""
        for key, value in filters.items():
            if key not in metadata or metadata[key] != value:
                return False
        return True

    def _save_index(self, index_name: str) -> None:
        """Save index and metadata to disk"""
        try:
            # Save FAISS index
            index_path = self.index_dir / f"{index_name}.faiss"
            faiss.write_index(self.indices[index_name], str(index_path))

            # Save metadata
            metadata_path = self.index_dir / f"{index_name}_metadata.jsonl"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                for meta, text in zip(self.metadata[index_name], self.texts[index_name]):
                    record = {
                        'faiss_id': len(self.metadata[index_name]) - 1,  # Approximate
                        'metadata': meta,
                        'text': text
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')

            logger.debug(f"Saved index '{index_name}' to disk")

        except Exception as e:
            logger.error(f"Failed to save index '{index_name}': {e}")

    def _load_index(self, index_name: str) -> None:
        """Load index and metadata from disk"""
        try:
            index_path = self.index_dir / f"{index_name}.faiss"
            metadata_path = self.index_dir / f"{index_name}_metadata.jsonl"

            if index_path.exists() and metadata_path.exists():
                # Load FAISS index
                self.indices[index_name] = faiss.read_index(str(index_path))

                # Load metadata
                self.metadata[index_name] = []
                self.texts[index_name] = []

                with open(metadata_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        record = json.loads(line.strip())
                        self.metadata[index_name].append(record['metadata'])
                        self.texts[index_name].append(record['text'])

                logger.info(f"Loaded index '{index_name}' with {len(self.metadata[index_name])} documents")

        except Exception as e:
            logger.error(f"Failed to load index '{index_name}': {e}")

    def _load_all_indices(self) -> None:
        """Load all available indices from disk"""
        if not self.index_dir.exists():
            return

        # Find all .faiss files
        faiss_files = list(self.index_dir.glob("*.faiss"))
        for faiss_file in faiss_files:
            index_name = faiss_file.stem  # Remove .faiss extension
            self._load_index(index_name)

    def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Get statistics about an index"""
        if index_name not in self.indices:
            return {'error': f"Index '{index_name}' not found"}

        index = self.indices[index_name]
        return {
            'total_vectors': index.ntotal,
            'dimension': index.d,
            'index_type': type(index).__name__
        }


# Global instance
_vector_db: Optional[FAISSVectorSearchDatabase] = None


def get_vector_search_db() -> FAISSVectorSearchDatabase:
    """Get or create the global vector search database instance"""
    global _vector_db
    if _vector_db is None:
        _vector_db = FAISSVectorSearchDatabase()
    return _vector_db