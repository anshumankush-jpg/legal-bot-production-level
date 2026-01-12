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


def reset_openai_clients():
    """Reset cached OpenAI clients - useful for testing or after configuration changes."""
    global _openai_client, _azure_openai_client
    _openai_client = None
    _azure_openai_client = None
    logger.info("OpenAI client cache reset.")


def get_openai_client():
    """
    Get or create OpenAI client (direct API).
    """
    global _openai_client
    # Force recreation if client exists but might have been created with proxies
    # This ensures we use the fixed version after code updates
    if _openai_client is None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'")
        import httpx
        
        # Create a custom httpx client that filters out 'proxies' argument
        # This is needed because OpenAI library internally tries to pass 'proxies' to httpx,
        # but newer httpx versions don't accept it
        class FilteredHttpxClient(httpx.Client):
            def __init__(self, *args, **kwargs):
                # Remove 'proxies' if present - it's not supported in newer httpx versions
                if 'proxies' in kwargs:
                    logger.warning("Filtering out 'proxies' argument from httpx client (not supported)")
                    del kwargs['proxies']
                super().__init__(*args, **kwargs)
        
        # Create httpx client with timeout, explicitly excluding proxies
        http_client = FilteredHttpxClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            # Do NOT pass proxies - it's not supported
        )
        
        # Build client kwargs - explicitly only include supported arguments
        client_kwargs = {
            "api_key": settings.OPENAI_API_KEY,
            "http_client": http_client,  # Use our custom client that filters proxies
            "timeout": 30.0  # Also set timeout on OpenAI client
        }
        
        # CRITICAL: Explicitly ensure proxies is NOT in kwargs
        # Remove it if it somehow got added
        if 'proxies' in client_kwargs:
            logger.warning("Removing 'proxies' from client_kwargs - not supported by OpenAI SDK")
            del client_kwargs['proxies']
        
        # Explicitly check and remove proxies if it exists in settings (from env var)
        if hasattr(settings, 'proxies') or hasattr(settings, 'OPENAI_PROXIES'):
            logger.warning("Found 'proxies' in settings - removing it as it's not supported by OpenAI SDK. "
                         "Use HTTP_PROXY/HTTPS_PROXY environment variables instead.")
        
        # Final safety check - ensure proxies is not in kwargs
        assert 'proxies' not in client_kwargs, "proxies should not be in client_kwargs!"
        
        # Configure timeout for faster failure
        # Only pass supported arguments - proxies is not supported in newer OpenAI SDK versions
        try:
            # Debug: Log what we're about to pass
            logger.debug(f"Initializing OpenAI client with kwargs: {list(client_kwargs.keys())}")
            _openai_client = OpenAI(**client_kwargs)
            logger.info("OpenAI client (direct API) initialized with 30s timeout.")
        except TypeError as e:
            if "proxies" in str(e).lower():
                import traceback
                logger.error("OpenAI client initialization failed: 'proxies' argument is not supported.")
                logger.error(f"Full traceback:\n{traceback.format_exc()}")
                logger.error(f"Client kwargs passed: {client_kwargs}")
                # Check if proxies somehow got into client_kwargs
                if 'proxies' in client_kwargs:
                    logger.error("ERROR: 'proxies' found in client_kwargs! This should not happen.")
                    del client_kwargs['proxies']
                    # Try again without proxies
                    try:
                        _openai_client = OpenAI(**client_kwargs)
                        logger.info("OpenAI client initialized successfully after removing proxies.")
                    except Exception as e2:
                        raise ValueError(
                            "OpenAI client does not support 'proxies' argument. "
                            "If you need proxy support, configure it via HTTP_PROXY/HTTPS_PROXY environment variables "
                            "or use a custom httpx client. Error: " + str(e2)
                        ) from e2
                else:
                    raise ValueError(
                        "OpenAI client does not support 'proxies' argument. "
                        "The error suggests 'proxies' is being passed from somewhere unexpected. "
                        "If you need proxy support, configure it via HTTP_PROXY/HTTPS_PROXY environment variables "
                        "or use a custom httpx client. Error: " + str(e)
                    ) from e
            raise
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

