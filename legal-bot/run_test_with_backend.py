#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automatically starts the backend server and runs the 5 legal questions test
Shows step-by-step responses with actual answers
"""
import requests
import json
import sys
import os
import time
import subprocess
import signal
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:8000"
BACKEND_PORT = 8000

# 5 Questions
QUESTIONS = [
    {
        "num": 1,
        "category": "FEDERAL LAW",
        "question": "What are the federal criminal penalties for drug trafficking in Canada?",
        "description": "Federal criminal law question about drug trafficking"
    },
    {
        "num": 2,
        "category": "TRAFFIC LAW",
        "question": "What are the penalties for speeding in Ontario?",
        "description": "Traffic law question about speeding violations"
    },
    {
        "num": 3,
        "category": "TRAFFIC LAW",
        "question": "What happens if I get a DUI ticket in Canada?",
        "description": "Traffic law question about DUI violations"
    },
    {
        "num": 4,
        "category": "CRIMINAL LAW",
        "question": "What is the difference between assault and aggravated assault?",
        "description": "Criminal law question about assault charges"
    },
    {
        "num": 5,
        "category": "FEDERAL LAW",
        "question": "What are the federal immigration requirements for permanent residency?",
        "description": "Federal administrative law question about immigration"
    }
]

backend_process = None

def check_backend_running():
    """Check if backend is already running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend server."""
    global backend_process
    
    print("\n" + "="*100)
    print("STARTING BACKEND SERVER")
    print("="*100)
    
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    if not backend_dir.exists():
        print(f"[ERROR] Backend directory not found: {backend_dir}")
        return False
    
    print(f"[*] Backend directory: {backend_dir}")
    print(f"[*] Starting server on port {BACKEND_PORT}...")
    
    try:
        # Start backend in background
        if sys.platform == 'win32':
            # Windows
            backend_process = subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)],
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Linux/Mac
            backend_process = subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)],
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        print(f"[*] Backend process started (PID: {backend_process.pid})")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to start backend: {e}")
        return False

def wait_for_backend(max_wait=60):
    """Wait for backend to be ready."""
    print(f"\n[*] Waiting for backend to start (max {max_wait} seconds)...")
    
    for i in range(max_wait):
        if check_backend_running():
            print(f"[SUCCESS] Backend is ready!")
            return True
        time.sleep(1)
        if i % 5 == 0:
            print(f"[*] Still waiting... ({i}/{max_wait} seconds)")
    
    print(f"[ERROR] Backend did not start within {max_wait} seconds")
    return False

def stop_backend():
    """Stop the backend server."""
    global backend_process
    if backend_process:
        print("\n[*] Stopping backend server...")
        try:
            if sys.platform == 'win32':
                backend_process.terminate()
            else:
                backend_process.send_signal(signal.SIGTERM)
            backend_process.wait(timeout=5)
            print("[SUCCESS] Backend stopped")
        except:
            try:
                backend_process.kill()
            except:
                pass
        backend_process = None

def print_step(step_num, title, content=""):
    """Print a formatted step."""
    print("\n" + "="*100)
    print(f"STEP {step_num}: {title}")
    print("="*100)
    if content:
        print(content)

def test_question(q_data):
    """Test a single question and show detailed response."""
    num = q_data["num"]
    category = q_data["category"]
    question = q_data["question"]
    description = q_data["description"]
    
    print_step(1, f"QUESTION {num} - {category}")
    print(f"Description: {description}")
    print(f"Question: {question}")
    
    print_step(2, "SENDING REQUEST")
    payload = {
        "message": question,
        "top_k": 10,
        "province": None
    }
    print(f"URL: {BASE_URL}/api/artillery/chat")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print("\n[*] Sending request...")
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/artillery/chat",
            json=payload,
            timeout=60
        )
        elapsed = time.time() - start_time
        
        print(f"[*] Response received in {elapsed:.2f} seconds")
        print(f"[*] Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print_step(3, "GENERATED ANSWER")
            answer = result.get('answer', 'No answer provided')
            print(answer)
            
            print_step(4, "STATISTICS")
            citations = result.get('citations', [])
            chunks_used = result.get('chunks_used', 0)
            confidence = result.get('confidence', 0.0)
            
            print(f"Citations Found: {len(citations)}")
            print(f"Chunks Used: {chunks_used}")
            print(f"Confidence Score: {confidence:.3f}")
            print(f"Response Time: {elapsed:.2f} seconds")
            
            print_step(5, "SOURCE CITATIONS")
            if citations:
                for i, citation in enumerate(citations[:10], 1):
                    filename = citation.get('filename', 'Unknown')
                    page = citation.get('page', 'N/A')
                    score = citation.get('score', 0)
                    doc_id = citation.get('doc_id', 'N/A')
                    
                    print(f"\n  [{i}] {filename}")
                    print(f"      Page: {page}")
                    print(f"      Relevance Score: {score:.3f}")
                    print(f"      Document ID: {doc_id[:50]}...")
                    
                    # Show content preview if available
                    if 'content' in citation:
                        preview = citation['content'][:150]
                        print(f"      Preview: {preview}...")
            else:
                print("  No citations found")
            
            print_step(6, f"QUESTION {num} COMPLETE - SUCCESS")
            return True, result
        else:
            print_step(6, f"QUESTION {num} FAILED - HTTP ERROR")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print_step(6, f"QUESTION {num} FAILED - CONNECTION ERROR")
        print(f"[ERROR] Cannot connect to backend")
        return False, None
    except Exception as e:
        print_step(6, f"QUESTION {num} FAILED - EXCEPTION")
        print(f"[ERROR] {type(e).__name__}: {e}")
        return False, None

def main():
    """Main function - start backend and run tests."""
    print("\n" + "="*100)
    print("AUTOMATED LEGAL AI QUESTION TEST")
    print("="*100)
    print("This script will:")
    print("  1. Check if backend is running")
    print("  2. Start backend if needed")
    print("  3. Wait for backend to be ready")
    print("  4. Run 5 legal questions test")
    print("  5. Show detailed responses")
    print("="*100)
    
    # Check if backend is already running
    print("\n[*] Checking if backend is already running...")
    if check_backend_running():
        print("[INFO] Backend is already running!")
        started_backend = False
    else:
        print("[INFO] Backend is not running, will start it...")
        if not start_backend():
            print("[ERROR] Failed to start backend")
            return 1
        started_backend = True
        
        # Wait for backend to be ready
        if not wait_for_backend():
            print("[ERROR] Backend failed to start")
            stop_backend()
            return 1
    
    try:
        # Run all questions
        print("\n" + "="*100)
        print("RUNNING 5 LEGAL QUESTIONS TEST")
        print("="*100)
        
        results = []
        all_responses = []
        
        for q_data in QUESTIONS:
            success, response = test_question(q_data)
            results.append(success)
            all_responses.append(response)
            time.sleep(1)  # Small delay between questions
        
        # Final summary
        print("\n" + "="*100)
        print("FINAL SUMMARY")
        print("="*100)
        print(f"Total Questions: {len(QUESTIONS)}")
        print(f"Successful: {sum(results)}")
        print(f"Failed: {len(results) - sum(results)}")
        
        print("\n" + "="*100)
        print("QUESTION RESULTS:")
        print("="*100)
        for i, q_data in enumerate(QUESTIONS, 1):
            status = "[PASS]" if results[i-1] else "[FAIL]"
            print(f"  {i}. {status} {q_data['category']}: {q_data['question'][:60]}...")
        
        # Show all answers summary
        if any(results):
            print("\n" + "="*100)
            print("ALL GENERATED ANSWERS SUMMARY")
            print("="*100)
            for i, (q_data, response) in enumerate(zip(QUESTIONS, all_responses), 1):
                if response:
                    print(f"\n--- QUESTION {i}: {q_data['category']} ---")
                    print(f"Q: {q_data['question']}")
                    answer = response.get('answer', 'No answer')
                    # Show first 300 chars of answer
                    if len(answer) > 300:
                        print(f"A: {answer[:300]}...")
                    else:
                        print(f"A: {answer}")
                    print(f"   Citations: {len(response.get('citations', []))}, Confidence: {response.get('confidence', 0):.3f}")
        
        print("\n" + "="*100)
        print("TEST COMPLETE")
        print("="*100)
        
        return 0 if all(results) else 1
        
    finally:
        # Stop backend if we started it
        if started_backend:
            print("\n[*] Press Enter to stop the backend server, or Ctrl+C to keep it running...")
            try:
                input()
            except KeyboardInterrupt:
                print("\n[*] Keeping backend running...")
            else:
                stop_backend()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[*] Test interrupted by user")
        stop_backend()
        sys.exit(1)
