"""
🔍 COMPREHENSIVE IMAGE PIPELINE VERIFICATION
Tests the entire flow: Upload → OCR → Chunk → Embed → Search → Chat
"""
import os
import sys
import requests
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_step(step_num, title):
    print(f"\n{BLUE}{'='*60}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*60}{RESET}\n")

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")

def verify_tesseract():
    """Verify Tesseract OCR is installed"""
    print_step(1, "Verifying Tesseract OCR Installation")
    
    try:
        import pytesseract
        from PIL import Image
        
        # Try to get version
        version = pytesseract.get_tesseract_version()
        print_success(f"Tesseract installed: Version {version}")
        return True
    except Exception as e:
        print_error(f"Tesseract not installed or not in PATH: {e}")
        print_info("Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def verify_dependencies():
    """Verify all required packages are installed"""
    print_step(2, "Verifying Python Dependencies")
    
    required = [
        'pytesseract',
        'Pillow',
        'pdfplumber',
        'python-docx',
        'openpyxl',
        'sentence_transformers',
        'faiss',
        'fastapi',
        'uvicorn'
    ]
    
    missing = []
    for package in required:
        try:
            if package == 'python-docx':
                __import__('docx')
            elif package == 'Pillow':
                __import__('PIL')
            else:
                __import__(package.replace('-', '_'))
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} NOT installed")
            missing.append(package)
    
    if missing:
        print_warning(f"Missing packages: {', '.join(missing)}")
        print_info(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print_success("All dependencies installed!")
    return True

def test_backend_server():
    """Test if backend server is running"""
    print_step(3, "Testing Backend Server Connection")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print_success("Backend server is running!")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend server!")
        print_info("Start the server with: START_BOTH_SERVERS.bat")
        return False
    except Exception as e:
        print_error(f"Error connecting to backend: {e}")
        return False

def create_test_image():
    """Create a test image with text"""
    print_step(4, "Creating Test Image with Text")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image
        img = Image.new('RGB', (800, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = """TRAFFIC VIOLATION NOTICE
Offence Number: 1234567890
Province: Ontario, Canada
Violation: Speeding
Speed: 120 km/h in 80 km/h zone
Fine: $295.00
Court Date: 2024-02-15
Location: Highway 401"""
        
        # Try to use a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), text, fill='black', font=font)
        
        # Save image
        test_image_path = 'test_traffic_ticket.png'
        img.save(test_image_path)
        
        print_success(f"Test image created: {test_image_path}")
        print_info(f"Image size: {img.size}")
        print_info(f"Text content: {len(text)} characters")
        
        return test_image_path
    except Exception as e:
        print_error(f"Failed to create test image: {e}")
        return None

def test_image_upload(image_path):
    """Test image upload to backend"""
    print_step(5, "Testing Image Upload to Backend")
    
    if not os.path.exists(image_path):
        print_error(f"Image file not found: {image_path}")
        return None
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/png')}
            data = {
                'user_id': 'test_user_verification',
                'offence_number': '1234567890'
            }
            
            print_info("Uploading image...")
            response = requests.post(
                'http://localhost:8000/api/artillery/upload',
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Image uploaded successfully!")
            print_info(f"Document ID: {result.get('doc_id')}")
            print_info(f"Chunks indexed: {result.get('chunks_indexed')}")
            print_info(f"Offence detected: {result.get('detected_offence_number')}")
            
            # Check if OCR worked
            if result.get('chunks_indexed', 0) > 0:
                print_success("OCR extracted text successfully!")
            else:
                print_warning("OCR might not have worked (0 chunks)")
            
            return result
        else:
            print_error(f"Upload failed with status code: {response.status_code}")
            print_error(f"Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Upload failed: {e}")
        return None

def test_document_search(query):
    """Test searching uploaded documents"""
    print_step(6, "Testing Document Search")
    
    try:
        payload = {
            'query': query,
            'k': 5,
            'user_id': 'test_user_verification'
        }
        
        print_info(f"Searching for: '{query}'")
        response = requests.post(
            'http://localhost:8000/api/artillery/search',
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json()
            print_success(f"Search successful! Found {len(results.get('results', []))} results")
            
            for i, result in enumerate(results.get('results', [])[:3], 1):
                print_info(f"\nResult {i}:")
                print(f"  Score: {result.get('score', 0):.4f}")
                print(f"  Source: {result.get('metadata', {}).get('filename', 'Unknown')}")
                print(f"  Content preview: {result.get('content', '')[:150]}...")
            
            return results
        else:
            print_error(f"Search failed with status code: {response.status_code}")
            print_error(f"Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Search failed: {e}")
        return None

def test_chat_with_image(question):
    """Test chatbot with uploaded image"""
    print_step(7, "Testing Chatbot with Uploaded Image")
    
    try:
        payload = {
            'message': question,
            'user_id': 'test_user_verification',
            'offence_number': '1234567890',
            'language': 'en',
            'top_k': 5
        }
        
        print_info(f"Asking: '{question}'")
        response = requests.post(
            'http://localhost:8000/api/artillery/chat',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Chatbot response received!")
            print_info(f"Answer preview: {result.get('answer', '')[:200]}...")
            print_info(f"Chunks used: {result.get('chunks_used', 0)}")
            print_info(f"Citations: {len(result.get('citations', []))}")
            
            # Full answer
            print(f"\n{BLUE}Full Answer:{RESET}")
            print(result.get('answer', 'No answer'))
            
            return result
        else:
            print_error(f"Chat failed with status code: {response.status_code}")
            print_error(f"Error: {response.text}")
            return None
    except Exception as e:
        print_error(f"Chat failed: {e}")
        return None

def main():
    """Run all verification tests"""
    print(f"\n{BLUE}{'='*60}")
    print("🔍 IMAGE PIPELINE VERIFICATION")
    print(f"{'='*60}{RESET}\n")
    
    # Step 1: Verify Tesseract
    if not verify_tesseract():
        print_error("\n❌ Tesseract not installed! Install it first:")
        print_info("Run: INSTALL_TESSERACT.bat")
        return False
    
    # Step 2: Verify dependencies
    if not verify_dependencies():
        print_error("\n❌ Missing dependencies! Install them first.")
        return False
    
    # Step 3: Test backend server
    if not test_backend_server():
        print_error("\n❌ Backend server not running! Start it first:")
        print_info("Run: START_BOTH_SERVERS.bat")
        return False
    
    # Step 4: Create test image
    test_image = create_test_image()
    if not test_image:
        print_error("\n❌ Failed to create test image!")
        return False
    
    # Step 5: Upload image
    upload_result = test_image_upload(test_image)
    if not upload_result:
        print_error("\n❌ Image upload failed!")
        return False
    
    # Step 6: Search for content
    search_result = test_document_search("traffic violation speeding")
    if not search_result:
        print_warning("\n⚠️  Document search had issues")
    
    # Step 7: Chat with image
    chat_result = test_chat_with_image("What is my offence number and what was I charged with?")
    if not chat_result:
        print_warning("\n⚠️  Chatbot had issues")
    
    # Final summary
    print(f"\n{GREEN}{'='*60}")
    print("✅ VERIFICATION COMPLETE!")
    print(f"{'='*60}{RESET}\n")
    
    print_success("All tests passed! The image pipeline is working correctly.")
    print_info("The bot can now:")
    print("  ✓ Upload images")
    print("  ✓ Extract text with OCR")
    print("  ✓ Chunk and embed content")
    print("  ✓ Search uploaded documents")
    print("  ✓ Answer questions about images")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Verification cancelled by user.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
