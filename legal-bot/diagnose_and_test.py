"""
Diagnose backend issues and run a simple test
"""
import requests
import subprocess
import time
import sys

def check_port(port=8000):
    """Check if port is in use."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=5
        )
        lines = result.stdout.split('\n')
        port_lines = [l for l in lines if f':{port}' in l and 'LISTENING' in l]
        return len(port_lines), port_lines
    except:
        return 0, []

def test_backend_simple():
    """Test backend with a simple request."""
    print("=" * 80)
    print("BACKEND DIAGNOSTIC TEST")
    print("=" * 80)
    
    # Check port
    print("\n[1] Checking port 8000...")
    port_count, port_lines = check_port(8000)
    if port_count > 0:
        print(f"[INFO] Found {port_count} process(es) listening on port 8000")
        if port_count > 1:
            print("[WARNING] Multiple processes detected - this may cause issues!")
            print("[TIP] Kill all processes: taskkill /F /PID <pid>")
    else:
        print("[INFO] No processes listening on port 8000")
        print("[TIP] Start backend: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return
    
    # Test root endpoint
    print("\n[2] Testing root endpoint...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"[OK] Root endpoint responded: {response.status_code}")
        print(f"[INFO] {response.json()}")
    except requests.exceptions.Timeout:
        print("[ERROR] Root endpoint timed out")
        print("[TIP] Backend might be stuck. Try restarting.")
        return
    except Exception as e:
        print(f"[ERROR] Root endpoint failed: {e}")
        return
    
    # Test health endpoint
    print("\n[3] Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"[OK] Health endpoint responded: {response.status_code}")
        print(f"[INFO] {response.json()}")
    except requests.exceptions.Timeout:
        print("[ERROR] Health endpoint timed out (backend might be slow)")
        print("[TIP] Backend might be loading models. Wait a bit longer.")
        return
    except Exception as e:
        print(f"[ERROR] Health endpoint failed: {e}")
        return
    
    # Test chat endpoint with simple question
    print("\n[4] Testing chat endpoint with simple question...")
    question = "What is a traffic ticket?"
    
    try:
        payload = {
            "message": question,
            "province": "ON",
            "country": "CA",
            "top_k": 3
        }
        
        print(f"[ASKING] {question}")
        start = time.time()
        response = requests.post(
            "http://localhost:8000/api/artillery/chat",
            json=payload,
            timeout=30
        )
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('answer', '')
            print(f"[SUCCESS] Got response in {elapsed:.2f}s")
            print(f"[INFO] Answer length: {len(answer)} chars")
            print(f"[INFO] Chunks: {data.get('chunks_used', 0)}")
            print(f"\n[ANSWER PREVIEW]")
            print(answer[:300] + "..." if len(answer) > 300 else answer)
            print("\n[OK] Backend is working!")
        else:
            print(f"[ERROR] Chat endpoint returned: {response.status_code}")
            print(f"[ERROR] {response.text}")
    except requests.exceptions.Timeout:
        print(f"[ERROR] Chat request timed out after 30s")
        print("[TIP] Backend might be slow or stuck. Check logs.")
    except Exception as e:
        print(f"[ERROR] Chat request failed: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_backend_simple()
