"""
Ingestion pipeline - orchestrates document processing, chunking, embedding, and indexing
"""

import tempfile
import os
from typing import Optional, List
from pathlib import Path
import logging

from ..schemas import IngestionPipeline, IngestResult, Chunk
from .embeddings import RTLDTextEmbeddingModel
from ..vector_search_engine import RTLDVectorSearchEngine
from .ocr import OCRProcessor
from .parsers import RTLDUnifiedParser

logger = logging.getLogger(__name__)


class RTLDIngestionPipeline(IngestionPipeline):
    """Complete ingestion pipeline for RTLD"""

    def __init__(
        self,
        embedding_model: Optional[RTLDTextEmbeddingModel] = None,
        vector_search_engine: Optional[RTLDVectorSearchEngine] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        max_file_size_mb: int = 50
    ):
        self.embedding_model = embedding_model or RTLDTextEmbeddingModel()
        self.vector_search_engine = vector_search_engine or RTLDVectorSearchEngine()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_file_size_mb = max_file_size_mb

        # Initialize processors
        self.content_processor = OCRProcessor()
        self.parser = RTLDUnifiedParser(chunk_size, chunk_overlap)

        logger.info("RTLD Ingestion Pipeline initialized")

    def ingest_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str] = None,
        user_id: Optional[str] = None,
        case_id: Optional[str] = None
    ) -> IngestResult:
        """
        Process and ingest a file end-to-end

        Steps:
        1. Validate file
        2. Extract text and detect offence number
        3. Parse into chunks
        4. Generate embeddings
        5. Index in vector database
        """
        # Validate file
        if len(file_bytes) > self.max_file_size_mb * 1024 * 1024:
            raise ValueError(f"File too large: {len(file_bytes)} bytes > {self.max_file_size_mb}MB")

        # Generate document ID
        doc_id = f"doc_{user_id or 'anon'}_{case_id or 'general'}_{filename.replace('.', '_')}"

        # Save file temporarily
        file_ext = Path(filename).suffix.lower()
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name

        detected_content_type = content_type  # Initialize with provided content_type

        try:
            # Step 1: Extract text and detect offence number
            extracted_text, detected_offence_number = self.content_processor.process_file(tmp_path)

            # Step 2: Parse into chunks
            chunks, detected_content_type = self.parser.parse_file(tmp_path, doc_id, {
                'filename': filename,
                'user_id': user_id,
                'case_id': case_id,
                'detected_offence_number': detected_offence_number,
                'content_type': content_type
            })

            # If no chunks from parser (e.g., PDF/image), create chunks from extracted text
            if not chunks and extracted_text:
                from .parsers import RTLDTextParser
                text_parser = RTLDTextParser(self.chunk_size, self.chunk_overlap)
                chunks = text_parser.parse_text(extracted_text, doc_id, {
                    'filename': filename,
                    'user_id': user_id,
                    'case_id': case_id,
                    'detected_offence_number': detected_offence_number,
                    'content_type': content_type
                })

            # Step 3: Generate embeddings
            if chunks:
                texts_to_embed = [chunk.content for chunk in chunks]
                embeddings = self.embedding_model.embed_texts(texts_to_embed)

                # Step 4: Index in vector database
                self.vector_search_engine.index_documents("documents", chunks, embeddings)

                logger.info(f"Successfully ingested {filename}: {len(chunks)} chunks, offence_number={detected_offence_number}")
            else:
                logger.warning(f"No chunks generated for {filename}")

            return IngestResult(
                doc_id=doc_id,
                chunks=chunks,
                detected_offence_number=detected_offence_number,
                extracted_text=extracted_text,
                num_chunks=len(chunks),
                content_type=content_type or detected_content_type,
                metadata={
                    'filename': filename,
                    'user_id': user_id,
                    'case_id': case_id,
                    'file_size': len(file_bytes),
                    'processing_success': len(chunks) > 0
                }
            )

        finally:
            # Clean up temp file
            try:
                os.unlink(tmp_path)
            except:
                pass


# Global instance
_ingestion_pipeline: Optional[RTLDIngestionPipeline] = None


def get_ingestion_pipeline() -> RTLDIngestionPipeline:
    """Get or create the global ingestion pipeline instance."""
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        _ingestion_pipeline = RTLDIngestionPipeline()
    return _ingestion_pipeline