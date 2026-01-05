"""Azure OpenAI client wrapper for embeddings and chat completions."""
import numpy as np
from typing import List, Optional
from openai import AzureOpenAI
import logging
import time

from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Wrapper around Azure OpenAI Python SDK."""
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None
    ):
        """Initialize Azure OpenAI client."""
        self.endpoint = endpoint or settings.AZURE_OPENAI_ENDPOINT
        self.api_key = api_key or settings.AZURE_OPENAI_API_KEY
        self.embedding_api_version = api_version or settings.AZURE_OPENAI_EMBEDDING_API_VERSION
        
        if not self.endpoint or not self.api_key:
            raise ValueError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set")
        
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.embedding_api_version
        )
        self.embedding_model = settings.AZURE_OPENAI_EMBEDDING_MODEL
        self.chat_model = settings.AZURE_OPENAI_CHAT_MODEL
        self.chat_api_version = settings.AZURE_OPENAI_CHAT_API_VERSION
        self.embedding_delay = settings.EMBEDDING_DELAY
    
    def get_embeddings(self, texts: List[str], organization: Optional[str] = None, subject: Optional[str] = None) -> np.ndarray:
        """
        Get embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            organization: Optional organization name for content formatting
            subject: Optional subject for content formatting
            
        Returns:
            numpy array of shape (N, D) where N is number of texts and D is embedding dimension
        """
        if not texts:
            raise ValueError("texts list cannot be empty")
        
        try:
            # Format content if organization/subject provided
            if organization or subject:
                formatted_texts = []
                for text in texts:
                    parts = []
                    if organization:
                        parts.append(f"Organization: {organization}")
                    if subject:
                        parts.append(f"Subject: {subject}")
                    parts.append(f"context: {text}")
                    formatted_texts.append(", ".join(parts))
                texts = formatted_texts
            
            # Generate embeddings with rate limiting
            embeddings = []
            for i, text in enumerate(texts):
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=text
                )
                embeddings.append(response.data[0].embedding)
                
                # Rate limiting delay (except for last item)
                if i < len(texts) - 1:
                    time.sleep(self.embedding_delay)
            
            # Convert to numpy array
            vectors = np.array(embeddings, dtype=np.float32)
            
            logger.info(f"Generated {len(embeddings)} embeddings with dimension {vectors.shape[1]}")
            return vectors
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def chat_completion(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate chat completion using Azure OpenAI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            # Use chat API version for chat completions
            chat_client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.chat_api_version
            )
            
            response = chat_client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise


# Global singleton instance
_azure_openai_client: Optional[AzureOpenAIClient] = None


def get_openai_client() -> AzureOpenAIClient:
    """Get or create the global Azure OpenAI client instance."""
    global _azure_openai_client
    if _azure_openai_client is None:
        _azure_openai_client = AzureOpenAIClient()
    return _azure_openai_client

