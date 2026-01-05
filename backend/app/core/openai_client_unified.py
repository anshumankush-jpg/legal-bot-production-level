"""Unified OpenAI client supporting both direct OpenAI and Azure OpenAI."""
import logging
from typing import List, Optional
import numpy as np
from openai import OpenAI, AzureOpenAI
from openai import APIConnectionError, APIStatusError

from app.core.config import settings

logger = logging.getLogger(__name__)

_openai_client: Optional[OpenAI] = None
_azure_openai_client: Optional[AzureOpenAI] = None


def get_openai_client():
    """
    Get or create OpenAI client (direct API).
    """
    global _openai_client
    if _openai_client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'")
        import httpx
        # Configure timeout for faster failure
        _openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=httpx.Timeout(30.0, connect=10.0)  # 30s total, 10s connect
        )
        logger.info("OpenAI client (direct API) initialized with 30s timeout.")
    return _openai_client


def get_azure_openai_client():
    """
    Get or create Azure OpenAI client.
    """
    global _azure_openai_client
    if _azure_openai_client is None:
        if not settings.AZURE_OPENAI_API_KEY or not settings.AZURE_OPENAI_ENDPOINT:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are required for Azure OpenAI")
        import httpx
        # Configure timeout for faster failure
        _azure_openai_client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_EMBEDDING_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            timeout=httpx.Timeout(30.0, connect=10.0)  # 30s total, 10s connect
        )
        logger.info("Azure OpenAI client initialized with 30s timeout.")
    return _azure_openai_client


def get_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of texts.
    Supports both OpenAI direct API and Azure OpenAI.

    Args:
        texts: A list of strings to embed.

    Returns:
        A numpy array of float32 embeddings.
    """
    try:
        if settings.LLM_PROVIDER == "azure":
            client = get_azure_openai_client()
            response = client.embeddings.create(
                model=settings.AZURE_OPENAI_EMBEDDING_MODEL,
                input=texts
            )
        else:  # OpenAI direct
            client = get_openai_client()
            response = client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=texts
            )
        
        embeddings = np.array([d.embedding for d in response.data], dtype=np.float32)
        return embeddings
    except APIConnectionError as e:
        logger.error(f"OpenAI API connection error: {e}")
        raise
    except APIStatusError as e:
        logger.error(f"OpenAI API status error: {e.status_code} - {e.response}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during embedding generation: {e}")
        raise


def chat_completion(
    messages: List[dict],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    streaming: bool = False
) -> str:
    """
    Generate chat completion using OpenAI or Azure OpenAI.
    Timeout is configured at client initialization (30s).

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name (optional, uses config default)
        temperature: Temperature (optional, uses config default)
        max_tokens: Max tokens (optional, uses config default)
        streaming: Whether to stream response

    Returns:
        Generated text response
    """
    import httpx
    
    model = model or (settings.AZURE_OPENAI_CHAT_MODEL if settings.LLM_PROVIDER == "azure" else settings.OPENAI_CHAT_MODEL)
    temperature = temperature if temperature is not None else settings.OPENAI_TEMPERATURE
    max_tokens = max_tokens or settings.OPENAI_MAX_TOKENS
    
    try:
        if settings.LLM_PROVIDER == "azure":
            client = get_azure_openai_client()
            # Build parameters - only include streaming if True
            params = {
                'model': model,
                'messages': messages,
            }
            if temperature is not None:
                params['temperature'] = temperature
            if max_tokens is not None:
                params['max_tokens'] = max_tokens
            if streaming:
                params['stream'] = True  # Use 'stream' instead of 'streaming'
            
            response = client.chat.completions.create(**params)
        else:  # OpenAI direct
            client = get_openai_client()
            # Build parameters - only include streaming if True (some OpenAI versions don't accept False)
            params = {
                'model': model,
                'messages': messages,
            }
            if temperature is not None:
                params['temperature'] = temperature
            if max_tokens is not None:
                params['max_tokens'] = max_tokens
            if streaming:
                params['stream'] = True  # Use 'stream' instead of 'streaming'
            
            response = client.chat.completions.create(**params)
        
        if streaming:
            return response  # Return stream object
        else:
            return response.choices[0].message.content
    except (APIConnectionError, httpx.TimeoutException, TimeoutError) as e:
        logger.error(f"OpenAI API connection/timeout error during chat completion: {e}")
        raise
    except APIStatusError as e:
        logger.error(f"OpenAI API status error during chat completion: {e.status_code} - {e.response}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during chat completion: {e}")
        raise

