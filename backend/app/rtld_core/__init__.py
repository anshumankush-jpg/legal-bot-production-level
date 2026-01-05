"""
RTLD Core Module - Multi-modal embedding and retrieval system
"""

from .schemas import (
    Chunk,
    SearchResult,
    IngestResult,
    OffenceExtractionResult
)

# Core components
from .vector_search_engine import RTLDVectorSearchEngine, get_vector_search_engine
from .vector_search_db import FAISSVectorSearchDatabase, get_vector_search_db

# Ingestion components
from .ingestion.ingest import RTLDIngestionPipeline, get_ingestion_pipeline
from .ingestion.embeddings import RTLDTextEmbeddingModel, get_embedding_model, EmbeddingService
from .ingestion.chunking import TextChunker, chunk_document_text
from .ingestion.parsers import DocumentParser, parse_document
from .ingestion.ocr import OCRProcessor, OffenceNumberExtractor, extract_offence_number, get_ocr_processor, get_offence_extractor

# Interfaces
from .schemas import IngestionPipeline

__all__ = [
    # Schemas
    'Chunk',
    'SearchResult',
    'IngestResult',
    'OffenceExtractionResult',

    # Core components
    'RTLDVectorSearchEngine',
    'get_vector_search_engine',
    'FAISSVectorSearchDatabase',
    'get_vector_search_db',

    # Ingestion components
    'RTLDIngestionPipeline',
    'get_ingestion_pipeline',
    'RTLDTextEmbeddingModel',
    'get_embedding_model',
    'EmbeddingService',
    'TextChunker',
    'chunk_document_text',
    'DocumentParser',
    'parse_document',
    'OCRProcessor',
    'OffenceNumberExtractor',
    'extract_offence_number',
    'get_ocr_processor',
    'get_offence_extractor',

    # Interfaces
    'IngestionPipeline'
]