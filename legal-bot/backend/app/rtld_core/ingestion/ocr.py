"""
OCR functionality for image processing and offence number extraction
"""

import re
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple, List
import logging

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

from ..schemas import OffenceExtractionResult

logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    OCR processor for extracting text from images and documents
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize OCR processor

        Args:
            tesseract_cmd: Path to tesseract executable (optional)
        """
        if TESSERACT_AVAILABLE:
            if tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        else:
            logger.warning("Tesseract not available. OCR functionality disabled.")

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using OCR

        Args:
            image_path: Path to image file

        Returns:
            Extracted text
        """
        if not TESSERACT_AVAILABLE:
            raise ImportError("Tesseract not available. Install with: pip install pytesseract")

        try:
            logger.info(f"Performing OCR on image: {image_path}")

            # Open image
            image = Image.open(image_path)

            # Preprocessing for better OCR
            # Convert to grayscale if needed
            if image.mode != 'L':
                image = image.convert('L')

            # Extract text
            text = pytesseract.image_to_string(image)

            logger.info(f"OCR extracted {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return ""

    def extract_text_from_pdf_images(self, pdf_path: str) -> str:
        """
        Extract text from image-based PDF pages

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text from image pages
        """
        if not PDFPLUMBER_AVAILABLE or not TESSERACT_AVAILABLE:
            logger.warning("PDF image OCR not available")
            return ""

        try:
            logger.info(f"Extracting text from PDF images: {pdf_path}")
            text_parts = []

            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    try:
                        # Check if page has text
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            # Page has extractable text, use it
                            text_parts.append(page_text)
                        else:
                            # Page is image-based, use OCR
                            logger.info(f"Page {i} appears to be image-based, using OCR")

                            # Convert page to image
                            page_image = page.to_image(resolution=300)
                            pil_image = page_image.original

                            # OCR the image
                            ocr_text = pytesseract.image_to_string(pil_image)
                            if ocr_text.strip():
                                text_parts.append(ocr_text)

                    except Exception as e:
                        logger.warning(f"Error processing PDF page {i}: {e}")
                        continue

            full_text = "\n\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from PDF with OCR")
            return full_text

        except Exception as e:
            logger.error(f"PDF OCR failed for {pdf_path}: {e}")
            return ""

    def process_file(self, file_path: str) -> Tuple[str, Optional[str]]:
        """
        Process a file and extract text and offence number

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (extracted_text, detected_offence_number)
        """
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()

        extracted_text = ""
        detected_offence_number = None

        try:
            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                # Image file - use OCR
                extracted_text = self.extract_text_from_image(str(file_path))

            elif file_ext == '.pdf':
                # PDF file - try direct text extraction first, then OCR
                if PDFPLUMBER_AVAILABLE:
                    try:
                        with pdfplumber.open(file_path) as pdf:
                            for page in pdf.pages:
                                page_text = page.extract_text() or ""
                                extracted_text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"PDF text extraction failed: {e}, falling back to OCR")
                        extracted_text = self.extract_text_from_pdf_images(str(file_path))
                else:
                    logger.warning("PDF processing not available, using OCR")
                    extracted_text = self.extract_text_from_pdf_images(str(file_path))

            else:
                # For other file types, we'll handle them in the parser
                logger.info(f"File type {file_ext} will be handled by document parser")
                return "", None

            # Extract offence number from the text
            if extracted_text.strip():
                offence_extractor = OffenceNumberExtractor()
                result = offence_extractor.extract_offence_number(extracted_text)
                detected_offence_number = result.offence_number if result.confidence > 0.5 else None

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            extracted_text = ""
            detected_offence_number = None

        return extracted_text, detected_offence_number


class OffenceNumberExtractor:
    """
    Extract offence numbers from text using pattern matching
    """

    # Patterns for offence numbers (customize based on jurisdiction)
    OFFENCE_PATTERNS = [
        # Ontario style: "Offence No. 123456789"
        r'(?:offence|offense)\s*(?:no\.?|number)\s*[:\-]?\s*([A-Z0-9\-]+)',

        # Notice/Ticket numbers
        r'(?:notice|ticket)\s*(?:no\.?|number)\s*[:\-]?\s*([A-Z0-9\-]+)',

        # Direct number patterns (Ontario has 9-12 digit numbers often)
        r'\b(\d{9,12})\b',

        # Alpha-numeric patterns
        r'\b([A-Z]{1,3}\d{6,10})\b',

        # Common prefixes
        r'\b(ON\d+|QC\d+|BC\d+|AB\d+|MB\d+|SK\d+|NB\d+|NS\d+|PE\d+|NL\d+)\b',
    ]

    CONFIDENCE_WEIGHTS = {
        'explicit_offence': 1.0,  # "Offence No. 123"
        'notice_ticket': 0.9,     # "Notice No. 123"
        'numeric_only': 0.6,      # Just numbers
        'alpha_numeric': 0.7,     # Mixed letters/numbers
        'jurisdiction_prefix': 0.8,  # Province prefixes
    }

    def extract_offence_number(self, text: str) -> OffenceExtractionResult:
        """
        Extract offence number from text

        Args:
            text: Text to search

        Returns:
            OffenceExtractionResult with extracted number and confidence
        """
        if not text or not text.strip():
            return OffenceExtractionResult()

        text = text.upper()  # Case insensitive matching
        candidates = []

        for pattern_idx, pattern in enumerate(self.OFFENCE_PATTERNS):
            matches = re.findall(pattern, text, re.IGNORECASE)
            pattern_type = self._get_pattern_type(pattern_idx)

            for match in matches:
                match_str = str(match).strip()

                # Filter out obviously invalid matches
                if self._is_valid_offence_number(match_str):
                    confidence = self._calculate_confidence(match_str, pattern_type, text)
                    candidates.append({
                        'number': match_str,
                        'confidence': confidence,
                        'pattern_type': pattern_type
                    })

        if not candidates:
            return OffenceExtractionResult()

        # Sort by confidence and return best match
        candidates.sort(key=lambda x: x['confidence'], reverse=True)
        best = candidates[0]

        return OffenceExtractionResult(
            offence_number=best['number'],
            confidence=best['confidence'],
            extraction_method="ocr"
        )

    def _get_pattern_type(self, pattern_idx: int) -> str:
        """Get pattern type name"""
        pattern_types = [
            'explicit_offence',
            'notice_ticket',
            'numeric_only',
            'alpha_numeric',
            'jurisdiction_prefix'
        ]
        return pattern_types[pattern_idx] if pattern_idx < len(pattern_types) else 'unknown'

    def _is_valid_offence_number(self, number: str) -> bool:
        """
        Check if a string looks like a valid offence number
        """
        # Remove common separators
        clean_number = re.sub(r'[\s\-_]', '', number)

        # Must have at least 6 characters
        if len(clean_number) < 6:
            return False

        # Must contain at least some digits
        if not re.search(r'\d', clean_number):
            return False

        # Shouldn't be too long (probably not a valid offence number)
        if len(clean_number) > 12:
            return False

        # Avoid obviously wrong matches (like dates, phone numbers, etc.)
        if re.match(r'^\d{4}[\-/]\d{1,2}[\-/]\d{1,2}', number):  # Date pattern
            return False

        if re.match(r'^\d{10,11}$', clean_number):  # Phone number
            return False

        return True

    def _calculate_confidence(self, number: str, pattern_type: str, full_text: str) -> float:
        """
        Calculate confidence score for extracted number
        """
        base_confidence = self.CONFIDENCE_WEIGHTS.get(pattern_type, 0.5)

        # Boost confidence based on context
        context_words = ['offence', 'offense', 'ticket', 'notice', 'violation', 'summons', 'citation']
        context_boost = 0.0

        number_pos = full_text.upper().find(number.upper())
        if number_pos >= 0:
            # Check surrounding context (100 chars before/after)
            start = max(0, number_pos - 100)
            end = min(len(full_text), number_pos + len(number) + 100)
            context = full_text[start:end].upper()

            for word in context_words:
                if word.upper() in context:
                    context_boost += 0.1
                    break

        # Length appropriateness (Ontario offence numbers are often 9-12 digits)
        clean_number = re.sub(r'[\s\-_]', '', number)
        if 9 <= len(clean_number) <= 12 and clean_number.isdigit():
            length_boost = 0.2
        else:
            length_boost = 0.0

        final_confidence = min(1.0, base_confidence + context_boost + length_boost)
        return final_confidence


# Global instances
_ocr_processor: Optional[OCRProcessor] = None
_offence_extractor: Optional[OffenceNumberExtractor] = None


def get_ocr_processor(tesseract_cmd: Optional[str] = None) -> OCRProcessor:
    """Get or create OCR processor instance"""
    global _ocr_processor
    if _ocr_processor is None:
        _ocr_processor = OCRProcessor(tesseract_cmd=tesseract_cmd)
    return _ocr_processor


def get_offence_extractor() -> OffenceNumberExtractor:
    """Get or create offence extractor instance"""
    global _offence_extractor
    if _offence_extractor is None:
        _offence_extractor = OffenceNumberExtractor()
    return _offence_extractor


def extract_offence_number(text: str) -> OffenceExtractionResult:
    """
    Convenience function to extract offence number from text

    Args:
        text: Text to search

    Returns:
        Extraction result
    """
    extractor = get_offence_extractor()
    return extractor.extract_offence_number(text)