"""
RTLD API endpoints for document upload and enhanced chat with retrieval
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel

# Lazy imports to avoid initialization errors at startup
def _get_ingestion_pipeline():
    from app.rtld_core import get_ingestion_pipeline
    return get_ingestion_pipeline()

def _get_vector_search_engine():
    from app.rtld_core import get_vector_search_engine
    return get_vector_search_engine()

def _extract_offence_number(text: str):
    from app.rtld_core import extract_offence_number
    return extract_offence_number(text)

def _get_legal_llm_client():
    from app.llm_client import get_legal_llm_client
    return get_legal_llm_client()

def _get_legal_rag_builder():
    from app.rag_prompt_builder import get_legal_rag_builder
    return get_legal_rag_builder()

# Import schemas
from app.models.schemas import LegalChatRequest, LegalChatResponse

logger = logging.getLogger(__name__)

# Lazy initialization to avoid startup errors
router = APIRouter(prefix="/api/rtld", tags=["rtld"])

# Don't initialize vector store at import time - only when endpoints are called


class DocumentUploadRequest(BaseModel):
    """Request for document upload with optional fields"""
    offence_number: Optional[str] = None
    status: Optional[str] = None
    case_id: Optional[str] = None
    user_id: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    doc_id: str
    chunks_indexed: int
    detected_offence_number: Optional[str] = None
    index_name: str
    filename: str
    message: str


class EnhancedChatRequest(BaseModel):
    """Enhanced chat request with offence number and document filtering"""
    message: str
    offence_number: Optional[str] = None
    status: Optional[str] = None
    doc_ids: Optional[list[str]] = None
    max_results: int = 8


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    offence_number: Optional[str] = None,
    status: Optional[str] = None,
    case_id: Optional[str] = None,
    user_id: Optional[str] = "default_user"
):
    """
    Upload and index a document using RTLD pipeline

    Supports: PDF, DOCX, images, text files
    Automatically extracts offence numbers via OCR if not provided
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Validate file size (50MB limit)
    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > 50:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {file_size_mb:.1f}MB (max 50MB)"
        )

    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.doc', '.txt', '.md', '.jpg', '.jpeg', '.png']
    file_ext = file.filename.lower().split('.')[-1]
    if f'.{file_ext}' not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    try:
        logger.info(f"Processing upload: {file.filename} ({file_size_mb:.1f}MB)")

        # Get RTLD ingestion pipeline
        ingestion_pipeline = _get_ingestion_pipeline()

        # Process document
        result = ingestion_pipeline.ingest_file(
            file_bytes=file_content,
            filename=file.filename,
            user_id=user_id,
            case_id=case_id
        )

        # Index the document chunks
        search_engine = _get_vector_search_engine()

        # Extract embeddings for chunks
        chunk_texts = [chunk.text for chunk in result.chunks]
        if chunk_texts:
            # Index with RTLD search engine
            search_engine.index_documents(
                index_name="documents",
                chunks=result.chunks
            )

        # Use provided offence number, or detected one, or None
        final_offence_number = offence_number or result.detected_offence_number

        logger.info(f"Document indexed: {file.filename} -> {result.doc_id} ({len(result.chunks)} chunks)")

        return DocumentUploadResponse(
            doc_id=result.doc_id,
            chunks_indexed=len(result.chunks),
            detected_offence_number=result.detected_offence_number,
            index_name="documents",
            filename=file.filename,
            message=f"Document uploaded and indexed successfully. {'Offence number detected: ' + result.detected_offence_number if result.detected_offence_number else ''}"
        )

    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.post("/chat", response_model=LegalChatResponse)
async def enhanced_chat(request: EnhancedChatRequest) -> LegalChatResponse:
    """
    Enhanced chat with RTLD retrieval

    Features:
    - RTLD vector search for relevant document chunks
    - Offence number extraction/validation
    - Document filtering by offence number/status
    - Citations from retrieved documents
    """
    try:
        logger.info(f"Enhanced chat request: '{request.message}' (offence: {request.offence_number})")

        # Check if offence number is needed but missing
        offence_extraction = None
        if not request.offence_number:
            # Try to extract offence number from the message itself
            offence_extraction = _extract_offence_number(request.message)

            if not offence_extraction.offence_number:
                # No offence number found - ask user for it
                return LegalChatResponse(
                    answer="I'd be happy to help with your legal question. However, to provide the most accurate and relevant information, I need your offence number (also called ticket number, notice number, or offence number). This helps me search through the relevant legal documents and statutes.\n\n**What is your offence number?** (You can also upload your ticket/document and I'll try to extract it automatically.)",
                    sources=[],
                    jurisdiction="Unknown",
                    country="Unknown",
                    chunks_used=0,
                    citations=[]
                )

        final_offence_number = request.offence_number or offence_extraction.offence_number

        # Perform RTLD search
        search_engine = _get_vector_search_engine()

        # Build search filters
        filters = {}
        if final_offence_number:
            filters['offence_number'] = final_offence_number

        # Search for relevant chunks
        relevant_chunks = search_engine.search(
            query=request.message,
            k=request.max_results,
            filters=filters if filters else None
        )

        if not relevant_chunks:
            return LegalChatResponse(
                answer="I searched through the legal documents but couldn't find specific information related to your query. This could be because:\n\n1. The offence number or details aren't in our indexed documents yet\n2. The query might need to be more specific\n3. You may need to upload relevant legal documents first\n\nPlease try uploading your ticket or legal document, or provide more specific details about your situation.",
                sources=[],
                jurisdiction="Unknown",
                country="Unknown",
                chunks_used=0,
                citations=[]
            )

        # Build context from retrieved chunks
        context_parts = []
        citations = []

        for i, chunk in enumerate(relevant_chunks):
            # Add chunk content to context
            context_parts.append(f"[Document {i+1}]: {chunk.text}")

            # Build citation
            citation = {
                'source': chunk.metadata.get('source_file', 'Unknown document'),
                'page': chunk.metadata.get('page', 'N/A'),
                'snippet': chunk.text[:200] + '...' if len(chunk.text) > 200 else chunk.text,
                'chunk_id': chunk.id,
                'doc_id': chunk.metadata.get('doc_id', 'Unknown')
            }
            citations.append(citation)

        full_context = "\n\n".join(context_parts)

        # Generate response using LLM
        llm_client = _get_legal_llm_client()
        rag_builder = _get_legal_rag_builder()

        # Build RAG prompt
        rag_prompt = rag_builder.build_prompt(
            question=request.message,
            context=full_context,
            offence_number=final_offence_number,
            jurisdiction="Ontario",  # Default for now
            country="Canada"
        )

        # Get LLM response
        llm_response = llm_client.generate(rag_prompt)

        logger.info(f"Enhanced chat completed: {len(relevant_chunks)} chunks used, {len(citations)} citations")

        return LegalChatResponse(
            answer=llm_response,
            sources=citations,
            jurisdiction="Ontario",  # TODO: detect from content
            country="Canada",
            chunks_used=len(relevant_chunks),
            citations=citations
        )

    except Exception as e:
        logger.error(f"Enhanced chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/documents/search")
async def search_documents(
    query: str,
    offence_number: Optional[str] = None,
    limit: int = 10
):
    """
    Search documents using RTLD vector search

    Returns relevant document chunks with metadata
    """
    try:
        search_engine = _get_vector_search_engine()

        filters = {}
        if offence_number:
            filters['offence_number'] = offence_number

        results = search_engine.search_with_scores(
            query=query,
            k=limit,
            filters=filters if filters else None
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'chunk_id': result.chunk.id,
                'doc_id': result.chunk.metadata.get('doc_id'),
                'score': result.score,
                'text': result.chunk.text,
                'source_file': result.chunk.metadata.get('source_file'),
                'page': result.chunk.metadata.get('page'),
                'offence_number': result.chunk.metadata.get('offence_number')
            })

        return {
            'query': query,
            'total_results': len(formatted_results),
            'results': formatted_results
        }

    except Exception as e:
        logger.error(f"Document search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/stats")
async def get_rtld_stats():
    """Get RTLD system statistics"""
    try:
        search_engine = _get_vector_search_engine()
        stats = search_engine.get_index_stats()

        return {
            'system': 'RTLD',
            'status': 'active',
            'index_stats': stats
        }

    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        return {
            'system': 'RTLD',
            'status': 'error',
            'error': str(e)
        }