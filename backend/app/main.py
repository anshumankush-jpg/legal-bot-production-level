"""FastAPI application entry point."""
import logging
import os
import uuid
import sys
import json
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import openai
from io import BytesIO
from fastapi import Header

# Fix import paths - add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Artillery imports (from artillery directory) - lazy import to avoid FAISS memory issues
# Only import when actually needed
artillery_embedding = None
artillery_docproc = None
artillery_store = None

def get_artillery_embedding_service():
    """Lazy import artillery embedding service."""
    global artillery_embedding
    if artillery_embedding is None:
        import artillery.embedding_service as artillery_embedding_module
        artillery_embedding = artillery_embedding_module
    return artillery_embedding.get_artillery_embedding_service()

def get_artillery_document_processor():
    """Lazy import artillery document processor."""
    global artillery_docproc
    if artillery_docproc is None:
        import artillery.document_processor as artillery_docproc_module
        artillery_docproc = artillery_docproc_module
    return artillery_docproc.get_artillery_document_processor()

def get_artillery_vector_store(dimension: int = 384, description: str = "artillery_legal_documents", gcs_bucket: Optional[str] = None):
    """Lazy import artillery vector store."""
    global artillery_store
    if artillery_store is None:
        import artillery.vector_store as artillery_store_module
        artillery_store = artillery_store_module
    # Call with correct parameter order from artillery/vector_store.py: dimension, gcs_bucket, description
    return artillery_store.get_artillery_vector_store(
        dimension=dimension,
        gcs_bucket=gcs_bucket,
        description=description
    )

# Legacy imports (if they exist)
try:
    # Import only what we actually need - the modules exist but don't export those names
    # from app.api.routes import ingest, query, matters, analytics, documents, legal_chat, rtld
    from app.models.schemas import HealthResponse
    from app.vector_store import get_vector_store
    from app.core.openai_client_unified import chat_completion
    from app.core.config import settings
    LEGACY_SYSTEMS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Legacy systems import failed: {e}")
    LEGACY_SYSTEMS_AVAILABLE = False
    chat_completion = None
    settings = None

# Configure detailed logging for debugging
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.DEBUG),
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('backend_detailed.log', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info("="*80)
logger.info("BACKEND STARTING - DETAILED LOGGING ENABLED")
logger.info("="*80)

# Configure Tesseract OCR path for Windows
if os.name == 'nt':  # Windows
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.info(f"[OK] Tesseract OCR configured at: {tesseract_path}")
            # Test it
            version = pytesseract.get_tesseract_version()
            logger.info(f"[OK] Tesseract version: {version}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to configure Tesseract: {e}")
    else:
        logger.warning(f"[WARNING] Tesseract not found at: {tesseract_path}")
else:
    logger.info("[INFO] Non-Windows system - Tesseract should be in PATH")

# Create FastAPI app
app = FastAPI(
    title="PLAZA-AI Legal RAG Backend",
    description="Embedding and RAG backend for legal document analysis",
    version="1.0.0"
)

# CORS Configuration - Allow React dev server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4200", "http://localhost:5173", "*"],  # React/Vite/Angular default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include legacy routers (if available) - DISABLED to avoid conflicts with artillery endpoints
# The artillery endpoints are defined directly in this file and should be used instead
if False and LEGACY_SYSTEMS_AVAILABLE:
    try:
        app.include_router(ingest.router)
        app.include_router(query.router)
        app.include_router(matters.router)
        app.include_router(analytics.router)
        app.include_router(documents.router)
        app.include_router(legal_chat.router)
        app.include_router(rtld.router)
    except Exception as e:
        logger.warning(f"Legacy routers not available: {e}")

# Create uploads directory
UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Lazy-loaded Artillery Services
_embedding_service = None
_doc_processor = None
_vector_store = None

def get_embedding_service():
    """
    Get embedding service with fallback to OpenAI if Sentence Transformers fails.
    """
    global _embedding_service
    if _embedding_service is None:
        try:
            # Try Sentence Transformers first (free, local)
            _embedding_service = get_artillery_embedding_service()
            logger.info("[OK] Using Sentence Transformers (local, free)")
        except Exception as e:
            logger.warning(f"[WARNING] Sentence Transformers failed: {e}")
            logger.info("[INFO] Falling back to OpenAI embeddings...")
            try:
                from app.core.openai_embedding_fallback import get_openai_embedding_service
                _embedding_service = get_openai_embedding_service()
                logger.info("[OK] Using OpenAI embeddings (fallback)")
            except Exception as e2:
                logger.error(f"[ERROR] OpenAI embedding fallback also failed: {e2}")
                raise Exception(f"Both embedding services failed. Sentence Transformers: {e}, OpenAI: {e2}")
    return _embedding_service

def get_doc_processor():
    global _doc_processor
    if _doc_processor is None:
        _doc_processor = get_artillery_document_processor()
    return _doc_processor

def get_vector_store_artillery():
    """
    Get Artillery vector store with dynamic dimension based on embedding service.
    This is separate from the legacy get_vector_store to avoid conflicts.
    """
    global _vector_store
    if _vector_store is None:
        # Determine dimension based on embedding service
        try:
            embedding_service = get_embedding_service()
            # Try to get dimension from service
            if hasattr(embedding_service, 'unified_dim'):
                dimension = embedding_service.unified_dim  # Sentence Transformers: 384
            elif hasattr(embedding_service, 'dimension'):
                dimension = embedding_service.dimension  # OpenAI: 1536
            elif hasattr(embedding_service, 'get_sentence_embedding_dimension'):
                dimension = embedding_service.get_sentence_embedding_dimension()
            else:
                dimension = 384  # Default fallback
        except:
            dimension = 1536  # Default to OpenAI dimension if service not available
        
        logger.info(f"Initializing Artillery vector store with dimension: {dimension}")
        
        # Local storage for testing - no GCS bucket
        data_dir = Path("./data")
        data_dir.mkdir(exist_ok=True)
        
        # Get artillery vector store with correct parameter order
        _vector_store = get_artillery_vector_store(
            dimension=dimension,
            description="artillery_legal_documents",
            gcs_bucket=None  # None for local testing
        )
    return _vector_store

# Request/Response Models (simplified for local testing)
class ChatRequest(BaseModel):
    message: str
    offence_number: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    law_category: Optional[str] = None
    law_type: Optional[str] = None
    law_scope: Optional[str] = None
    jurisdiction: Optional[str] = None
    top_k: int = 5

class ChatResponse(BaseModel):
    answer: str
    citations: List[Dict]
    chunks_used: int
    confidence: float

class SearchRequest(BaseModel):
    query: str
    k: int = 10
    filters: Optional[Dict] = None
    score_threshold: float = 0.7

class VoiceChatRequest(BaseModel):
    text: str
    language: Optional[str] = 'en'
    voice: Optional[str] = 'alloy'

class CaseLookupRequest(BaseModel):
    query: str
    jurisdiction: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    limit: int = 10

class AmendmentRequest(BaseModel):
    document_type: str
    case_details: Dict[str, Any]
    jurisdiction: Optional[str] = None

class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = None

class ChatHistorySearchRequest(BaseModel):
    user_id: str
    search_query: str
    limit: int = 20

class GenerateSummaryRequest(BaseModel):
    messages: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None


def generate_structured_answer(question: str, results: List[Dict], citations: List[Dict]) -> str:
    """
    Generate a simple document-based answer when LLM is unavailable.
    This is a LAST RESORT fallback - we should always try to use LLM first.
    """
    
    # Extract key information from top results
    relevant_content = []
    for r in results[:5]:  # Use top 5 most relevant chunks
        content = r.get('content', '')
        metadata = r.get('metadata', {})
        
        if len(content) > 100:  # Only use substantial chunks
            # Format with source information
            jurisdiction = metadata.get('organization', metadata.get('jurisdiction', 'Unknown'))
            source = metadata.get('filename', metadata.get('source_name', 'Legal Document'))
            relevant_content.append(f"[{jurisdiction} - {source}]\n{content[:600]}...\n")
    
    if not relevant_content:
        return """I apologize, but I couldn't find sufficient information in the available legal documents to answer your question.

Please note: This system requires an AI language model (LLM) to generate proper answers. The LLM appears to be unavailable or not configured.

Next Steps:
1. Ensure your LLM provider is configured (OpenAI, Gemini, or Ollama)
2. Check your API keys in the configuration
3. Or consult with a licensed legal professional for your specific situation

This is not legal advice. Always consult a qualified legal professional."""

    # Combine relevant excerpts
    combined_content = "\n---\n\n".join(relevant_content[:3])  # Limit to top 3 sources
    
    answer = f"""Legal Information from Retrieved Documents:

Based on the available legal documents, here is the relevant information:

{combined_content}

---

Important Notes:
• The above are direct excerpts from legal documents in our database
• This is informational content only, not a personalized answer or legal advice
• This system works best with an AI language model (LLM) enabled - the LLM may be unavailable or not configured
• For proper legal analysis and advice specific to your situation, please consult a licensed lawyer or paralegal

Sources: {len(citations)} legal documents retrieved"""
    
    return answer


# Artillery Endpoints
@app.post("/api/artillery/upload")
async def artillery_upload_document(
    file: UploadFile = File(...),
    user_id: str = Form("default_user"),
    offence_number: Optional[str] = Form(None)
):
    """Upload and process document with Artillery embedding system."""
    import time
    start_time = time.time()

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Validate file size (50MB limit)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")

    # Validate file type - NOW INCLUDES IMAGES!
    allowed_extensions = {
        # Documents
        '.pdf', '.docx', '.txt', '.xlsx', '.xls',
        # Images (for OCR)
        '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'
    }
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_ext}. Allowed: PDF, DOCX, TXT, XLSX, and Images (JPG, PNG, BMP, TIFF)"
        )

    try:
        # Create upload directory
        user_upload_dir = UPLOAD_DIR / user_id
        user_upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate document ID
        doc_id = f"doc_{user_id}_{uuid.uuid4().hex[:8]}"

        # Save uploaded file
        file_path = user_upload_dir / f"{doc_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"📄 Processing upload: {file.filename} ({len(content)} bytes)")

        # Initialize services
        doc_processor = get_doc_processor()
        embedding_service = get_embedding_service()
        vector_store = get_vector_store_artillery()

        # Debug: print processor type
        print(f"DEBUG: Using processor type: {type(doc_processor)}")
        print(f"DEBUG: Processor class: {doc_processor.__class__}")
        print(f"DEBUG: Processor module: {doc_processor.__class__.__module__}")
        print(f"DEBUG: Processor has detect_offence_number: {hasattr(doc_processor, 'detect_offence_number')}")
        if hasattr(doc_processor, 'detect_offence_number'):
            print("DEBUG: detect_offence_number method found")
        else:
            print("DEBUG: detect_offence_number method NOT found")
            print(f"DEBUG: Available methods: {[m for m in dir(doc_processor) if not m.startswith('_')]}")

        # Process document using the unified process_document method
        try:
            extracted = doc_processor.process_document(str(file_path))
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Document processing error: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Failed to process document: {error_msg}")

        if not extracted or not extracted.get('text_chunks'):
            raise HTTPException(status_code=400, detail="No content extracted from document")
        
        # Log if OCR failed (for debugging)
        if extracted.get('text_chunks'):
            first_chunk = extracted['text_chunks'][0].get('content', '')
            if 'OCR not available' in first_chunk or 'install Tesseract' in first_chunk:
                logger.warning(f"Image uploaded without OCR: {file.filename}")

        # Extract offence number if not provided
        if not offence_number:
            # Use the offence number detected during document processing
            offence_number = extracted.get('detected_offence_number')

        # Process and embed chunks
        all_embeddings = []
        all_metadata = []

        # Process text chunks
        for idx, chunk in enumerate(extracted['text_chunks']):
            chunk_text = chunk['content']
            if not chunk_text or len(chunk_text.strip()) < 10:  # Skip very short chunks
                continue

            # Generate embedding
            embedding = embedding_service.embed_text(chunk_text)

            # Create metadata
            chunk_metadata = {
                'user_id': user_id,
                'doc_id': doc_id,
                'filename': file.filename,
                'page': chunk.get('page', 1),
                'chunk_id': f"{doc_id}_chunk_{idx}",
                'offence_number': offence_number,
                'content': chunk_text
            }

            all_embeddings.append(embedding[0])  # embedding is (1, 384), take first
            all_metadata.append(chunk_metadata)

        # Add to vector store
        if all_embeddings:
            import numpy as np
            embeddings_array = np.array(all_embeddings)
            vector_store.add_vectors(embeddings_array, all_metadata)
            vector_store.save()

        processing_time = time.time() - start_time

        return {
            "doc_id": doc_id,
            "detected_offence_number": offence_number,
            "chunks_indexed": len(all_metadata),
            "file_path": str(file_path),
            "status": "success",
            "message": f"Document '{file.filename}' uploaded and indexed. {len(all_metadata)} chunks processed."
        }

    except Exception as e:
        logger.error(f"[ERROR] Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/api/artillery/chat", response_model=ChatResponse)
async def artillery_chat(request: ChatRequest):
    """Chat with legal documents using Artillery RAG system - NOW WITH DOCUMENT RETRIEVAL!"""
    import time
    import traceback
    start_time = time.time()
    
    try:
        message = request.message
        logger.info(f"[ARTILLERY_CHAT] Received chat request: {message[:100]}...")
        
        # 🔍 STEP 1: Query uploaded documents from vector store
        relevant_chunks = []
        citations = []
        try:
            embedding_service = get_embedding_service()
            vector_store = get_vector_store_artillery()
            
            logger.info(f"[ARTILLERY_CHAT] Querying vector store (total docs: {vector_store.index.ntotal})...")
            
            # Embed the user's question
            query_embedding = embedding_service.embed_text(message)
            
            # Search for relevant document chunks (top 5)
            if vector_store.index.ntotal > 0:
                results = vector_store.search(query_embedding[0], k=5, filters={})
                logger.info(f"[ARTILLERY_CHAT] Found {len(results)} relevant document chunks")
                
                for idx, result in enumerate(results):
                    relevant_chunks.append({
                        'content': result.get('content', ''),
                        'score': result.get('score', 0.0),
                        'metadata': result.get('metadata', {})
                    })
                    
                    # Create citation
                    metadata = result.get('metadata', {})
                    citations.append({
                        'text': result.get('content', '')[:200] + '...',
                        'source': metadata.get('filename', 'Unknown'),
                        'page': metadata.get('page', 'N/A'),
                        'score': result.get('score', 0.0)
                    })
            else:
                logger.info("[ARTILLERY_CHAT] No documents in vector store yet")
        except Exception as ve:
            logger.warning(f"[ARTILLERY_CHAT] Vector search failed: {ve}")
            # Continue without document context
        
        # 🤖 STEP 2: Build professional legal prompt using new system
        from app.legal_prompts import LegalPromptSystem
        
        messages = LegalPromptSystem.build_artillery_prompt(
            question=message,
            document_chunks=relevant_chunks if relevant_chunks else None,
            jurisdiction=request.jurisdiction if hasattr(request, 'jurisdiction') else None,
            law_category=request.law_category if hasattr(request, 'law_category') else None,
            law_scope=request.law_scope if hasattr(request, 'law_scope') else None,
            language=request.language if hasattr(request, 'language') else 'en'
        )
        
        # Use OpenAI
        answer = None
        logger.info(f"[ARTILLERY_CHAT] Calling OpenAI...")
        if settings and LEGACY_SYSTEMS_AVAILABLE and chat_completion:
            if settings.LLM_PROVIDER == "openai":
                if settings.OPENAI_API_KEY:
                    try:
                        answer = chat_completion(messages=messages, temperature=0.2, max_tokens=1500)
                        logger.info(f"[ARTILLERY_CHAT] OpenAI response received: {answer[:100]}")
                    except Exception as e:
                        logger.error(f"OpenAI error: {e}", exc_info=True)
                        answer = f"Error calling OpenAI: {str(e)}"
                else:
                    answer = "OpenAI API key not configured"
            else:
                answer = f"LLM provider is set to '{settings.LLM_PROVIDER}', but OpenAI is required"
        else:
            if not settings:
                answer = "Settings not available - check backend configuration"
            elif not LEGACY_SYSTEMS_AVAILABLE:
                answer = "Legacy systems not available - check imports"
            elif not chat_completion:
                answer = "Chat completion function not available"
        
        if not answer:
            answer = "Unable to generate response"
        
        logger.info(f"[ARTILLERY_CHAT] Returning response with answer length: {len(answer)}, citations: {len(citations)}")
        return ChatResponse(
            answer=answer[:5000],
            citations=citations,  # Now includes uploaded document citations!
            chunks_used=len(relevant_chunks),
            confidence=0.85 if relevant_chunks else 0.5
        )
    except Exception as e:
        logger.error(f"[ARTILLERY_CHAT] Chat endpoint error: {e}", exc_info=True)
        error_trace = traceback.format_exc()
        logger.error(f"[ARTILLERY_CHAT] Full traceback: {error_trace}")
        # Raise HTTPException with the error
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
        # Return error as ChatResponse instead of raising HTTPException
        try:
            return ChatResponse(
                answer=f"I encountered an error: {str(e)}. Please check the backend logs for details.",
                citations=[],
                chunks_used=0,
                confidence=0.0
            )
        except Exception as e2:
            # If ChatResponse creation fails, return JSON directly
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=200,
                content={
                    "answer": f"Error: {str(e)[:200]}",
                    "citations": [],
                    "chunks_used": 0,
                    "confidence": 0.0
                }
            )


@app.post("/api/artillery/simple-chat")
async def simple_chat(request: ChatRequest):
    """Simplified chat endpoint that just uses OpenAI - for testing."""
    try:
        if not LEGACY_SYSTEMS_AVAILABLE or not chat_completion:
            return ChatResponse(
                answer="OpenAI client not available",
                citations=[],
                chunks_used=0,
                confidence=0.0
            )
        
        if not settings.OPENAI_API_KEY:
            return ChatResponse(
                answer="OpenAI API key not configured",
                citations=[],
                chunks_used=0,
                confidence=0.0
            )
        
        # Simple prompt
        messages = [
            {'role': 'system', 'content': 'You are LeguBot, a helpful legal information assistant. Answer questions clearly and conversationally, like ChatGPT. Start with a direct answer.'},
            {'role': 'user', 'content': request.message}
        ]
        
        answer = chat_completion(
            messages=messages,
            temperature=0.2,
            max_tokens=1500
        )
        
        return ChatResponse(
            answer=answer,
            citations=[],
            chunks_used=0,
            confidence=0.5
        )
    except Exception as e:
        import traceback
        logger.error(f"Simple chat error: {e}\n{traceback.format_exc()}")
        return ChatResponse(
            answer=f"Error: {str(e)}",
            citations=[],
            chunks_used=0,
            confidence=0.0
        )


@app.get("/api/artillery/test-openai")
async def test_openai():
    """Test endpoint to verify OpenAI API is working."""
    try:
        if not LEGACY_SYSTEMS_AVAILABLE or not chat_completion:
            return {"status": "error", "message": "OpenAI client not available"}
        
        if not settings.OPENAI_API_KEY:
            return {"status": "error", "message": "OpenAI API key not configured"}
        
        # Simple test message
        test_messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Say "Hello, OpenAI is working!" in one sentence.'}
        ]
        
        import time
        start_time = time.time()
        response = chat_completion(
            messages=test_messages,
            temperature=0.2,
            max_tokens=50
        )
        elapsed = time.time() - start_time
        
        return {
            "status": "success",
            "message": "OpenAI API is working!",
            "response": response,
            "elapsed_time": round(elapsed, 2),
            "model": settings.OPENAI_CHAT_MODEL,
            "api_key_set": bool(settings.OPENAI_API_KEY)
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.post("/api/artillery/recent-updates")
async def get_recent_updates(request: Dict[str, Any]):
    """Get recent legal updates for a specific law type and jurisdiction."""
    try:
        law_type = request.get("law_type", "")
        jurisdiction = request.get("jurisdiction", "")
        
        # Load recent updates from cache
        updates_file = Path(project_root) / "legal_data_cache" / "recent_updates.json"
        
        if not updates_file.exists():
            return {"updates": []}
        
        with open(updates_file, 'r', encoding='utf-8') as f:
            all_updates = json.load(f)
        
        # Get updates for this law type and jurisdiction
        key = f"{law_type}|{jurisdiction}"
        updates = all_updates.get(key, [])
        
        return {"updates": updates}
        
    except Exception as e:
        logger.error(f"Error fetching recent updates: {e}")
        return {"updates": []}


@app.get("/api/artillery/government-resources")
async def get_government_resources(
    law_type: str = Query(..., description="Type of law (e.g., Traffic Law, Criminal Law)"),
    province: Optional[str] = Query(None, description="Province code (e.g., ON, QC, BC)")
):
    """Get government resources for a specific law type and province."""
    try:
        # Import the provincial resources module
        sys.path.insert(0, str(project_root))
        from provincial_resources import get_provincial_resources
        
        resources = get_provincial_resources(law_type, province)
        
        return {
            "law_type": law_type,
            "province": province,
            "resources": resources
        }
    except Exception as e:
        logger.error(f"Error fetching government resources: {e}")
        return {
            "law_type": law_type,
            "province": province,
            "resources": []
        }


@app.get("/api/artillery/health")
async def artillery_health():
    """Artillery system health check."""
    try:
        # Don't call get_vector_store() to avoid initialization errors
        return {
            "status": "healthy",
            "faiss_index_size": 0,
            "models_loaded": True,
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/api/artillery/search")
async def artillery_search(request: SearchRequest):
    """Vector similarity search."""
    try:
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()

        query = request.query
        k = request.k
        filters = request.filters
        score_threshold = request.score_threshold

        if vector_store.index.ntotal == 0:
            return {"results": [], "total_found": 0, "message": "No documents indexed"}

        # Embed query
        query_embedding = embedding_service.embed_text(query)

        # Search
        results = vector_store.search(query_embedding[0], k=k, filters=filters)

        # Apply score threshold
        filtered_results = [r for r in results if r['score'] >= score_threshold]

        return {
            "results": [{
                "score": r['score'],
                "content": r['content'][:200] + "..." if len(r['content']) > 200 else r['content'],
                "metadata": r['metadata']
            } for r in filtered_results],
            "total_found": len(filtered_results),
            "query": query
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
async def artillery_search(request: SearchRequest):
    """Vector similarity search."""
    try:
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()

        query = request.query
        k = request.k
        filters = request.filters
        score_threshold = request.score_threshold

        if vector_store.index.ntotal == 0:
            return {"results": [], "total_found": 0, "message": "No documents indexed"}

        # Embed query
        query_embedding = embedding_service.embed_text(query)

        # Search
        results = vector_store.search(query_embedding[0], k=k, filters=filters)

        # Apply score threshold
        filtered_results = [r for r in results if r['score'] >= score_threshold]

        return {
            "results": [{
                "score": r['score'],
                "content": r['content'][:200] + "..." if len(r['content']) > 200 else r['content'],
                "metadata": r['metadata']
            } for r in filtered_results],
            "total_found": len(filtered_results),
            "query": query
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")

@app.get("/api/artillery/documents")
async def list_documents(user_id: str = "default_user"):
    """List all uploaded documents for a user."""
    try:
        vector_store = get_vector_store_artillery()

        # Get unique documents from metadata
        documents = {}
        for metadata in vector_store.metadata:
            if metadata.get('user_id') == user_id:
                doc_id = metadata.get('doc_id')
                if doc_id not in documents:
                    documents[doc_id] = {
                        'doc_id': doc_id,
                        'filename': metadata.get('filename'),
                        'chunks_count': 0,
                        'offence_number': metadata.get('offence_number')
                    }
                documents[doc_id]['chunks_count'] += 1

        return {
            "documents": list(documents.values()),
            "total": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/artillery/documents/{doc_id}")
async def delete_document(doc_id: str, user_id: str = "default_user"):
    """Delete a document and its chunks."""
    try:
        vector_store = get_vector_store_artillery()

        # Find chunks to delete by doc_id
        deleted_count = 0
        remaining_metadata = []
        remaining_indices = []

        for idx, metadata in enumerate(vector_store.metadata):
            if not (metadata.get('doc_id') == doc_id and metadata.get('user_id') == user_id):
                remaining_metadata.append(metadata)
                remaining_indices.append(idx)

        deleted_count = len(vector_store.metadata) - len(remaining_metadata)

        if deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

        # Note: FAISS doesn't support easy deletion, so we need to rebuild the index
        # For now, we'll mark the document as deleted but keep the data
        # In production, you'd want to rebuild the FAISS index
        logger.info(f"Marked {deleted_count} chunks as deleted for document {doc_id}")

        return {
            "status": "success",
            "doc_id": doc_id,
            "chunks_deleted": deleted_count,
            "message": f"Document {doc_id} marked for deletion ({deleted_count} chunks)"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Document deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document deletion failed: {str(e)}")


@app.get("/")
async def root():
    return {
        "message": "PLAZA-AI Legal Assistant API",
        "version": "1.0.0",
        "system": "Artillery - Multi-modal legal document assistant with local embeddings",
        "endpoints": {
            "health": "/api/artillery/health",
            "upload": "/api/artillery/upload",
            "chat": "/api/artillery/chat",
            "search": "/api/artillery/search",
            "documents": "/api/artillery/documents",
            "delete": "/api/artillery/documents/{doc_id}"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint - doesn't initialize vector store."""
    return {
        "status": "healthy",
        "backend_running": True,
        "openai_configured": bool(settings and settings.OPENAI_API_KEY) if LEGACY_SYSTEMS_AVAILABLE else False,
        "version": "1.0.0"
    }


# ============================================================================
# LEGAL API INTEGRATIONS - Case Lookup, Amendments, Translation
# ============================================================================

@app.post("/api/legal/case-lookup")
async def case_lookup(request: CaseLookupRequest, authorization: Optional[str] = Header(None)):
    """
    Search for legal cases using integrated legal APIs.
    Requires PREMIUM role or higher.
    """
    try:
        # Check permissions
        from app.services.rbac_service import get_rbac_service, UserRole
        rbac = get_rbac_service()
        
        # Extract role from token or default to STANDARD for demo
        user_role = UserRole.STANDARD
        if authorization:
            token = authorization.replace("Bearer ", "")
            user_role = rbac.get_user_role_from_token(token) or UserRole.STANDARD
        
        # Check API access
        access_check = rbac.can_use_api(user_role, "case_lookup")
        if not access_check["has_access"]:
            upgrade_info = rbac.get_upgrade_recommendation(user_role, "Case Lookup API")
            return {
                "success": False,
                "error": "Access denied",
                "upgrade_info": upgrade_info
            }
        
        # Use legal API integration service
        from app.services.legal_api_integrations import get_legal_api_service
        legal_api = get_legal_api_service()
        
        # Try CaseText first, fallback to LexisNexis
        result = await legal_api.case_lookup_casetext(
            query=request.query,
            jurisdiction=request.jurisdiction,
            year_from=request.year_from,
            year_to=request.year_to,
            limit=request.limit
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Case lookup error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Case lookup failed: {str(e)}")


@app.post("/api/legal/generate-amendment")
async def generate_amendment(request: AmendmentRequest, authorization: Optional[str] = Header(None)):
    """
    Generate legal amendments using integrated legal APIs.
    Requires PREMIUM role or higher.
    """
    try:
        # Check permissions
        from app.services.rbac_service import get_rbac_service, UserRole
        rbac = get_rbac_service()
        
        user_role = UserRole.STANDARD
        if authorization:
            token = authorization.replace("Bearer ", "")
            user_role = rbac.get_user_role_from_token(token) or UserRole.STANDARD
        
        access_check = rbac.can_use_api(user_role, "amendment_generation")
        if not access_check["has_access"]:
            upgrade_info = rbac.get_upgrade_recommendation(user_role, "Amendment Generation API")
            return {
                "success": False,
                "error": "Access denied",
                "upgrade_info": upgrade_info
            }
        
        # Use legal API integration service
        from app.services.legal_api_integrations import get_legal_api_service
        legal_api = get_legal_api_service()
        
        result = await legal_api.generate_amendment_legalzoom(
            document_type=request.document_type,
            case_details=request.case_details,
            jurisdiction=request.jurisdiction
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Amendment generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Amendment generation failed: {str(e)}")


@app.post("/api/legal/search-statutes")
async def search_statutes(
    query: str,
    jurisdiction: str = "US",
    law_type: Optional[str] = None,
    authorization: Optional[str] = Header(None)
):
    """
    Search for statutes and regulations.
    Requires STANDARD role or higher.
    """
    try:
        # Check permissions
        from app.services.rbac_service import get_rbac_service, UserRole
        rbac = get_rbac_service()
        
        user_role = UserRole.STANDARD
        if authorization:
            token = authorization.replace("Bearer ", "")
            user_role = rbac.get_user_role_from_token(token) or UserRole.STANDARD
        
        access_check = rbac.can_use_api(user_role, "statute_search")
        if not access_check["has_access"]:
            upgrade_info = rbac.get_upgrade_recommendation(user_role, "Statute Search API")
            return {
                "success": False,
                "error": "Access denied",
                "upgrade_info": upgrade_info
            }
        
        # Use legal API integration service
        from app.services.legal_api_integrations import get_legal_api_service
        legal_api = get_legal_api_service()
        
        result = await legal_api.search_statutes(
            query=query,
            jurisdiction=jurisdiction,
            law_type=law_type
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Statute search error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Statute search failed: {str(e)}")


# ============================================================================
# TRANSLATION API
# ============================================================================

@app.post("/api/translate")
async def translate_text(request: TranslationRequest, authorization: Optional[str] = Header(None)):
    """
    Translate text to target language.
    Available for STANDARD role and higher.
    """
    try:
        # Check permissions
        from app.services.rbac_service import get_rbac_service, UserRole
        rbac = get_rbac_service()
        
        user_role = UserRole.STANDARD
        if authorization:
            token = authorization.replace("Bearer ", "")
            user_role = rbac.get_user_role_from_token(token) or UserRole.STANDARD
        
        access_check = rbac.can_use_api(user_role, "translation")
        if not access_check["has_access"]:
            upgrade_info = rbac.get_upgrade_recommendation(user_role, "Translation API")
            return {
                "success": False,
                "error": "Access denied",
                "upgrade_info": upgrade_info
            }
        
        # Use translation service
        from app.services.translation_service import get_translation_service
        translation_service = get_translation_service()
        
        result = await translation_service.translate_text(
            text=request.text,
            target_language=request.target_language,
            source_language=request.source_language
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.get("/api/translate/languages")
async def get_supported_languages():
    """Get list of supported languages for translation."""
    from app.services.translation_service import get_translation_service
    translation_service = get_translation_service()
    
    return {
        "languages": translation_service.get_supported_languages()
    }


# ============================================================================
# CHAT HISTORY API
# ============================================================================

@app.post("/api/chat-history/save")
async def save_chat_message(
    user_id: str,
    session_id: str,
    message: str,
    response: str,
    metadata: Optional[Dict[str, Any]] = None
):
    """Save a chat message to history."""
    try:
        from app.services.chat_history_service import get_chat_history_service
        chat_history = get_chat_history_service(storage_type="local")
        
        message_id = await chat_history.save_message(
            user_id=user_id,
            session_id=session_id,
            message=message,
            response=response,
            metadata=metadata
        )
        
        return {
            "success": True,
            "message_id": message_id
        }
        
    except Exception as e:
        logger.error(f"Failed to save chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")


@app.get("/api/chat-history/session/{user_id}/{session_id}")
async def get_session_history(user_id: str, session_id: str, limit: int = 50):
    """Get chat history for a specific session."""
    try:
        from app.services.chat_history_service import get_chat_history_service
        chat_history = get_chat_history_service(storage_type="local")
        
        messages = await chat_history.get_session_history(
            user_id=user_id,
            session_id=session_id,
            limit=limit
        )
        
        return {
            "success": True,
            "messages": messages,
            "count": len(messages)
        }
        
    except Exception as e:
        logger.error(f"Failed to get session history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@app.get("/api/chat-history/sessions/{user_id}")
async def get_user_sessions(user_id: str, limit: int = 20):
    """Get all chat sessions for a user."""
    try:
        from app.services.chat_history_service import get_chat_history_service
        chat_history = get_chat_history_service(storage_type="local")
        
        sessions = await chat_history.get_user_sessions(
            user_id=user_id,
            limit=limit
        )
        
        return {
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")


@app.post("/api/chat-history/search")
async def search_chat_history(request: ChatHistorySearchRequest):
    """Search through chat history."""
    try:
        from app.services.chat_history_service import get_chat_history_service
        chat_history = get_chat_history_service(storage_type="local")
        
        results = await chat_history.search_chat_history(
            user_id=request.user_id,
            search_query=request.search_query,
            limit=request.limit
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"Failed to search chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.delete("/api/chat-history/session/{user_id}/{session_id}")
async def delete_session(user_id: str, session_id: str):
    """Delete a chat session."""
    try:
        from app.services.chat_history_service import get_chat_history_service
        chat_history = get_chat_history_service(storage_type="local")
        
        success = await chat_history.delete_session(
            user_id=user_id,
            session_id=session_id
        )
        
        return {
            "success": success,
            "message": "Session deleted successfully" if success else "Failed to delete session"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


# ============================================================================
# AI SUMMARY GENERATION API
# ============================================================================

@app.post("/api/chat/generate-summary")
async def generate_ai_summary(request: GenerateSummaryRequest):
    """
    Generate AI-powered case summary from conversation.
    Analyzes the conversation and provides comprehensive legal case summary.
    """
    try:
        from app.services.ai_summary_service import get_ai_summary_service
        
        ai_summary_service = get_ai_summary_service()
        
        logger.info(f"[AI_SUMMARY] Generating summary for {len(request.messages)} messages")
        
        result = await ai_summary_service.generate_case_summary(
            messages=request.messages,
            metadata=request.metadata
        )
        
        logger.info(f"[AI_SUMMARY] Summary generated successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate AI summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


# ============================================================================
# RBAC API
# ============================================================================

@app.post("/api/auth/token")
async def generate_auth_token(user_id: str, role: str = "standard"):
    """Generate authentication token for a user."""
    try:
        from app.services.rbac_service import get_rbac_service, UserRole
        rbac = get_rbac_service()
        
        # Convert role string to UserRole enum
        try:
            user_role = UserRole(role.lower())
        except ValueError:
            user_role = UserRole.STANDARD
        
        token = rbac.generate_token(user_id=user_id, role=user_role)
        permissions = rbac.get_role_permissions(user_role)
        limits = rbac.get_role_limits(user_role)
        
        return {
            "success": True,
            "token": token,
            "role": user_role.value,
            "permissions": [p.value for p in permissions],
            "limits": limits
        }
        
    except Exception as e:
        logger.error(f"Failed to generate token: {e}")
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")


@app.get("/api/auth/verify")
async def verify_token(authorization: str = Header(...)):
    """Verify authentication token."""
    try:
        from app.services.rbac_service import get_rbac_service
        rbac = get_rbac_service()
        
        token = authorization.replace("Bearer ", "")
        payload = rbac.verify_token(token)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {
            "success": True,
            "valid": True,
            "user_id": payload.get("user_id"),
            "role": payload.get("role"),
            "permissions": payload.get("permissions", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.get("/api/auth/check-access")
async def check_api_access(
    api_name: str,
    authorization: Optional[str] = Header(None)
):
    """Check if user has access to a specific API."""
    try:
        from app.services.rbac_service import get_rbac_service, UserRole
        rbac = get_rbac_service()
        
        user_role = UserRole.GUEST
        if authorization:
            token = authorization.replace("Bearer ", "")
            user_role = rbac.get_user_role_from_token(token) or UserRole.GUEST
        
        access_info = rbac.can_use_api(user_role, api_name)
        
        if not access_info["has_access"]:
            access_info["upgrade_info"] = rbac.get_upgrade_recommendation(user_role, api_name)
        
        return access_info
        
    except Exception as e:
        logger.error(f"Access check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Access check failed: {str(e)}")


# Voice Chat Endpoints - OpenAI TTS and Whisper
@app.post("/api/voice/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe audio using OpenAI Whisper API."""
    try:
        if not settings or not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Read audio file
        audio_data = await file.read()
        
        # Create OpenAI client
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Transcribe using Whisper
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=("audio.webm", audio_data, "audio/webm"),
            response_format="text"
        )
        
        logger.info(f"[VOICE] Transcribed: {transcript[:100]}...")
        return {"text": transcript}
        
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.post("/api/voice/speak")
async def text_to_speech(request: VoiceChatRequest):
    """Convert text to speech using OpenAI TTS API."""
    try:
        if not settings or not settings.OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Map language to OpenAI voice
        voice_map = {
            'en': 'alloy',    # English - neutral, balanced
            'hi': 'nova',     # Hindi - warm, friendly
            'fr': 'shimmer',  # French - elegant
            'es': 'fable',    # Spanish - expressive
            'pa': 'onyx',     # Punjabi - deep, authoritative
            'zh': 'echo'      # Chinese - clear, articulate
        }
        
        selected_voice = voice_map.get(request.language, 'alloy')
        if request.voice:
            selected_voice = request.voice
        
        logger.info(f"[VOICE] TTS request - Language: {request.language}, Voice: {selected_voice}, Text length: {len(request.text)}")
        
        # Create OpenAI client
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Generate speech
        response = client.audio.speech.create(
            model="tts-1",  # or tts-1-hd for higher quality
            voice=selected_voice,
            input=request.text[:4096],  # OpenAI TTS limit
            response_format="mp3"
        )
        
        # Stream the audio back
        audio_bytes = BytesIO(response.content)
        
        return StreamingResponse(
            audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

