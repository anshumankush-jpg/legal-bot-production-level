"""
RAG Prompt Builder for Legal Q&A.

Constructs properly formatted prompts for legal questions using retrieved document chunks.
Ensures answers are grounded in legal sources and include proper citations.
"""

import logging
from typing import List, Dict
from app.legal_retrieval import RetrievedChunk

logger = logging.getLogger(__name__)


class LegalRAGPromptBuilder:
    """
    Builder for legal RAG prompts that ensure grounded, cited answers.
    """

    def __init__(self, max_context_tokens: int = 3000):
        """
        Initialize the prompt builder.

        Args:
            max_context_tokens: Maximum tokens for context (approximate)
        """
        self.max_context_tokens = max_context_tokens

    def build_legal_rag_messages(
        self,
        question: str,
        retrieved_chunks: List[RetrievedChunk],
        user_country: str = None,
        user_jurisdiction: str = None
    ) -> List[Dict[str, str]]:
        """
        Build RAG messages for legal Q&A.

        Args:
            question: User's legal question
            retrieved_chunks: Retrieved document chunks with legal metadata
            user_country: User's country (if known)
            user_jurisdiction: User's jurisdiction (if known)

        Returns:
            List of message dicts for LLM API
        """
        if not retrieved_chunks:
            # No context available - return message indicating insufficient information
            return self._build_insufficient_context_messages(question)

        # Build context from retrieved chunks
        context_parts = []
        citations_used = []

        for i, chunk in enumerate(retrieved_chunks, 1):
            # Create document identifier
            doc_id = f"Doc #{i}"
            if chunk.law_name:
                doc_id += f" | Law: {chunk.law_name}"
            if chunk.section:
                doc_id += f" | Section: {chunk.section}"
            if chunk.jurisdiction:
                doc_id += f" | Jurisdiction: {chunk.jurisdiction}"
            if chunk.country:
                doc_id += f" | Country: {chunk.country}"

            # Add page info if available
            if chunk.page > 0:
                doc_id += f" | Page: {chunk.page}"

            # Format context entry
            context_entry = f"[{doc_id}]\n{chunk.text}\n"
            context_parts.append(context_entry)

            # Track citations
            citations_used.append({
                'doc_id': chunk.doc_id,
                'law_name': chunk.law_name,
                'section': chunk.section,
                'citation': chunk.citation,
                'jurisdiction': chunk.jurisdiction,
                'country': chunk.country,
                'page': chunk.page,
                'source_path': chunk.source_path
            })

        # Join all context parts
        full_context = "\n---\n".join(context_parts)

        # Truncate if too long (rough token estimation: ~4 chars per token)
        max_chars = self.max_context_tokens * 4
        if len(full_context) > max_chars:
            full_context = full_context[:max_chars] + "\n[Context truncated due to length...]"
            logger.warning(f"Context truncated to fit token limit: {len(full_context)} chars")

        # Build system message
        system_message = self._build_legal_system_message(user_country, user_jurisdiction)

        # Build user message with context
        user_message = f"""Legal Question: {question}

Retrieved Legal Documents:
{full_context}

Please answer the question based ONLY on the retrieved legal documents above. If the documents do not contain sufficient information to answer the question, explicitly state that you cannot provide an answer from the available legal sources."""

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

    def _build_legal_system_message(self, user_country: str = None, user_jurisdiction: str = None) -> str:
        """
        Build the system message for legal Q&A using professional prompt system.

        Args:
            user_country: User's country for jurisdiction awareness
            user_jurisdiction: User's specific jurisdiction

        Returns:
            System message string
        """
        from app.legal_prompts import LegalPromptSystem
        
        # Start with professional system prompt
        system_message = LegalPromptSystem.PROFESSIONAL_SYSTEM_PROMPT
        
        # Add document context instructions
        system_message += "\n\n" + LegalPromptSystem.DOCUMENT_CONTEXT_PROMPT
        
        # Add jurisdiction-specific context
        jurisdiction = user_jurisdiction or user_country
        if jurisdiction:
            jurisdiction_lower = jurisdiction.lower()
            for key, prompt in LegalPromptSystem.JURISDICTION_PROMPTS.items():
                if key in jurisdiction_lower:
                    system_message += "\n\n" + prompt
                    break
            
            # Add specific jurisdiction note
            system_message += f"\n\n**USER JURISDICTION:** The user is located in {jurisdiction}. Prioritize information relevant to this jurisdiction."
        
        return system_message

    def _build_insufficient_context_messages(self, question: str) -> List[Dict[str, str]]:
        """
        Build messages when no relevant legal context is available.

        Args:
            question: User's question

        Returns:
            List of message dicts indicating insufficient context
        """
        system_message = """You are a legal information assistant. You only provide information based on official legal documents.

When no relevant legal documents are available to answer a question, you must clearly state that you cannot provide information from the available legal sources."""

        user_message = f"""Legal Question: {question}

Available Legal Documents: None found

Please respond indicating that you don't have sufficient legal information to answer this question."""

        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

    def extract_citations_from_chunks(self, chunks: List[RetrievedChunk]) -> List[Dict]:
        """
        Extract citation information from retrieved chunks for API response.

        Args:
            chunks: Retrieved legal chunks

        Returns:
            List of citation dictionaries for API response
        """
        citations = []
        for chunk in chunks:
            citation = {
                'doc_id': chunk.doc_id,
                'law_name': chunk.law_name,
                'section': chunk.section,
                'citation': chunk.citation,
                'jurisdiction': chunk.jurisdiction,
                'country': chunk.country,
                'page': chunk.page,
                'source_path': chunk.source_path,
                'relevance_score': chunk.score
            }
            citations.append(citation)

        return citations


# Global instance
_legal_rag_builder: LegalRAGPromptBuilder = None


def get_legal_rag_builder(max_context_tokens: int = 3000) -> LegalRAGPromptBuilder:
    """Get or create the global legal RAG prompt builder."""
    global _legal_rag_builder
    if _legal_rag_builder is None:
        _legal_rag_builder = LegalRAGPromptBuilder(max_context_tokens=max_context_tokens)
    return _legal_rag_builder