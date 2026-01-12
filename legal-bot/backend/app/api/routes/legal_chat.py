"""
Legal Chat API - RAG-based Legal Q&A Endpoint.

Provides jurisdiction-aware legal answers grounded in indexed legal documents.
"""

import logging
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.models.schemas import LegalChatRequest, LegalChatResponse
from app.legal_retrieval import get_legal_retrieval_service, initialize_legal_index
from app.rag_prompt_builder import get_legal_rag_builder
from app.llm_client import get_legal_llm_client, validate_legal_llm_setup

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/legal", tags=["legal-chat"])


@router.post("/chat", response_model=LegalChatResponse)
async def legal_chat(request: LegalChatRequest) -> LegalChatResponse:
    """
    Answer legal questions using RAG with retrieved legal documents.

    This endpoint:
    1. Searches the legal document index with jurisdiction filtering
    2. Builds context from retrieved chunks with proper citations
    3. Calls LLM to generate grounded legal answer
    4. Returns answer with source citations

    Body:
    - question: User's legal question
    - country: Optional country filter (Canada, USA)
    - jurisdiction: Optional jurisdiction filter (Ontario, California, etc.)
    - max_results: Maximum chunks to retrieve (default: 8)

    Returns:
    - answer: Grounded legal answer
    - citations: List of legal sources used
    - jurisdiction: Jurisdiction of the answer
    - country: Country of the answer
    - chunks_used: Number of document chunks used
    """
    try:
        logger.info(f"Legal chat request: '{request.question}' (country: {request.country}, jurisdiction: {request.jurisdiction})")

        # Step 1: Validate setup
        if not initialize_legal_index():
            raise HTTPException(
                status_code=503,
                detail="Legal document index is not available. Please ensure documents have been ingested."
            )

        llm_validation = validate_legal_llm_setup()
        if not llm_validation.get('setup_valid'):
            logger.error(f"LLM setup invalid: {llm_validation}")
            raise HTTPException(
                status_code=503,
                detail="LLM service is not properly configured. Please check API keys."
            )

        # Step 2: Set up services
        retrieval_service = get_legal_retrieval_service()
        prompt_builder = get_legal_rag_builder()
        llm_client = get_legal_llm_client()

        # Step 3: Search legal documents
        filters = {}
        if request.country:
            filters['country'] = request.country
        if request.jurisdiction:
            filters['jurisdiction'] = request.jurisdiction

        retrieved_chunks = retrieval_service.search_legal_index(
            query=request.question,
            k=request.max_results,
            filters=filters
        )

        # Step 4: Check if we have sufficient context
        if not retrieved_chunks:
            logger.info(f"No relevant legal documents found for question: {request.question}")
            return LegalChatResponse(
                answer="I don't have information about that in the available legal documents. Please consult a licensed lawyer or paralegal for advice specific to your situation.",
                citations=[],
                jurisdiction=request.jurisdiction,
                country=request.country,
                chunks_used=0
            )

        # Step 5: Build RAG prompt
        messages = prompt_builder.build_legal_rag_messages(
            question=request.question,
            retrieved_chunks=retrieved_chunks,
            user_country=request.country,
            user_jurisdiction=request.jurisdiction
        )

        # Step 6: Call LLM
        answer = llm_client.call_legal_llm(messages)

        # Step 7: Extract citations
        citations = prompt_builder.extract_citations_from_chunks(retrieved_chunks)

        # Step 8: Build response
        response = LegalChatResponse(
            answer=answer,
            citations=citations,
            jurisdiction=request.jurisdiction or (citations[0].get('jurisdiction') if citations else None),
            country=request.country or (citations[0].get('country') if citations else None),
            chunks_used=len(retrieved_chunks)
        )

        logger.info(f"Legal chat completed: {len(citations)} citations, {len(retrieved_chunks)} chunks used")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in legal chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your legal question: {str(e)}"
        )


@router.get("/health")
async def legal_chat_health() -> Dict[str, Any]:
    """
    Health check for legal chat service.

    Returns status of legal index and LLM setup.
    """
    try:
        index_ready = initialize_legal_index()
        llm_setup = validate_legal_llm_setup()

        status = "healthy" if (index_ready and llm_setup.get('setup_valid')) else "unhealthy"

        return {
            "status": status,
            "index_ready": index_ready,
            "llm_ready": llm_setup.get('setup_valid'),
            "llm_provider": "openai" if "openai" in str(llm_setup) else "unknown",
            "message": "Legal chat service is ready" if status == "healthy" else "Service not fully configured"
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }