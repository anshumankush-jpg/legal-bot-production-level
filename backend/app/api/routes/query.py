"""Endpoints for querying and answering questions."""
import logging
from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import QueryRequest, QueryResponse
from app.rag.rag_service import get_rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("/answer", response_model=QueryResponse)
async def answer_question(
    request: QueryRequest,
    hybrid: bool = Query(True, description="Use hybrid search (vector + text)"),
    include_parent: bool = Query(True, description="Include parent context for child chunks")
):
    """
    Answer a question using RAG with Azure AI Search.
    
    Body:
    - question: User's question
    - top_k: Optional number of chunks to retrieve (defaults to config)
    
    Query params:
    - hybrid: Use hybrid search (vector + text) - default True
    - include_parent: Include parent context for child chunks - default True
    
    Returns:
    - answer: Generated answer
    - sources: List of source chunks used
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.answer_question(
            query=request.question,
            top_k=request.top_k,
            hybrid_search=hybrid,
            include_parent_context=include_parent,
            language=request.language,
            country=request.country,
            province=request.province,
            offense_type=request.offense_type,
            context=request.context
        )
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_similar(
    request: QueryRequest,
    hybrid: bool = Query(True, description="Use hybrid search")
):
    """
    Perform similarity search without LLM generation using Azure AI Search.
    
    Returns top_k most similar chunks with metadata.
    """
    try:
        rag_service = get_rag_service()
        top_k = request.top_k or rag_service.top_k
        
        # Embed query
        query_embedding = rag_service.embedding_service.embed_text(request.question)
        query_vector = query_embedding[0].tolist()
        
        # Search Azure AI Search
        results = rag_service.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
            search_text=request.question if hybrid else None,
            filters="is_config eq false"
        )
        
        # Format results
        sources = []
        for score, doc in results:
            sources.append({
                'doc_id': doc.get('id'),
                'parent_id': doc.get('parent_id'),
                'child_id': doc.get('child_id'),
                'source_name': doc.get('source'),
                'source_type': 'document',
                'page': doc.get('page', 0),
                'score': score,
                'text': doc.get('content', ''),
                'snippet': doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', ''),
                'subject': doc.get('subject', '')
            })
        
        return {
            'query': request.question,
            'results': sources
        }
    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

