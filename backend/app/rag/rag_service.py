"""RAG service for question answering with retrieved context using FAISS (local vector database) and Sentence Transformers (local embeddings)."""
import logging
from typing import List, Dict, Optional, Tuple
import uuid
from datetime import datetime

from app.core.config import settings
from app.embeddings.embedding_service import get_embedding_service
from app.vector_store import get_vector_store
from app.core.openai_client_unified import chat_completion, get_embeddings

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG-based question answering with parent-child chunking."""
    
    def __init__(self):
        """Initialize RAG service."""
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()
        self.top_k = settings.RAG_TOP_K
        self.use_parent_child = settings.USE_PARENT_CHILD
        
        # Parent-child chunking settings
        self.parent_chunk_size = settings.PARENT_CHUNK_SIZE
        self.parent_chunk_overlap = settings.PARENT_CHUNK_OVERLAP
        self.child_chunk_size = settings.CHILD_CHUNK_SIZE
        self.child_chunk_overlap = settings.CHILD_CHUNK_OVERLAP
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int,
        overlap: int
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start forward by (chunk_size - overlap) for next chunk
            start += chunk_size - overlap
            
            # Prevent infinite loop if overlap >= chunk_size
            if overlap >= chunk_size:
                break
        
        return chunks
    
    def create_parent_child_chunks(
        self,
        text: str,
        doc_id: str,
        source_name: str,
        source_type: str = "text",
        page: Optional[int] = None,
        organization: Optional[str] = None,
        subject: Optional[str] = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Create parent and child chunks with hierarchical structure.
        
        Args:
            text: Full text to chunk
            doc_id: Document ID
            source_name: Source identifier
            source_type: Type of source
            page: Page number (if applicable)
            organization: Organization name
            subject: Document subject
            
        Returns:
            Tuple of (parent_documents, child_documents)
        """
        # Create parent chunks
        parent_chunks = self.chunk_text(text, self.parent_chunk_size, self.parent_chunk_overlap)
        
        parent_docs = []
        child_docs = []
        
        for parent_idx, parent_text in enumerate(parent_chunks):
            parent_id = f"{doc_id}_parent_{parent_idx}"
            
            # Create parent document (without vector, reference only)
            parent_doc = {
                "id": parent_id,
                "content": parent_text,
                "parent_id": None,
                "child_id": None,
                "subject": subject or "",
                "is_config": False,
                "source": source_name,
                "page": page or 0,
                "organization": organization or "",
                "vector": []  # Parent chunks don't have vectors
            }
            parent_docs.append(parent_doc)
            
            # Create child chunks from this parent
            child_chunks = self.chunk_text(parent_text, self.child_chunk_size, self.child_chunk_overlap)
            
            for child_idx, child_text in enumerate(child_chunks):
                child_id = f"{parent_id}_child_{child_idx}"
                
                child_doc = {
                    "id": child_id,
                    "content": child_text,
                    "parent_id": parent_id,
                    "child_id": child_id,
                    "subject": subject or "",
                    "is_config": False,
                    "source": source_name,
                    "page": page or 0,
                    "organization": organization or "",
                    "vector": []  # Will be filled after embedding
                }
                child_docs.append(child_doc)
        
        return parent_docs, child_docs
    
    def ingest_file_rtld(
        self,
        file_path: str,
        source_name: str,
        content_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest a file using RTLD's multi-modal processing capabilities.

        Args:
            file_path: Path to the file
            source_name: Name/identifier of the source
            content_type: Type of content ('text', 'image', 'table', 'document', 'auto')
            tags: Optional tags
            metadata: Additional metadata

        Returns:
            Dict with doc_id and chunk counts
        """
        if settings.EMBEDDING_PROVIDER != "rtld":
            raise ValueError("RTLD provider required for multi-modal file ingestion")

        doc_id = str(uuid.uuid4())
        metadata = metadata or {}
        tags = tags or []

        # Use RTLD to process the file
        embeddings, chunk_texts, chunk_ids = self.embedding_service.embed_file(
            file_path=file_path,
            content_type=content_type,
            metadata={
                'doc_id': doc_id,
                'source_name': source_name,
                'source_type': content_type or 'document',
                'tags': tags,
                **metadata
            }
        )

        if len(embeddings) == 0:
            return {
                'doc_id': doc_id,
                'chunks': 0,
                'source_name': source_name,
                'message': 'No content extracted from file'
            }

        # Create metadata for each chunk
        metadatas = []
        texts = []

        for i, (chunk_text, chunk_id) in enumerate(zip(chunk_texts, chunk_ids)):
            chunk_metadata = {
                'id': f"{doc_id}_chunk_{i}",
                'doc_id': doc_id,
                'chunk_id': chunk_id,
                'source_name': source_name,
                'source_type': content_type or 'document',
                'tags': tags,
                'chunk_index': i,
                **metadata
            }
            metadatas.append(chunk_metadata)
            texts.append(chunk_text)

        # Add to vector store
        ids = self.vector_store.add_embeddings(embeddings, metadatas, texts)

        # Save the index
        self.vector_store.save()

        logger.info(f"Ingested RTLD file: {source_name} with {len(chunk_texts)} chunks")

        return {
            'doc_id': doc_id,
            'chunks': len(chunk_texts),
            'source_name': source_name,
            'content_type': content_type,
            'rtld_chunks': len(chunk_texts)
        }

    def ingest_text(
        self,
        text: str,
        source_name: str,
        source_type: str = "text",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        organization: Optional[str] = None,
        subject: Optional[str] = None,
        page: Optional[int] = None
    ) -> Dict:
        """
        Ingest text into Azure AI Search with parent-child chunking.
        
        Args:
            text: Text to ingest
            source_name: Name/identifier of the source
            source_type: Type of source (text, pdf, image_ticket, etc.)
            tags: Optional tags
            metadata: Additional metadata
            organization: Organization name
            subject: Document subject
            page: Page number
            
        Returns:
            Dict with doc_id and chunk counts
        """
        doc_id = str(uuid.uuid4())
        metadata = metadata or {}
        
        if self.use_parent_child:
            # Create parent-child structure
            parent_docs, child_docs = self.create_parent_child_chunks(
                text=text,
                doc_id=doc_id,
                source_name=source_name,
                source_type=source_type,
                page=page,
                organization=organization,
                subject=subject
            )
            
            # Generate embeddings for child chunks only
            child_texts = [doc["content"] for doc in child_docs]
            child_embeddings = self.embedding_service.embed_texts(
                child_texts,
                organization=organization,
                subject=subject
            )
            
            # Add vectors to child documents
            for i, child_doc in enumerate(child_docs):
                child_doc["vector"] = child_embeddings[i].tolist()
            
            # Upload parent documents (no vectors)
            if parent_docs:
                self.vector_store.add_documents(parent_docs)
            
            # Upload child documents (with vectors)
            if child_docs:
                self.vector_store.add_documents(child_docs)
            
            total_chunks = len(parent_docs) + len(child_docs)
            
        else:
            # Simple chunking (fallback)
            chunks = self.chunk_text(text, self.child_chunk_size, self.child_chunk_overlap)
            
            # Generate embeddings
            embeddings = self.embedding_service.embed_texts(
                chunks,
                organization=organization,
                subject=subject
            )
            
            # Create documents
            documents = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                doc = {
                    "id": chunk_id,
                    "content": chunk,
                    "parent_id": None,
                    "child_id": None,
                    "subject": subject or "",
                    "is_config": False,
                    "source": source_name,
                    "page": page or 0,
                    "organization": organization or "",
                    "vector": embeddings[i].tolist()
                }
                documents.append(doc)
            
            self.vector_store.add_documents(documents)
            total_chunks = len(documents)
        
        logger.info(f"Ingested document {doc_id} with {total_chunks} chunks")
        
        return {
            'doc_id': doc_id,
            'chunks': total_chunks,
            'source_name': source_name,
            'parent_child': self.use_parent_child
        }
    
    def answer_question(
        self,
        query: str,
        top_k: Optional[int] = None,
        hybrid_search: bool = True,
        include_parent_context: bool = True,
        language: Optional[str] = "en",
        country: Optional[str] = None,
        province: Optional[str] = None,
        offense_type: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Answer a question using RAG with parent-child retrieval.
        
        Args:
            query: User's question
            top_k: Number of chunks to retrieve (defaults to config)
            hybrid_search: Use hybrid search (vector + text)
            include_parent_context: Retrieve parent chunks for child results
            
        Returns:
            Dict with 'answer' and 'sources'
        """
        top_k = top_k or self.top_k
        
        # Step 1: Embed query
        query_embedding = self.embedding_service.embed_text(query)
        query_vector = query_embedding[0].tolist()
        
        # Step 2: Search FAISS vector database (local)
        # Note: search_text and filters are for Azure compatibility, FAISS uses vector similarity only
        search_text = query if hybrid_search else None
        results = self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
            search_text=search_text,  # Ignored by FAISS, kept for compatibility
            filters="is_config eq false"  # Ignored by FAISS, kept for compatibility
        )
        
        if not results:
            return {
                'answer': "I don't have enough information in my knowledge base to answer this question. Please ensure relevant documents have been ingested.\n\nTo ingest documents:\n1. Use the upload feature in the chat interface\n2. Or run the bulk ingestion script: `python backend/scripts/bulk_ingest_documents.py`\n\nThis will index documents from:\n- US state codes\n- Canada traffic acts\n- Paralegal advice dataset\n- All legal document folders",
                'sources': []
            }
        
        # Step 3: Build context with parent-child expansion
        context_parts = []
        sources = []
        seen_parents = set()
        
        for score, doc in results:
            source_info = {
                'doc_id': doc.get('id'),
                'parent_id': doc.get('parent_id'),
                'child_id': doc.get('child_id'),
                'source_name': doc.get('source'),
                'source_type': 'document',
                'page': doc.get('page', 0),
                'score': score,
                'snippet': doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', '')
            }
            sources.append(source_info)
            
            # If this is a child chunk and we want parent context
            if include_parent_context and self.use_parent_child:
                parent_id = doc.get('parent_id')
                if parent_id and parent_id not in seen_parents:
                    parent_doc = self.vector_store.get_parent_context(parent_id)
                    if parent_doc:
                        seen_parents.add(parent_id)
                        # Add parent context
                        context_parts.append(
                            f"[Parent Context from {doc.get('source', 'Unknown')}, Page {doc.get('page', 0)}]\n{parent_doc.get('content', '')}\n"
                        )
            
            # Add the retrieved chunk
            context_parts.append(
                f"[Source: {doc.get('source', 'Unknown')}, Page {doc.get('page', 0)}]\n{doc.get('content', '')}\n"
            )
        
        context = "\n---\n".join(context_parts)
        
        # Build context information for the prompt
        context_info = []
        if country:
            context_info.append(f"Country: {country}")
        if province:
            context_info.append(f"Province/State: {province}")
        if offense_type:
            context_info.append(f"Offense Type: {offense_type}")
        if context:
            if context.get('offenseDetails'):
                context_info.append(f"User Details: {context.get('offenseDetails', {})}")
        
        context_header = "\n".join(context_info) if context_info else "No specific jurisdiction or offense context provided."
        
        # Step 4: Generate answer using LLM with legal assistant system prompt
        # Use LEGAL_ASSISTANT_SYSTEM_PROMPT for ticket/summons queries, SYSTEM_PROMPT for general queries
        language_instruction = f"\n\nIMPORTANT: Respond in {language.upper()} language. The user has selected {language} as their preferred language."
        
        system_prompt = f"""{settings.LEGAL_ASSISTANT_SYSTEM_PROMPT}
{language_instruction}

USER CONTEXT:
{context_header}

RETRIEVED DOCUMENTS:
{context}

HISTORY:
(No previous conversation)

QUESTION: {query}

ANSWER:"""

        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query}
        ]
        
        try:
            answer = chat_completion(
                messages=messages,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            answer = f"I encountered an error while generating an answer: {str(e)}"
        
        return {
            'answer': answer,
            'sources': sources
        }


# Global singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create the global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
