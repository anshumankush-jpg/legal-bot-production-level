"""
Debug script to trace the upload flow
"""
import sys
import os
sys.path.insert(0, 'backend')

# Set UTF-8 encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Import the document processor
from artillery.document_processor import ArtilleryDocumentProcessor, OCR_AVAILABLE

print("=" * 60)
print("DEBUGGING ARTILLERY DOCUMENT PROCESSOR")
print("=" * 60)
print(f"OCR_AVAILABLE: {OCR_AVAILABLE}")
print()

if OCR_AVAILABLE:
    import pytesseract
    print(f"pytesseract.pytesseract.tesseract_cmd: {pytesseract.pytesseract.tesseract_cmd}")
    try:
        version = pytesseract.get_tesseract_version()
        print(f"Tesseract version: {version}")
    except Exception as e:
        print(f"[ERROR] Tesseract not working: {e}")
else:
    print("[ERROR] OCR_AVAILABLE is False!")

print()
print("=" * 60)
print("TESTING IMAGE PROCESSING")
print("=" * 60)

# Find test image
from pathlib import Path
test_images = list(Path('.').rglob('*.png'))
if not test_images:
    print("[ERROR] No test images found!")
    sys.exit(1)

test_image = test_images[0]
print(f"Test image: {test_image}")
print()

# Create processor and process image
processor = ArtilleryDocumentProcessor()
print("Processing image...")
result = processor.process_document(str(test_image))

print()
print("RESULTS:")
print(f"  Text chunks: {len(result['text_chunks'])}")
print(f"  Images: {len(result['images'])}")
print()

if result['text_chunks']:
    for i, chunk in enumerate(result['text_chunks'][:3], 1):  # Show first 3
        content = chunk['content']
        print(f"Chunk {i}:")
        print(f"  Length: {len(content)} chars")
        print(f"  Preview: {content[:150]}...")
        print()

print("=" * 60)
