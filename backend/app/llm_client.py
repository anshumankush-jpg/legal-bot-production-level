"""
LLM Client for Legal Chat Completions.

Handles OpenAI-compatible API calls for legal RAG with proper error handling and configuration.
"""

import logging
import asyncio
from typing import List, Dict, Optional
from app.core.openai_client_unified import chat_completion
from app.core.config import settings

logger = logging.getLogger(__name__)


class LegalLLMClient:
    """
    Specialized LLM client for legal RAG applications.

    Provides legal-focused chat completions with appropriate temperature and error handling.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0.1,  # Lower temperature for legal accuracy
        max_tokens: int = 2000,
        timeout: int = 30
    ):
        """
        Initialize the legal LLM client.

        Args:
            model: LLM model name (uses config default if None)
            temperature: Sampling temperature (lower for legal precision)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
        """
        self.model = model or settings.OPENAI_CHAT_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

        logger.info(f"Legal LLM client initialized: model={self.model}, temp={self.temperature}")

    async def call_legal_llm_async(self, messages: List[Dict[str, str]]) -> str:
        """
        Async call to LLM for legal Q&A.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            LLM response text
        """
        try:
            # Use the unified OpenAI client
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: chat_completion(
                    messages=messages,
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            )

            if not response or not response.strip():
                logger.warning("LLM returned empty response")
                return "I apologize, but I received an empty response. Please try rephrasing your question."

            logger.info(f"LLM response generated: {len(response)} characters")
            return response.strip()

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return self._get_fallback_response(str(e))

    def call_legal_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        Synchronous call to LLM for legal Q&A.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            LLM response text
        """
        try:
            # Use the unified OpenAI client
            response = chat_completion(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            if not response or not response.strip():
                logger.warning("LLM returned empty response")
                return "I apologize, but I received an empty response. Please try rephrasing your question."

            logger.info(f"LLM response generated: {len(response)} characters")
            return response.strip()

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return self._get_fallback_response(str(e))

    def _get_fallback_response(self, error: str) -> str:
        """
        Generate a fallback response when LLM call fails.

        Args:
            error: Error message from failed call

        Returns:
            User-friendly fallback response
        """
        fallback = """I apologize, but I'm currently unable to generate a response due to a technical issue.

This is general legal information only, not legal advice. For advice about your specific case, please consult a licensed lawyer or paralegal in your jurisdiction.

If you continue to experience issues, please try again later or contact support."""

        logger.warning(f"Using fallback response due to error: {error}")
        return fallback

    def validate_api_key(self) -> bool:
        """
        Validate that the API key is configured.

        Returns:
            True if API key is available, False otherwise
        """
        if settings.LLM_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
            logger.error("OpenAI API key not configured")
            return False
        elif settings.LLM_PROVIDER == "azure" and (not settings.AZURE_OPENAI_API_KEY or not settings.AZURE_OPENAI_ENDPOINT):
            logger.error("Azure OpenAI credentials not configured")
            return False

        return True


# Global instance
_legal_llm_client: Optional[LegalLLMClient] = None


def get_legal_llm_client() -> LegalLLMClient:
    """Get or create the global legal LLM client instance."""
    global _legal_llm_client
    if _legal_llm_client is None:
        _legal_llm_client = LegalLLMClient()
    return _legal_llm_client


def validate_legal_llm_setup() -> Dict[str, bool]:
    """
    Validate the legal LLM setup.

    Returns:
        Dict with validation results
    """
    client = get_legal_llm_client()

    results = {
        'api_key_configured': client.validate_api_key(),
        'model_specified': bool(client.model),
        'client_initialized': True
    }

    all_valid = all(results.values())
    results['setup_valid'] = all_valid

    if all_valid:
        logger.info("Legal LLM setup validation passed")
    else:
        logger.error(f"Legal LLM setup validation failed: {results}")

    return results