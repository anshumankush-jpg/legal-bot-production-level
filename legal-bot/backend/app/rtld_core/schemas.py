"""
Schemas and data models for RTLD core components
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel
from enum import Enum


class ContentType(str, Enum):
    """Supported content types for ingestion."""
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"
    DOCUMENT = "document"
    AUTO = "auto"


class SearchResult(BaseModel):
    """Result from vector search"""
    id: str
    score: float
    content: str
    metadata: Dict[str, Any]
    chunk_id: Optional[str] = None
    doc_id: Optional[str] = None


class Chunk(BaseModel):
    """Document chunk with metadata"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    doc_id: Optional[str] = None
    page: Optional[int] = None
    chunk_index: Optional[int] = None


class OffenceExtractionResult(BaseModel):
    """Result from offence number extraction"""
    offence_number: Optional[str] = None
    confidence: float = 0.0
    source_text: Optional[str] = None
    extraction_method: str = "none"


class IngestResult(BaseModel):
    """Result from document ingestion"""
    doc_id: str
    chunks: List[Chunk]
    detected_offence_number: Optional[str] = None
    extracted_text: str
    num_chunks: int
    content_type: str
    metadata: Dict[str, Any]


class UploadRequest(BaseModel):
    """Request for document upload"""
    offence_number: Optional[str] = None
    status: Optional[str] = None
    case_id: Optional[str] = None


class UploadResponse(BaseModel):
    """Response from document upload"""
    doc_id: str
    detected_offence_number: Optional[str] = None
    chunks_indexed: int
    index_name: str
    filename: str


class ChatRequest(BaseModel):
    """Request for chat with retrieval"""
    message: str
    offence_number: Optional[str] = None
    status: Optional[str] = None
    doc_ids: Optional[List[str]] = None


class ChatResponse(BaseModel):
    """Response from chat with retrieval"""
    answer: str
    citations: List[Dict[str, Any]]
    offence_number: Optional[str] = None
    status: Optional[str] = None


class DocumentMetadata(BaseModel):
    """Metadata for a document"""
    doc_id: str
    filename: str
    user_id: Optional[str] = None
    case_id: Optional[str] = None
    offence_number: Optional[str] = None
    status: Optional[str] = None
    content_type: str
    num_chunks: int
    uploaded_at: Optional[str] = None


class VectorSearchConfig(BaseModel):
    """Configuration for vector search"""
    index_name: str = "default"
    dimension: int = 384
    max_results: int = 10
    similarity_threshold: float = 0.0


class VectorSearchDatabase:
    """Interface for vector database operations"""

    def upsert_documents(
        self,
        index_name: str,
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """Add or update documents in the vector database"""
        raise NotImplementedError

    def query(
        self,
        index_name: str,
        query_vector: List[float],
        k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Query the vector database"""
        raise NotImplementedError

    def ensure_index(self, index_name: str, dim: int) -> None:
        """Ensure index exists"""
        raise NotImplementedError


class VectorSearchEngine:
    """Interface for vector search operations"""

    def index_documents(self, index_name: str, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        """Index documents with their embeddings"""
        raise NotImplementedError

    def search(
        self,
        index_name: str,
        query: str,
        k: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for similar documents"""
        raise NotImplementedError


class EmbeddingModel:
    """Interface for embedding models"""

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        raise NotImplementedError

    def get_dimension(self) -> int:
        """Get embedding dimension"""
        raise NotImplementedError


class IngestionPipeline:
    """Interface for document ingestion pipeline"""

    def ingest_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: Optional[str] = None,
        user_id: Optional[str] = None,
        case_id: Optional[str] = None
    ) -> IngestResult:
        """Process and ingest a file"""
        raise NotImplementedError