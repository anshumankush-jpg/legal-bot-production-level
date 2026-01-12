"""
Enhanced OCR Processing with Advanced Features
Includes image preprocessing, pattern recognition, and confidence scoring
"""

import os
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

# Try to import OCR libraries
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import cv2
    OCR_AVAILABLE = True
    
    # Configure Tesseract path for Windows
    if os.name == 'nt':
        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        if os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.info(f"[ENHANCED_OCR] Tesseract configured at: {tesseract_path}")
except ImportError as e:
    OCR_AVAILABLE = False
    logger.warning(f"[ENHANCED_OCR] OCR libraries not available: {e}")


class EnhancedOCR:
    """
    Enhanced OCR processor with:
    - Image preprocessing (contrast, sharpening, denoising)
    - Automatic rotation correction
    - Pattern recognition (dates, codes, numbers)
    - Confidence scoring
    - Multi-region text extraction
    - Error handling and user feedback
    """
    
    def __init__(self):
        self.min_confidence = 60  # Minimum confidence threshold
        self.date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',     # YYYY-MM-DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # Month DD, YYYY
        ]
        self.code_patterns = [
            r'\b[A-Z]{2,4}\d{3,6}\b',  # ABC123, CODE456
            r'\b\d{3,}-\d{3,}\b',       # 123-456
            r'\b[A-Z0-9]{6,}\b',        # Alphanumeric codes
        ]
        
    def preprocess_image(self, image: Image.Image) -> List[Image.Image]:
        """
        Preprocess image to improve OCR accuracy.
        Returns multiple preprocessed versions for best results.
        """
        processed_images = []
        
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Original image
            processed_images.append(('original', image))
            
            # High contrast version
            enhancer = ImageEnhance.Contrast(image)
            high_contrast = enhancer.enhance(2.0)
            processed_images.append(('high_contrast', high_contrast))
            
            # Sharpened version
            sharpened = image.filter(ImageFilter.SHARPEN)
            processed_images.append(('sharpened', sharpened))
            
            # Grayscale with threshold (for text documents)
            gray = image.convert('L')
            # Apply threshold to make text clearer
            threshold = 128
            gray_threshold = gray.point(lambda x: 0 if x < threshold else 255)
            processed_images.append(('grayscale_threshold', gray_threshold))
            
            # Denoised version (if cv2 available)
            try:
                import cv2
                img_array = np.array(image)
                denoised = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
                denoised_img = Image.fromarray(denoised)
                processed_images.append(('denoised', denoised_img))
            except:
                pass
            
            logger.info(f"[ENHANCED_OCR] Created {len(processed_images)} preprocessed versions")
            
        except Exception as e:
            logger.error(f"[ENHANCED_OCR] Preprocessing error: {e}")
            processed_images = [('original', image)]
        
        return processed_images
    
    def detect_rotation(self, image: Image.Image) -> float:
        """
        Detect image rotation using OSD (Orientation and Script Detection).
        Returns rotation angle in degrees.
        """
        try:
            osd = pytesseract.image_to_osd(image)
            rotation = int(re.search(r'Rotate: (\d+)', osd).group(1))
            logger.info(f"[ENHANCED_OCR] Detected rotation: {rotation} degrees")
            return rotation
        except Exception as e:
            logger.debug(f"[ENHANCED_OCR] Could not detect rotation: {e}")
            return 0
    
    def correct_rotation(self, image: Image.Image) -> Image.Image:
        """
        Automatically correct image rotation.
        """
        try:
            rotation = self.detect_rotation(image)
            if rotation != 0:
                image = image.rotate(-rotation, expand=True)
                logger.info(f"[ENHANCED_OCR] Corrected rotation by {rotation} degrees")
        except Exception as e:
            logger.debug(f"[ENHANCED_OCR] Rotation correction skipped: {e}")
        
        return image
    
    def extract_with_confidence(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text with confidence scores for each word.
        """
        try:
            # Get detailed OCR data with confidence scores
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            words = []
            confidences = []
            
            for i, word in enumerate(data['text']):
                if word.strip():  # Skip empty strings
                    conf = int(data['conf'][i])
                    if conf > 0:  # Skip -1 confidence values
                        words.append(word)
                        confidences.append(conf)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': ' '.join(words),
                'words': words,
                'confidences': confidences,
                'avg_confidence': avg_confidence,
                'low_confidence_words': [w for w, c in zip(words, confidences) if c < self.min_confidence]
            }
            
        except Exception as e:
            logger.error(f"[ENHANCED_OCR] Confidence extraction error: {e}")
            return {
                'text': '',
                'words': [],
                'confidences': [],
                'avg_confidence': 0,
                'low_confidence_words': []
            }
    
    def extract_structured_fields(self, text: str) -> Dict[str, List[str]]:
        """
        Extract structured fields like dates, codes, numbers using pattern recognition.
        """
        fields = {
            'dates': [],
            'codes': [],
            'numbers': [],
            'emails': [],
            'phones': []
        }
        
        # Extract dates
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            fields['dates'].extend(matches)
        
        # Extract codes
        for pattern in self.code_patterns:
            matches = re.findall(pattern, text)
            fields['codes'].extend(matches)
        
        # Extract numbers (amounts, IDs, etc.)
        number_pattern = r'\b\d{3,}\b'
        fields['numbers'] = re.findall(number_pattern, text)
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        fields['emails'] = re.findall(email_pattern, text)
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        fields['phones'] = re.findall(phone_pattern, text)
        
        # Remove duplicates
        for key in fields:
            fields[key] = list(set(fields[key]))
        
        return fields
    
    def find_labeled_fields(self, text: str) -> Dict[str, str]:
        """
        Find fields with labels like "Code Date:", "Invoice Number:", etc.
        """
        labeled_fields = {}
        
        # Common label patterns
        label_patterns = [
            (r'(?:code\s*date|date\s*code)[:\s]+([^\n]+)', 'code_date'),
            (r'(?:invoice|order)\s*(?:number|#)[:\s]+([^\n]+)', 'invoice_number'),
            (r'(?:expiration|expiry)\s*date[:\s]+([^\n]+)', 'expiration_date'),
            (r'(?:order|purchase)\s*date[:\s]+([^\n]+)', 'order_date'),
            (r'(?:total|amount)[:\s]+\$?([0-9,]+\.?\d*)', 'amount'),
            (r'(?:customer|client)\s*(?:name|id)[:\s]+([^\n]+)', 'customer'),
        ]
        
        for pattern, field_name in label_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                labeled_fields[field_name] = matches[0].strip()
        
        return labeled_fields
    
    def process_image_enhanced(self, image_path: str) -> Dict[str, Any]:
        """
        Enhanced OCR processing with all features.
        
        Returns:
            Dict containing:
            - text: Extracted text
            - confidence: Average confidence score
            - structured_fields: Dates, codes, numbers, etc.
            - labeled_fields: Fields with labels
            - warnings: List of issues found
            - suggestions: Suggestions for improvement
        """
        if not OCR_AVAILABLE:
            return {
                'text': '',
                'confidence': 0,
                'error': 'OCR libraries not available. Please install pytesseract and Pillow.',
                'warnings': ['OCR not configured'],
                'suggestions': ['Install Tesseract OCR and required Python libraries']
            }
        
        result = {
            'text': '',
            'confidence': 0,
            'structured_fields': {},
            'labeled_fields': {},
            'warnings': [],
            'suggestions': [],
            'preprocessing_used': None
        }
        
        try:
            # Load image
            image = Image.open(image_path)
            original_size = image.size
            
            # Check image quality
            if min(original_size) < 300:
                result['warnings'].append(f"Low resolution detected ({original_size[0]}x{original_size[1]})")
                result['suggestions'].append("For better OCR accuracy, use images with at least 300 DPI or 1000x1000 pixels")
            
            # Correct rotation
            image = self.correct_rotation(image)
            
            # Preprocess image (create multiple versions)
            preprocessed_images = self.preprocess_image(image)
            
            # Try OCR on each preprocessed version and pick the best
            best_result = None
            best_confidence = 0
            
            for name, proc_image in preprocessed_images:
                try:
                    ocr_result = self.extract_with_confidence(proc_image)
                    
                    if ocr_result['avg_confidence'] > best_confidence:
                        best_confidence = ocr_result['avg_confidence']
                        best_result = ocr_result
                        result['preprocessing_used'] = name
                        
                except Exception as e:
                    logger.debug(f"[ENHANCED_OCR] Failed on {name} version: {e}")
                    continue
            
            if best_result:
                result['text'] = best_result['text']
                result['confidence'] = best_result['avg_confidence']
                
                # Extract structured fields
                result['structured_fields'] = self.extract_structured_fields(result['text'])
                
                # Find labeled fields
                result['labeled_fields'] = self.find_labeled_fields(result['text'])
                
                # Add warnings for low confidence
                if best_result['avg_confidence'] < self.min_confidence:
                    result['warnings'].append(f"Low OCR confidence ({best_result['avg_confidence']:.1f}%)")
                    result['suggestions'].append("Try rescanning with better lighting or higher resolution")
                
                if best_result['low_confidence_words']:
                    result['warnings'].append(f"{len(best_result['low_confidence_words'])} words detected with low confidence")
                    result['suggestions'].append("Some text may be unclear. Consider uploading a clearer image")
                
                # Check for missing common fields
                if not result['structured_fields']['dates'] and 'date' in result['text'].lower():
                    result['warnings'].append("Date mentioned but not clearly detected")
                    result['suggestions'].append("Ensure dates are in standard format (MM/DD/YYYY or YYYY-MM-DD)")
                
                logger.info(f"[ENHANCED_OCR] Extracted {len(result['text'])} characters with {result['confidence']:.1f}% confidence")
                logger.info(f"[ENHANCED_OCR] Found: {len(result['structured_fields']['dates'])} dates, {len(result['structured_fields']['codes'])} codes")
                
            else:
                result['error'] = "Could not extract text from image"
                result['warnings'].append("OCR failed on all preprocessing attempts")
                result['suggestions'].extend([
                    "Ensure the image is clear and not blurry",
                    "Check that text is properly oriented (not rotated)",
                    "Try increasing image resolution or contrast"
                ])
            
        except Exception as e:
            logger.error(f"[ENHANCED_OCR] Processing error: {e}")
            result['error'] = str(e)
            result['warnings'].append(f"OCR processing failed: {e}")
            result['suggestions'].append("Try uploading a different image or check image format")
        
        return result
    
    def format_ocr_response(self, ocr_result: Dict[str, Any], filename: str) -> str:
        """
        Format OCR results into a user-friendly response.
        """
        lines = []
        lines.append(f"📄 OCR Analysis: {filename}")
        lines.append("")
        
        if ocr_result.get('error'):
            lines.append(f"❌ Error: {ocr_result['error']}")
        else:
            lines.append(f"✅ Text extracted successfully")
            lines.append(f"📊 Confidence: {ocr_result['confidence']:.1f}%")
            lines.append(f"📝 Characters: {len(ocr_result['text'])}")
            
            if ocr_result.get('preprocessing_used'):
                lines.append(f"🔧 Best preprocessing: {ocr_result['preprocessing_used']}")
            
            lines.append("")
            
            # Show structured fields
            if ocr_result.get('structured_fields'):
                fields = ocr_result['structured_fields']
                if any(fields.values()):
                    lines.append("📋 Detected Fields:")
                    if fields['dates']:
                        lines.append(f"  📅 Dates: {', '.join(fields['dates'][:5])}")
                    if fields['codes']:
                        lines.append(f"  🔢 Codes: {', '.join(fields['codes'][:5])}")
                    if fields['numbers']:
                        lines.append(f"  #️⃣ Numbers: {', '.join(fields['numbers'][:5])}")
                    lines.append("")
            
            # Show labeled fields
            if ocr_result.get('labeled_fields'):
                lines.append("🏷️ Labeled Fields:")
                for label, value in ocr_result['labeled_fields'].items():
                    lines.append(f"  • {label.replace('_', ' ').title()}: {value}")
                lines.append("")
        
        # Show warnings
        if ocr_result.get('warnings'):
            lines.append("⚠️ Warnings:")
            for warning in ocr_result['warnings']:
                lines.append(f"  • {warning}")
            lines.append("")
        
        # Show suggestions
        if ocr_result.get('suggestions'):
            lines.append("💡 Suggestions:")
            for suggestion in ocr_result['suggestions']:
                lines.append(f"  • {suggestion}")
            lines.append("")
        
        # Show text preview
        if ocr_result.get('text'):
            preview = ocr_result['text'][:300]
            lines.append("📄 Text Preview:")
            lines.append(preview + ("..." if len(ocr_result['text']) > 300 else ""))
        
        return '\n'.join(lines)


# Global instance
_enhanced_ocr_instance = None

def get_enhanced_ocr() -> EnhancedOCR:
    """Get or create global EnhancedOCR instance."""
    global _enhanced_ocr_instance
    if _enhanced_ocr_instance is None:
        _enhanced_ocr_instance = EnhancedOCR()
    return _enhanced_ocr_instance
