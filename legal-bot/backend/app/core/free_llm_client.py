"""
Free LLM Provider Support for PLAZA-AI
Supports: Ollama (local, 100% free), Google Gemini (free tier), Hugging Face (free tier)
"""
import logging
from typing import List, Optional, Dict, Any
import httpx
import os

logger = logging.getLogger(__name__)

# Global clients
_ollama_client = None
_gemini_client = None
_huggingface_client = None


def get_ollama_client(base_url: str = "http://localhost:11434"):
    """Get or create Ollama client (100% free, runs locally)."""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = {"base_url": base_url}
        logger.info(f"Ollama client configured: {base_url}")
    return _ollama_client


def get_gemini_client(api_key: Optional[str] = None):
    """Get or create Google Gemini client (free tier available)."""
    global _gemini_client
    if _gemini_client is None:
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini provider")
        _gemini_client = {"api_key": api_key}
        logger.info("Google Gemini client initialized (free tier available)")
    return _gemini_client


def get_huggingface_client(api_key: Optional[str] = None):
    """Get or create Hugging Face Inference API client (free tier available)."""
    global _huggingface_client
    if _huggingface_client is None:
        api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY is required for Hugging Face provider")
        _huggingface_client = {"api_key": api_key}
        logger.info("Hugging Face Inference API client initialized (free tier available)")
    return _huggingface_client


def chat_completion_ollama(
    messages: List[dict],
    model: str = "llama3.2",  # Free, fast model
    temperature: float = 0.2,
    max_tokens: int = 1500,
    base_url: str = "http://localhost:11434",
    timeout: int = 60  # Ollama can be slower locally
) -> str:
    """
    Generate chat completion using Ollama (100% free, runs locally).
    
    Install: https://ollama.ai
    Models: llama3.2, mistral, phi3, etc. (all free)
    """
    try:
        # Convert messages to Ollama format
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
        
        prompt += "Assistant:"
        
        # Call Ollama API
        response = httpx.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            },
            timeout=timeout
        )
        response.raise_for_status()
        result = response.json()
        
        return result.get("response", "").strip()
        
    except httpx.TimeoutException:
        logger.error(f"Ollama request timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        raise


def chat_completion_gemini(
    messages: List[dict],
    model: str = "gemini-1.5-flash",  # Free tier model
    temperature: float = 0.2,
    max_tokens: int = 1500,
    api_key: Optional[str] = None,
    timeout: int = 30
) -> str:
    """
    Generate chat completion using Google Gemini (free tier: 15 RPM, 1M tokens/day).
    
    Get API key: https://makersuite.google.com/app/apikey
    Free tier limits: 15 requests/minute, 1M tokens/day
    """
    try:
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        # Convert messages to Gemini format
        gemini_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            # Gemini uses "user" and "model" instead of "assistant"
            if role == "assistant":
                role = "model"
            gemini_messages.append({"role": role, "parts": [{"text": content}]})
        
        # Call Gemini API
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
            json={
                "contents": gemini_messages,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            },
            timeout=timeout
        )
        response.raise_for_status()
        result = response.json()
        
        # Extract response text
        if "candidates" in result and len(result["candidates"]) > 0:
            content = result["candidates"][0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "").strip()
        
        raise ValueError("No response from Gemini API")
        
    except httpx.TimeoutException:
        logger.error(f"Gemini request timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise


def chat_completion_huggingface(
    messages: List[dict],
    model: str = "mistralai/Mistral-7B-Instruct-v0.2",  # Free model
    temperature: float = 0.2,
    max_tokens: int = 1500,
    api_key: Optional[str] = None,
    timeout: int = 30
) -> str:
    """
    Generate chat completion using Hugging Face Inference API (free tier available).
    
    Get API key: https://huggingface.co/settings/tokens
    Free tier: Limited requests, some models free
    Models: mistralai/Mistral-7B-Instruct-v0.2, meta-llama/Llama-2-7b-chat-hf, etc.
    """
    try:
        api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY is required")
        
        # Convert messages to Hugging Face format
        # Hugging Face expects a single prompt string or chat format
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"<s>[INST] {content} [/INST]"
            elif role == "user":
                prompt += f"<s>[INST] {content} [/INST]"
            elif role == "assistant":
                prompt += f" {content} </s>"
        
        # Call Hugging Face Inference API
        headers = {"Authorization": f"Bearer {api_key}"}
        response = httpx.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens,
                    "return_full_text": False
                }
            },
            timeout=timeout
        )
        response.raise_for_status()
        result = response.json()
        
        # Extract response (format varies by model)
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").strip()
        elif isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"].strip()
        else:
            # Try to extract from any text field
            text = str(result)
            return text.strip()
        
    except httpx.TimeoutException:
        logger.error(f"Hugging Face request timed out after {timeout}s")
        raise
    except Exception as e:
        logger.error(f"Hugging Face API error: {e}")
        raise


def chat_completion_free(
    messages: List[dict],
    provider: str = "ollama",  # "ollama", "gemini", "huggingface"
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 1500,
    **kwargs
) -> str:
    """
    Unified interface for free LLM providers.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        provider: "ollama" (local, 100% free), "gemini" (free tier), "huggingface" (free tier)
        model: Model name (optional, uses defaults)
        temperature: Temperature
        max_tokens: Max tokens
        **kwargs: Provider-specific options
    
    Returns:
        Generated text response
    """
    if provider == "ollama":
        model = model or kwargs.get("ollama_model", "llama3.2")
        base_url = kwargs.get("ollama_base_url", "http://localhost:11434")
        timeout = kwargs.get("timeout", 60)
        return chat_completion_ollama(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url,
            timeout=timeout
        )
    
    elif provider == "gemini":
        model = model or kwargs.get("gemini_model", "gemini-1.5-flash")
        api_key = kwargs.get("gemini_api_key")
        timeout = kwargs.get("timeout", 30)
        return chat_completion_gemini(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            timeout=timeout
        )
    
    elif provider == "huggingface":
        model = model or kwargs.get("huggingface_model", "mistralai/Mistral-7B-Instruct-v0.2")
        api_key = kwargs.get("huggingface_api_key")
        timeout = kwargs.get("timeout", 30)
        return chat_completion_huggingface(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            timeout=timeout
        )
    
    else:
        raise ValueError(f"Unknown free provider: {provider}. Choose: ollama, gemini, huggingface")
