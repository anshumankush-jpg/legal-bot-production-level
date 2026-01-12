"""
Simple Image Upload Test
Tests if OCR is working with your images
"""

import requests
import sys
from pathlib import Path

BACKEND_URL = "http://localhost:8000"

print("=" * 60)
print("IMAGE UPLOAD & OCR TEST")
print("=" * 60)

# Step 1: Check backend
print("\nStep 1: Checking backend...")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    if response.status_code == 200:
        print("[OK] Backend is running!")
    else:
        print("[FAIL] Backend returned:", response.status_code)
        sys.exit(1)
except Exception as e:
    print("[FAIL] Backend not responding:", e)
    print("\nRun this: .\\CLEAN_START.bat")
    sys.exit(1)

# Step 2: Find test image
print("\nStep 2: Finding test image...")
test_images = [
    Path("C:/Users/anshu/Downloads/assiii/artillty/LK INSIGHT 1 .png"),
    Path("C:/Users/anshu/Downloads/assiii/artillty/BETTER _PIXEL _LK_!.png"),
]

image_path = None
for img in test_images:
    if img.exists():
        image_path = img
        print(f"[OK] Found: {img.name}")
        break

if not image_path:
    print("[FAIL] No test images found")
    print("\nPlease enter path to an image:")
    user_input = input("Image path: ").strip()
    if user_input:
        image_path = Path(user_input)
        if not image_path.exists():
            print("[FAIL] File not found")
            sys.exit(1)
    else:
        sys.exit(1)

# Step 3: Upload image
print(f"\nStep 3: Uploading {image_path.name}...")
print(f"Size: {image_path.stat().st_size / 1024:.1f} KB")
print("Processing... (may take 5-10 seconds)")

try:
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/png')}
        data = {'user_id': 'test_user'}
        
        response = requests.post(
            f"{BACKEND_URL}/api/artillery/upload",
            files=files,
            data=data,
            timeout=30
        )
    
    if response.status_code == 200:
        result = response.json()
        print("\n[SUCCESS] Upload complete!")
        print(f"  Doc ID: {result.get('doc_id', 'N/A')}")
        print(f"  Chunks: {result.get('chunks_indexed', 0)}")
        print(f"  OCR: {result.get('ocr_extracted', 'N/A')}")
        print(f"  Time: {result.get('processing_time', 0):.2f}s")
        
        doc_id = result.get('doc_id')
        
        # Step 4: Test chat
        print("\nStep 4: Testing chatbot...")
        chat_request = {
            "message": "What text was extracted from the image?",
            "doc_ids": [doc_id],
            "max_results": 5
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/artillery/chat",
            json=chat_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            print(f"\n[OK] Chatbot response:")
            print(f"  {answer[:300]}...")
            print(f"\n  Chunks used: {result.get('chunks_used', 0)}")
            print(f"  Confidence: {result.get('confidence', 0):.2f}")
        else:
            print(f"[FAIL] Chat failed: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE!")
        print("=" * 60)
        print("\nYour OCR system is working!")
        print("Try it in the browser:")
        print("  1. Open http://localhost:4201")
        print("  2. Drag & drop an image")
        print("  3. Ask questions!")
        
    else:
        print(f"\n[FAIL] Upload failed: {response.status_code}")
        print(f"Error: {response.text[:500]}")
        
        if "tesseract" in response.text.lower():
            print("\n[FIX] Tesseract issue detected!")
            print("Run: .\\CLEAN_START.bat")

except requests.exceptions.Timeout:
    print("\n[FAIL] Upload timed out!")
    print("File might be too large or backend is slow")
    print("\nTry:")
    print("  1. Use a smaller image")
    print("  2. Restart: .\\CLEAN_START.bat")

except Exception as e:
    print(f"\n[FAIL] Error: {e}")
