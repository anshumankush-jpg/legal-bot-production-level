#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple script to test 5 legal questions - assumes backend is already running
Shows step-by-step responses
"""
import requests
import json
import sys
import time

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:8000"

# 5 Questions
QUESTIONS = [
    {
        "num": 1,
        "category": "FEDERAL LAW",
        "question": "What are the federal criminal penalties for drug trafficking in Canada?",
    },
    {
        "num": 2,
        "category": "TRAFFIC LAW",
        "question": "What are the penalties for speeding in Ontario?",
    },
    {
        "num": 3,
        "category": "TRAFFIC LAW",
        "question": "What happens if I get a DUI ticket in Canada?",
    },
    {
        "num": 4,
        "category": "CRIMINAL LAW",
        "question": "What is the difference between assault and aggravated assault?",
    },
    {
        "num": 5,
        "category": "FEDERAL LAW",
        "question": "What are the federal immigration requirements for permanent residency?",
    }
]

def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_question(q_data):
    """Test a question and show response."""
    num = q_data["num"]
    category = q_data["category"]
    question = q_data["question"]
    
    print("\n" + "="*100)
    print(f"QUESTION {num}: {category}")
    print("="*100)
    print(f"Q: {question}")
    print("-"*100)
    
    try:
        payload = {
            "message": question,
            "top_k": 10,
            "province": None
        }
        
        print(f"\n[*] Sending to: {BASE_URL}/api/artillery/chat")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/artillery/chat",
            json=payload,
            timeout=60
        )
        
        elapsed = time.time() - start_time
        print(f"[*] Response time: {elapsed:.2f} seconds")
        print(f"[*] Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n" + "-"*100)
            print("ANSWER:")
            print("-"*100)
            answer = result.get('answer', 'No answer')
            print(answer)
            
            print("\n" + "-"*100)
            print("STATISTICS:")
            print("-"*100)
            citations = result.get('citations', [])
            print(f"Citations: {len(citations)}")
            print(f"Chunks Used: {result.get('chunks_used', 0)}")
            print(f"Confidence: {result.get('confidence', 0.0):.3f}")
            
            if citations:
                print("\n" + "-"*100)
                print("SOURCES:")
                print("-"*100)
                for i, cit in enumerate(citations[:5], 1):
                    print(f"\n[{i}] {cit.get('filename', 'Unknown')}")
                    print(f"    Page: {cit.get('page', 'N/A')}")
                    print(f"    Score: {cit.get('score', 0):.3f}")
            
            print("\n" + "="*100)
            return True, result
        else:
            print(f"\n[ERROR] Status {response.status_code}: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Cannot connect to backend at {BASE_URL}")
        print("        Make sure backend is running:")
        print("        cd backend")
        print("        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False, None
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        return False, None

def main():
    """Main function."""
    print("\n" + "="*100)
    print("5 LEGAL QUESTIONS TEST - STEP BY STEP")
    print("="*100)
    
    # Check backend
    print("\n[*] Checking backend connection...")
    if not check_backend():
        print("[ERROR] Backend is not running!")
        print("\nPlease start the backend first:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("\nThen run this script again.")
        return 1
    
    print("[SUCCESS] Backend is running!")
    
    # Test all questions
    print(f"\n[*] Testing {len(QUESTIONS)} questions...")
    
    results = []
    responses = []
    
    for q_data in QUESTIONS:
        success, response = test_question(q_data)
        results.append(success)
        responses.append(response)
        time.sleep(0.5)
    
    # Summary
    print("\n" + "="*100)
    print("SUMMARY")
    print("="*100)
    print(f"Total: {len(QUESTIONS)}")
    print(f"Success: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    print("\n" + "="*100)
    print("ALL ANSWERS")
    print("="*100)
    for i, (q, resp) in enumerate(zip(QUESTIONS, responses), 1):
        if resp:
            print(f"\n[{i}] {q['category']}")
            print(f"Q: {q['question']}")
            ans = resp.get('answer', '')[:200]
            print(f"A: {ans}...")
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
