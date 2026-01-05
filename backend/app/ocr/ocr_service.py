"""OCR service for extracting text from images (tickets, summons)."""
import logging
from pathlib import Path
from typing import Optional
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Try to import pytesseract, but handle gracefully if not available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract not installed. OCR functionality will be limited.")


class OCRService:
    """Service for extracting text from images using OCR."""
    
    def __init__(self, engine: str = "tesseract"):
        """
        Initialize OCR service.
        
        Args:
            engine: OCR engine to use (currently only 'tesseract' supported)
        """
        self.engine = engine
        self.available = TESSERACT_AVAILABLE
        
        if not self.available and engine == "tesseract":
            logger.warning(
                "Tesseract OCR not available. Install with: pip install pytesseract "
                "and ensure Tesseract binary is installed on your system."
            )
    
    def extract_text_from_image(self, file_path: str) -> str:
        """
        Extract text from an image file.
        
        Args:
            file_path: Path to image file (JPG, PNG, etc.)
            
        Returns:
            Extracted text string
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")
        
        if not self.available:
            raise RuntimeError(
                "OCR not available. Please install pytesseract:\n"
                "  pip install pytesseract\n\n"
                "And install Tesseract OCR binary:\n"
                "  Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "  Mac: brew install tesseract\n"
                "  Linux: sudo apt-get install tesseract-ocr"
            )
        
        try:
            # Check if Tesseract binary is available
            try:
                pytesseract.get_tesseract_version()
            except Exception as tesseract_error:
                error_msg = str(tesseract_error).lower()
                if 'tesseract' in error_msg or 'not found' in error_msg:
                    raise RuntimeError(
                        "Tesseract OCR binary not found.\n\n"
                        "To fix:\n"
                        "1. Download Tesseract for Windows:\n"
                        "   https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                        "2. Install it (default: C:\\Program Files\\Tesseract-OCR)\n\n"
                        "3. Add to PATH or set environment variable:\n"
                        "   $env:TESSERACT_CMD = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'\n\n"
                        f"Error details: {str(tesseract_error)}"
                    )
                raise
            
            # Preprocess image for better OCR
            image = self._preprocess_image(file_path)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image, lang='eng')
            
            if not text or not text.strip():
                logger.warning(f"OCR extracted empty text from {file_path}")
                return ""  # Return empty string instead of error
            
            logger.info(f"Extracted {len(text)} characters from {file_path}")
            return text.strip()
            
        except RuntimeError:
            raise  # Re-raise our custom errors
        except Exception as e:
            logger.error(f"Error extracting text from image {file_path}: {e}")
            raise RuntimeError(
                f"OCR extraction failed: {str(e)}\n\n"
                "Troubleshooting:\n"
                "1. Ensure Tesseract OCR is installed\n"
                "2. Check TESSERACT_CMD environment variable\n"
                "3. Verify image file is readable\n"
                "4. Try a different image format"
            )
    
    def _preprocess_image(self, file_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Preprocessed image as numpy array
        """
        # Read image
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError(f"Could not read image: {file_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get binary image
        # This helps with text recognition
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Optional: denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        return denoised


# Global singleton instance
_ocr_service: Optional[OCRService] = None


def get_ocr_service() -> OCRService:
    """Get or create the global OCR service instance."""
    global _ocr_service
    if _ocr_service is None:
        from app.core.config import settings
        _ocr_service = OCRService(engine=settings.OCR_ENGINE)
    return _ocr_service

