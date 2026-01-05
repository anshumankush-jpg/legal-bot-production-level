"""
RTLD Vector Search Engine for PLAZA-AI
Integrates multi-modal embeddings with FAISS vector search
"""

import logging
from typing import List, Dict, Optional, Any, Union, Tuple
import numpy as np

from multi_modal_embedding_service import MultiModalEmbeddingService, get_embedding_service
from faiss_vector_store import FAISSVectorStore, get_vector_store
from document_processor import DocumentProcessor, get_document_processor

logger = logging.getLogger(__name__)


class RTLDVectorSearchEngine:
    """
    RTLD (Real-Time Learning Database) Vector Search Engine.

    Combines multi-modal embedding generation with FAISS vector search
    for semantic similarity search across text and images.

    Features:
    - Multi-modal embeddings (text + images in unified 384D space)
    - Document processing with intelligent chunking
    - FAISS vector search with metadata filtering
    - GCS persistence for production deployment
    - Offence number detection and province recognition
    """

    def __init__(
        self,
        embedding_service: Optional[MultiModalEmbeddingService] = None,
        vector_store: Optional[FAISSVectorStore] = None,
        document_processor: Optional[DocumentProcessor] = None,
        auto_save: bool = True
    ):
        """
        Initialize RTLD Vector Search Engine.

        Args:
            embedding_service: Multi-modal embedding service instance
            vector_store: FAISS vector store instance
            document_processor: Document processor instance
            auto_save: Whether to auto-save after operations
        """
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_store = vector_store or get_vector_store()
        self.document_processor = document_processor or get_document_processor()
        self.auto_save = auto_save

        logger.info("🚀 RTLD Vector Search Engine initialized")

    def add_document(
        self,
        file_path: str,
        doc_id: Optional[str] = None,
        user_id: Optional[str] = None,
        content_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Add a document to the search engine.

        Args:
            file_path: Path to document file
            doc_id: Document ID (auto-generated if None)
            user_id: User ID for metadata
            content_type: Type of content ('auto', 'text', 'image', 'table')

        Returns:
            Document processing result with statistics
        """
        logger.info(f"📄 Adding document: {file_path}")

        # Process document
        doc_result = self.document_processor.process_document(
            file_path=file_path,
            doc_id=doc_id,
            user_id=user_id
        )

        # Prepare chunks for embedding
        all_chunks = []
        all_metadata = []

        # Process text chunks
        for chunk in doc_result['text_chunks']:
            all_chunks.append(chunk)
            all_metadata.append(chunk['metadata'])

        # Process tables if any
        for table in doc_result['tables']:
            table_text = f"Table: {table.get('sheet', 'Unknown')}\n"
            for row in table['data'][:10]:  # Limit table rows
                table_text += " | ".join(str(cell) for cell in row) + "\n"

            # Create chunk for table
            table_metadata = doc_result.copy()
            table_metadata.update({
                'chunk_index': len(all_chunks),
                'chunk_id': f"{doc_result['doc_id']}_table_{len(doc_result['tables'])}",
                'content_type': 'table'
            })

            all_chunks.append({
                'content': table_text,
                'metadata': table_metadata
            })
            all_metadata.append(table_metadata)

        # Generate embeddings for all chunks
        if all_chunks:
            logger.info(f"🧮 Generating embeddings for {len(all_chunks)} chunks...")

            # Batch embed text chunks
            texts = [chunk['content'] for chunk in all_chunks]
            embeddings = self.embedding_service.embed_text(texts)

            # Add to vector store
            chunk_ids = self.vector_store.add_vectors(
                vectors=embeddings,
                metadata_list=all_metadata
            )

            doc_result['chunk_ids'] = chunk_ids

        # Auto-save if enabled
        if self.auto_save:
            self.vector_store.save()

        logger.info(f"✅ Added document: {doc_result['doc_id']} with {len(all_chunks)} chunks")
        return doc_result

    def add_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add text content directly to the search engine.

        Args:
            text: Text content to add
            metadata: Additional metadata
            doc_id: Document ID
            user_id: User ID

        Returns:
            Processing result
        """
        # Generate doc_id if not provided
        if not doc_id:
            import uuid
            doc_id = f"text_{uuid.uuid4().hex[:16]}"

        # Prepare metadata
        base_metadata = {
            'doc_id': doc_id,
            'user_id': user_id,
            'content_type': 'text',
            'source': 'direct_text'
        }
        if metadata:
            base_metadata.update(metadata)

        # Chunk the text
        chunks = self.document_processor.chunk_text(text, base_metadata)

        if not chunks:
            return {'doc_id': doc_id, 'chunks_indexed': 0, 'error': 'No content to index'}

        # Generate embeddings
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.embedding_service.embed_text(texts)

        # Add to vector store
        chunk_ids = self.vector_store.add_vectors(
            vectors=embeddings,
            metadata_list=[chunk['metadata'] for chunk in chunks]
        )

        # Auto-save
        if self.auto_save:
            self.vector_store.save()

        return {
            'doc_id': doc_id,
            'chunks_indexed': len(chunks),
            'chunk_ids': chunk_ids,
            'total_characters': len(text)
        }

    def add_image(
        self,
        image_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add image content to the search engine.

        Args:
            image_path: Path to image file
            metadata: Additional metadata
            doc_id: Document ID
            user_id: User ID

        Returns:
            Processing result
        """
        # Generate doc_id if not provided
        if not doc_id:
            import uuid
            doc_id = f"image_{uuid.uuid4().hex[:16]}"

        # Prepare metadata
        base_metadata = {
            'doc_id': doc_id,
            'user_id': user_id,
            'content_type': 'image',
            'source': image_path,
            'file_name': image_path.split('/')[-1] if '/' in image_path else image_path
        }
        if metadata:
            base_metadata.update(metadata)

        # Generate embedding
        embedding = self.embedding_service.embed_image(image_path)

        # Add to vector store
        chunk_ids = self.vector_store.add_vectors(
            vectors=np.array([embedding]),
            metadata_list=[base_metadata]
        )

        # Try OCR to extract text for additional metadata
        try:
            extracted_text = self.document_processor.extract_text_from_image(image_path)
            if extracted_text:
                # Detect offence number from OCR text
                offence_num = self.document_processor.detect_offence_number(extracted_text)
                if offence_num:
                    self.vector_store.update_metadata(chunk_ids[0], {
                        'offence_number': offence_num,
                        'ocr_text': extracted_text[:1000]  # Store first 1000 chars
                    })
        except Exception as e:
            logger.warning(f"OCR processing failed: {e}")

        # Auto-save
        if self.auto_save:
            self.vector_store.save()

        return {
            'doc_id': doc_id,
            'chunks_indexed': 1,
            'chunk_ids': chunk_ids,
            'content_type': 'image'
        }

    def search(
        self,
        query: str,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        content_type: str = "text"
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content.

        Args:
            query: Search query (text or image path)
            k: Number of results to return
            filters: Metadata filters
            content_type: Query content type ('text' or 'image')

        Returns:
            List of search results
        """
        logger.debug(f"🔍 Searching for: {query[:50]}...")

        # Generate query embedding
        if content_type == "text":
            query_embedding = self.embedding_service.embed_text(query)
        elif content_type == "image":
            query_embedding = self.embedding_service.embed_image(query)
        else:
            query_embedding = self.embedding_service.embed_text(query)

        # Search vector store
        results = self.vector_store.search(
            query_vector=query_embedding,
            k=k,
            filters=filters
        )

        logger.debug(f"✅ Found {len(results)} results")
        return results

    def search_with_reranking(
        self,
        query: str,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        rerank_top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search with simple reranking based on metadata relevance.

        Args:
            query: Search query
            k: Final number of results to return
            filters: Metadata filters
            rerank_top_k: Number of initial results to rerank from

        Returns:
            Reranked search results
        """
        # Get more results initially
        initial_results = self.search(query, k=rerank_top_k, filters=filters)

        if not initial_results:
            return []

        # Simple reranking based on metadata quality
        for result in initial_results:
            score_boost = 0.0

            # Boost for exact offence number matches
            if filters and 'offence_number' in filters:
                if result['metadata'].get('offence_number') == filters['offence_number']:
                    score_boost += 0.2

            # Boost for province matches
            if filters and 'province' in filters:
                if result['metadata'].get('province') == filters['province']:
                    score_boost += 0.1

            # Boost for shorter, more relevant chunks
            content_length = len(result['content'])
            if content_length < 1000:  # Prefer concise chunks
                score_boost += 0.05

            result['score'] = min(1.0, result['score'] + score_boost)

        # Re-sort by boosted scores
        initial_results.sort(key=lambda x: x['score'], reverse=True)

        return initial_results[:k]

    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.

        Args:
            doc_id: Document ID

        Returns:
            List of chunks with metadata
        """
        # This is a simplified implementation
        # In production, you might want to query by doc_id more efficiently
        all_chunks = []

        for metadata in self.vector_store.metadata:
            if metadata.get('doc_id') == doc_id and not metadata.get('deleted', False):
                chunk_id = metadata.get('chunk_id')
                vector = self.vector_store.get_vector_by_id(chunk_id)
                if vector is not None:
                    all_chunks.append({
                        'chunk_id': chunk_id,
                        'content': metadata.get('content', ''),
                        'metadata': metadata,
                        'vector_shape': vector.shape
                    })

        return all_chunks

    def delete_document(self, doc_id: str) -> int:
        """
        Mark all chunks of a document as deleted.

        Args:
            doc_id: Document ID to delete

        Returns:
            Number of chunks marked as deleted
        """
        deleted_count = 0
        for metadata in self.vector_store.metadata:
            if metadata.get('doc_id') == doc_id:
                chunk_id = metadata.get('chunk_id')
                if self.vector_store.delete_by_id(chunk_id):
                    deleted_count += 1

        if deleted_count > 0 and self.auto_save:
            self.vector_store.save()

        logger.info(f"🗑️ Marked {deleted_count} chunks as deleted for doc {doc_id}")
        return deleted_count

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        store_stats = self.vector_store.get_stats()
        processor_stats = self.document_processor.get_processor_info()
        embedding_stats = self.embedding_service.get_model_info()

        return {
            'vector_store': store_stats,
            'document_processor': processor_stats,
            'embedding_service': embedding_stats,
            'total_documents': len(set(
                meta.get('doc_id') for meta in self.vector_store.metadata
                if not meta.get('deleted', False)
            )),
            'total_active_chunks': sum(
                1 for meta in self.vector_store.metadata
                if not meta.get('deleted', False)
            )
        }

    def save_index(self) -> bool:
        """Save the vector index and metadata."""
        return self.vector_store.save()

    def load_index(self) -> bool:
        """Load the vector index and metadata."""
        return self.vector_store.load()

    def rebuild_index(self) -> bool:
        """Rebuild the FAISS index (useful after many deletions)."""
        success = self.vector_store.rebuild_index()
        if success and self.auto_save:
            self.vector_store.save()
        return success

    def __str__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (f"RTLDVectorSearchEngine(\n"
                f"  Documents: {stats['total_documents']}\n"
                f"  Active Chunks: {stats['total_active_chunks']}\n"
                f"  Vector Store: {stats['vector_store']['total_vectors']} vectors\n"
                f"  Embedding Dim: {stats['embedding_service']['unified_dimension']}\n"
                f")")


# Global engine instance
_engine_instance = None

def get_rtld_search_engine(
    embedding_service: Optional[MultiModalEmbeddingService] = None,
    vector_store: Optional[FAISSVectorStore] = None,
    document_processor: Optional[DocumentProcessor] = None
) -> RTLDVectorSearchEngine:
    """Get or create global RTLD search engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = RTLDVectorSearchEngine(
            embedding_service=embedding_service,
            vector_store=vector_store,
            document_processor=document_processor
        )
    return _engine_instance