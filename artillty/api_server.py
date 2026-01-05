"""
FastAPI server for PLAZA-AI Artillery Embedding System
Provides REST API endpoints for multi-modal document processing and search
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import tempfile
import os
from pathlib import Path

from rtld_vector_search_engine import get_rtld_search_engine, RTLDVectorSearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PLAZA-AI Artillery API",
    description="Multi-modal embedding and search API for legal documents",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RTLD search engine
search_engine: RTLDVectorSearchEngine = get_rtld_search_engine()


# Pydantic models for API
class DocumentUploadRequest(BaseModel):
    """Request for document upload with optional fields"""
    offence_number: Optional[str] = Field(None, description="Detected offence/ticket number")
    province: Optional[str] = Field(None, description="Canadian province or US state")
    case_id: Optional[str] = Field(None, description="Associated case/matter ID")
    user_id: Optional[str] = Field("default_user", description="User identifier")
    tags: Optional[List[str]] = Field(None, description="Document tags")


class DocumentUploadResponse(BaseModel):
    """Response for document upload"""
    doc_id: str = Field(..., description="Unique document identifier")
    chunks_indexed: int = Field(..., description="Number of chunks created and indexed")
    detected_offence_number: Optional[str] = Field(None, description="Auto-detected offence number")
    detected_province: Optional[str] = Field(None, description="Auto-detected province/state")
    index_name: str = Field("legal_documents", description="Index name")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    processing_time_seconds: float = Field(..., description="Processing time")
    message: str = Field("Document processed successfully", description="Status message")


class ChatRequest(BaseModel):
    """Enhanced chat request with legal document search"""
    message: str = Field(..., description="User's legal question or query")
    offence_number: Optional[str] = Field(None, description="Filter by offence number")
    province: Optional[str] = Field(None, description="Filter by province/state")
    doc_ids: Optional[List[str]] = Field(None, description="Specific document IDs to search")
    max_results: int = Field(10, description="Maximum number of results to retrieve")
    include_metadata: bool = Field(True, description="Include full metadata in response")


class SearchResult(BaseModel):
    """Individual search result"""
    score: float = Field(..., description="Similarity score (0-1)")
    content: str = Field(..., description="Document chunk content")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata")
    chunk_id: str = Field(..., description="Unique chunk identifier")


class SearchResponse(BaseModel):
    """Response for search operations"""
    results: List[SearchResult] = Field(..., description="Search results")
    total_found: int = Field(..., description="Total results found")
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")
    filters_applied: Dict[str, Any] = Field(..., description="Applied filters")


class ChatResponse(BaseModel):
    """Response for chat queries"""
    answer: str = Field(..., description="AI-generated response")
    citations: List[Dict[str, Any]] = Field(..., description="Source citations")
    chunks_used: int = Field(..., description="Number of chunks used for response")
    confidence: float = Field(..., description="Response confidence score")
    search_results: List[SearchResult] = Field(..., description="Raw search results")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field("healthy", description="Service status")
    version: str = Field("1.0.0", description="API version")
    faiss_index_size: int = Field(..., description="Number of vectors in FAISS index")
    embedding_service_status: str = Field(..., description="Embedding service status")
    document_processor_status: str = Field(..., description="Document processor status")


# API Endpoints

@app.post("/api/artillery/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    offence_number: Optional[str] = Query(None, description="Override detected offence number"),
    province: Optional[str] = Query(None, description="Override detected province"),
    user_id: str = Query("default_user", description="User identifier")
):
    """
    Upload and process a document for embedding and search.

    Supports: PDF, DOCX, XLSX, images (with OCR), text files
    """
    import time
    start_time = time.time()

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Validate file size (50MB limit)
    file_size_limit = 50 * 1024 * 1024  # 50MB
    if hasattr(file, 'size') and file.size > file_size_limit:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
        try:
            # Write uploaded file to temp location
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()
            temp_path = tmp_file.name

            logger.info(f"📄 Processing upload: {file.filename} ({len(content)} bytes)")

            # Process document
            doc_result = search_engine.add_document(
                file_path=temp_path,
                user_id=user_id
            )

            # Override detected values if provided
            if offence_number:
                doc_result['detected_offence_number'] = offence_number
            if province:
                doc_result['detected_province'] = province

            # Prepare response
            response = DocumentUploadResponse(
                doc_id=doc_result['doc_id'],
                chunks_indexed=doc_result['total_chunks'],
                detected_offence_number=doc_result.get('detected_offence_number'),
                detected_province=doc_result.get('detected_province'),
                index_name="legal_documents",
                filename=file.filename,
                file_size=len(content),
                processing_time_seconds=time.time() - start_time,
                message=f"Successfully processed {file.filename} with {doc_result['total_chunks']} chunks"
            )

            logger.info(f"✅ Document uploaded: {response.doc_id} ({response.chunks_indexed} chunks)")
            return response

        except Exception as e:
            logger.error(f"❌ Upload failed: {e}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


@app.post("/api/artillery/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """
    Chat with legal documents using RAG (Retrieval-Augmented Generation).

    Searches for relevant document chunks and provides contextual answers.
    """
    import time
    start_time = time.time()

    try:
        logger.info(f"💬 Chat query: {request.message[:100]}...")

        # Prepare search filters
        filters = {}
        if request.offence_number:
            filters['offence_number'] = request.offence_number
        if request.province:
            filters['province'] = request.province
        if request.doc_ids:
            # For simplicity, we'll search all and filter later
            # In production, you might want to implement document-specific search
            pass

        # Search for relevant chunks
        search_results = search_engine.search(
            query=request.message,
            k=request.max_results,
            filters=filters if filters else None
        )

        # Prepare citations
        citations = []
        relevant_chunks = []

        for result in search_results[:5]:  # Use top 5 for response
            citations.append({
                'doc_id': result['metadata'].get('doc_id'),
                'chunk_index': result['metadata'].get('chunk_index'),
                'score': result['score'],
                'content_preview': result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
            })
            relevant_chunks.append(result['content'])

        # Generate RAG response (simplified - in production you'd use an LLM)
        # For now, we'll provide a structured response based on retrieved chunks
        if relevant_chunks:
            # Simple response generation - concatenate relevant chunks
            context = "\n\n".join(relevant_chunks[:3])  # Use top 3 chunks

            # Basic answer generation (replace with actual LLM in production)
            answer = f"Based on the legal documents, here's relevant information:\n\n{context[:1000]}"

            if len(context) > 1000:
                answer += "\n\n[...content truncated for brevity...]"

            # Add legal disclaimer
            answer += "\n\n⚠️ **Legal Disclaimer**: This is for informational purposes only and does not constitute legal advice. Please consult with a qualified legal professional for your specific situation."

            confidence = min(0.9, sum(r['score'] for r in search_results[:3]) / 3)  # Average top 3 scores

        else:
            answer = ("I couldn't find specific information related to your query in the uploaded documents. "
                     "Please ensure relevant legal documents have been uploaded and try rephrasing your question.")
            confidence = 0.0

        # Prepare search results for response
        search_result_objects = [
            SearchResult(
                score=result['score'],
                content=result['content'],
                metadata=result['metadata'],
                chunk_id=result['chunk_id']
            )
            for result in search_results
        ]

        response = ChatResponse(
            answer=answer,
            citations=citations,
            chunks_used=len(relevant_chunks),
            confidence=confidence,
            search_results=search_result_objects
        )

        logger.info(f"✅ Chat response generated ({len(citations)} citations, {response.confidence:.2f} confidence)")
        return response

    except Exception as e:
        logger.error(f"❌ Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.post("/api/artillery/search", response_model=SearchResponse)
async def search_documents(
    query: str = Body(..., description="Search query text"),
    k: int = Body(10, description="Number of results to return"),
    offence_number: Optional[str] = Body(None, description="Filter by offence number"),
    province: Optional[str] = Body(None, description="Filter by province/state"),
    score_threshold: float = Body(0.0, description="Minimum similarity score"),
    include_metadata: bool = Body(True, description="Include full metadata")
):
    """
    Vector similarity search across legal documents.

    Returns semantically similar document chunks based on the query.
    """
    import time
    start_time = time.time()

    try:
        logger.info(f"🔍 Search query: {query[:50]}... (k={k})")

        # Prepare filters
        filters = {}
        if offence_number:
            filters['offence_number'] = offence_number
        if province:
            filters['province'] = province

        # Perform search with reranking
        search_results = search_engine.search_with_reranking(
            query=query,
            k=k,
            filters=filters if filters else None
        )

        # Apply score threshold
        filtered_results = [
            result for result in search_results
            if result['score'] >= score_threshold
        ]

        # Prepare response objects
        result_objects = []
        for result in filtered_results:
            result_obj = SearchResult(
                score=result['score'],
                content=result['content'],
                chunk_id=result['chunk_id'],
                metadata=result['metadata'] if include_metadata else {}
            )
            result_objects.append(result_obj)

        response = SearchResponse(
            results=result_objects,
            total_found=len(filtered_results),
            query_time_ms=(time.time() - start_time) * 1000,
            filters_applied=filters
        )

        logger.info(f"✅ Search completed: {len(result_objects)} results in {response.query_time_ms:.1f}ms")
        return response

    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/artillery/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        stats = search_engine.get_stats()

        # Determine embedding service status
        embedding_status = "healthy"
        try:
            embedding_info = search_engine.embedding_service.get_model_info()
            if not embedding_info['clip_model']['available']:
                embedding_status = "degraded (CLIP unavailable)"
        except Exception:
            embedding_status = "error"

        # Determine document processor status
        processor_status = "healthy"
        try:
            processor_info = search_engine.document_processor.get_processor_info()
            if not (processor_info['capabilities']['pdf'] or processor_info['capabilities']['docx']):
                processor_status = "limited (PDF/DOCX unavailable)"
        except Exception:
            processor_status = "error"

        return HealthResponse(
            status="healthy",
            version="1.0.0",
            faiss_index_size=stats['vector_store']['total_vectors'],
            embedding_service_status=embedding_status,
            document_processor_status=processor_status
        )

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/api/artillery/stats")
async def get_system_stats():
    """Get comprehensive system statistics."""
    try:
        stats = search_engine.get_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"❌ Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Stats retrieval failed")


@app.delete("/api/artillery/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and all its chunks from the index."""
    try:
        deleted_count = search_engine.delete_document(doc_id)

        if deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

        return {
            "status": "success",
            "doc_id": doc_id,
            "chunks_deleted": deleted_count,
            "message": f"Marked {deleted_count} chunks as deleted"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Document deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Document deletion failed")


@app.post("/api/artillery/rebuild-index")
async def rebuild_faiss_index():
    """Rebuild the FAISS index (admin operation)."""
    try:
        success = search_engine.rebuild_index()

        if success:
            new_stats = search_engine.get_stats()
            return {
                "status": "success",
                "message": "Index rebuilt successfully",
                "new_stats": new_stats
            }
        else:
            raise HTTPException(status_code=500, detail="Index rebuild failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Index rebuild failed: {e}")
        raise HTTPException(status_code=500, detail="Index rebuild failed")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PLAZA-AI Artillery API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/artillery/upload",
            "chat": "/api/artillery/chat",
            "search": "/api/artillery/search",
            "health": "/api/artillery/health",
            "stats": "/api/artillery/stats"
        },
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)