"""
Translation Service
Provides multilingual support using Google Cloud Translation API and other translation services.
"""
import logging
import os
from typing import Dict, List, Optional, Any
import httpx

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translating text between languages."""
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese (Simplified)',
        'zh-TW': 'Chinese (Traditional)',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'pa': 'Punjabi',
        'bn': 'Bengali',
        'ur': 'Urdu',
        'ta': 'Tamil',
        'te': 'Telugu',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'nl': 'Dutch',
        'pl': 'Polish',
        'tr': 'Turkish',
        'vi': 'Vietnamese',
        'th': 'Thai',
        'id': 'Indonesian',
        'ms': 'Malay',
        'fil': 'Filipino'
    }
    
    def __init__(self):
        """Initialize translation service."""
        self.google_api_key = os.getenv("GOOGLE_TRANSLATE_API_KEY", "")
        self.google_project_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "")
        
        # HTTP client
        self.client = httpx.AsyncClient(timeout=30.0)
        
        logger.info("Translation service initialized")
    
    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'es', 'fr', 'hi')
            source_language: Source language code (auto-detect if None)
            
        Returns:
            Dictionary with translated text and metadata
        """
        if not text or not text.strip():
            return {
                "success": False,
                "error": "Empty text provided"
            }
        
        if target_language not in self.SUPPORTED_LANGUAGES:
            return {
                "success": False,
                "error": f"Unsupported target language: {target_language}"
            }
        
        # If target is same as source, no translation needed
        if source_language and source_language == target_language:
            return {
                "success": True,
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "no_translation_needed": True
            }
        
        try:
            # Try Google Cloud Translation API first
            if self.google_api_key:
                return await self._translate_google_api(text, target_language, source_language)
            else:
                logger.warning("Google Translate API key not configured, using mock translation")
                return self._mock_translation(text, target_language, source_language)
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_text": text
            }
    
    async def _translate_google_api(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str]
    ) -> Dict[str, Any]:
        """Translate using Google Cloud Translation API."""
        try:
            url = "https://translation.googleapis.com/language/translate/v2"
            
            params = {
                "key": self.google_api_key,
                "q": text,
                "target": target_language
            }
            
            if source_language:
                params["source"] = source_language
            
            response = await self.client.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" in data and "translations" in data["data"]:
                translation = data["data"]["translations"][0]
                detected_source = translation.get("detectedSourceLanguage", source_language)
                
                return {
                    "success": True,
                    "translated_text": translation["translatedText"],
                    "source_language": detected_source,
                    "target_language": target_language,
                    "service": "Google Cloud Translation"
                }
            else:
                raise Exception("Invalid response from Google Translate API")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Google Translate API error: {e.response.status_code} - {e.response.text}")
            return self._mock_translation(text, target_language, source_language)
        except Exception as e:
            logger.error(f"Google Translate API request failed: {e}")
            return self._mock_translation(text, target_language, source_language)
    
    def _mock_translation(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str]
    ) -> Dict[str, Any]:
        """Mock translation for demonstration when API is not configured."""
        logger.info(f"Using mock translation to {target_language}")
        
        # Simple mock: add language prefix
        target_lang_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)
        mock_text = f"[{target_lang_name}] {text}"
        
        return {
            "success": True,
            "translated_text": mock_text,
            "source_language": source_language or "en",
            "target_language": target_language,
            "service": "Mock Translation (API not configured)",
            "note": "Configure Google Translate API key for real translations"
        }
    
    async def translate_batch(
        self,
        texts: List[str],
        target_language: str,
        source_language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple texts at once.
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if None)
            
        Returns:
            List of translation results
        """
        results = []
        
        for text in texts:
            result = await self.translate_text(text, target_language, source_language)
            results.append(result)
        
        return results
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with detected language and confidence
        """
        if not self.google_api_key:
            return {
                "success": True,
                "language": "en",
                "confidence": 0.5,
                "service": "Mock Detection (API not configured)"
            }
        
        try:
            url = "https://translation.googleapis.com/language/translate/v2/detect"
            
            params = {
                "key": self.google_api_key,
                "q": text
            }
            
            response = await self.client.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if "data" in data and "detections" in data["data"]:
                detection = data["data"]["detections"][0][0]
                
                return {
                    "success": True,
                    "language": detection["language"],
                    "confidence": detection.get("confidence", 1.0),
                    "service": "Google Cloud Translation"
                }
            else:
                raise Exception("Invalid response from Google Translate API")
                
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get dictionary of supported language codes and names."""
        return self.SUPPORTED_LANGUAGES.copy()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Singleton instance
_translation_service = None

def get_translation_service() -> TranslationService:
    """Get or create the translation service singleton."""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
