#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Legal AI Test - 15 Questions
Covers Federal, Traffic, Criminal, Administrative, Civil, Family, Property, Tax, and Employment law
Shows detailed responses with citations and statistics
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

# 15 Comprehensive Questions covering all legal categories
QUESTIONS = [
    # FEDERAL LAW (3 questions)
    {
        "num": 1,
        "category": "FEDERAL CRIMINAL",
        "question": "What are the federal criminal penalties for drug trafficking in Canada?",
        "jurisdiction": "Canada"
    },
    {
        "num": 2,
        "category": "FEDERAL IMMIGRATION",
        "question": "What are the federal immigration requirements for permanent residency?",
        "jurisdiction": "Canada"
    },
    {
        "num": 3,
        "category": "FEDERAL TAX",
        "question": "What are the federal tax implications for self-employed individuals in Canada?",
        "jurisdiction": "Canada"
    },

    # TRAFFIC LAW (3 questions)
    {
        "num": 4,
        "category": "TRAFFIC SPEEDING",
        "question": "What are the penalties for speeding in Ontario?",
        "jurisdiction": "Ontario"
    },
    {
        "num": 5,
        "category": "TRAFFIC DUI",
        "question": "What happens if I get a DUI ticket in Canada?",
        "jurisdiction": "Canada"
    },
    {
        "num": 6,
        "category": "TRAFFIC COMMERCIAL",
        "question": "What are the requirements for commercial vehicle operators in Canada?",
        "jurisdiction": "Canada"
    },

    # CRIMINAL LAW (3 questions)
    {
        "num": 7,
        "category": "CRIMINAL ASSAULT",
        "question": "What is the difference between assault and aggravated assault?",
        "jurisdiction": "Canada"
    },
    {
        "num": 8,
        "category": "CRIMINAL THEFT",
        "question": "What are the penalties for theft under $5,000 in Canada?",
        "jurisdiction": "Canada"
    },
    {
        "num": 9,
        "category": "CRIMINAL FRAUD",
        "question": "What constitutes fraud under Canadian criminal law?",
        "jurisdiction": "Canada"
    },

    # ADMINISTRATIVE LAW (2 questions)
    {
        "num": 10,
        "category": "ADMINISTRATIVE LICENSING",
        "question": "What are the requirements for professional licensing in Ontario?",
        "jurisdiction": "Ontario"
    },
    {
        "num": 11,
        "category": "ADMINISTRATIVE APPEALS",
        "question": "How do I appeal an immigration decision in Canada?",
        "jurisdiction": "Canada"
    },

    # CIVIL LAW (2 questions)
    {
        "num": 12,
        "category": "CIVIL CONTRACT",
        "question": "What makes a contract legally binding in Canada?",
        "jurisdiction": "Canada"
    },
    {
        "num": 13,
        "category": "CIVIL TORT",
        "question": "What are the elements of negligence in Canadian tort law?",
        "jurisdiction": "Canada"
    },

    # FAMILY LAW (1 question)
    {
        "num": 14,
        "category": "FAMILY DIVORCE",
        "question": "What are the grounds for divorce in Canada?",
        "jurisdiction": "Canada"
    },

    # PROPERTY LAW (1 question)
    {
        "num": 15,
        "category": "PROPERTY LANDLORD",
        "question": "What are a landlord's obligations under Ontario tenancy law?",
        "jurisdiction": "Ontario"
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
    """Test a single question and show detailed response."""
    num = q_data["num"]
    category = q_data["category"]
    question = q_data["question"]
    jurisdiction = q_data["jurisdiction"]

    print("\n" + "="*120)
    print(f"QUESTION {num}: {category} ({jurisdiction})")
    print("="*120)
    print(f"Q: {question}")
    print("-"*120)

    try:
        payload = {
            "message": question,
            "top_k": 10,
            "province": jurisdiction if jurisdiction != "Canada" else None
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

            print("\n" + "-"*120)
            print("GENERATED ANSWER:")
            print("-"*120)
            answer = result.get('answer', 'No answer')
            print(answer)

            print("\n" + "-"*120)
            print("STATISTICS:")
            print("-"*120)
            citations = result.get('citations', [])
            print(f"Citations Found: {len(citations)}")
            print(f"Chunks Used: {result.get('chunks_used', 0)}")
            print(f"Confidence Score: {result.get('confidence', 0.0):.3f}")
            print(f"Jurisdiction: {jurisdiction}")

            if citations:
                print("\n" + "-"*120)
                print("SOURCE CITATIONS:")
                print("-"*120)
                for i, citation in enumerate(citations[:8], 1):
                    filename = citation.get('filename', 'Unknown')
                    page = citation.get('page', 'N/A')
                    score = citation.get('score', 0)
                    doc_id = citation.get('doc_id', 'N/A')

                    print(f"\n  [{i}] {filename}")
                    print(f"      Page: {page}")
                    print(f"      Relevance Score: {score:.3f}")
                    print(f"      Document ID: {doc_id[:50]}...")

            print("\n" + "="*120)
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
    print("\n" + "="*120)
    print("COMPREHENSIVE LEGAL AI TEST - 15 QUESTIONS")
    print("="*120)
    print("Testing Federal, Traffic, Criminal, Administrative, Civil, Family, Property, Tax & Employment Law")
    print("="*120)

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
    print(f"\n[*] Testing {len(QUESTIONS)} comprehensive legal questions...")

    results = []
    responses = []
    category_counts = {}

    for q_data in QUESTIONS:
        success, response = test_question(q_data)
        results.append(success)
        responses.append(response)

        # Count by category
        cat = q_data["category"].split()[0]  # First word of category
        category_counts[cat] = category_counts.get(cat, 0) + (1 if success else 0)

        time.sleep(0.5)

    # Final summary
    print("\n" + "="*120)
    print("COMPREHENSIVE TEST RESULTS")
    print("="*120)
    print(f"Total Questions: {len(QUESTIONS)}")
    print(f"Successful: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    print(f"Success Rate: {sum(results)/len(QUESTIONS)*100:.1f}%")

    print("\n" + "="*120)
    print("RESULTS BY LEGAL CATEGORY:")
    print("="*120)
    for category, count in sorted(category_counts.items()):
        total_in_cat = len([q for q in QUESTIONS if q["category"].startswith(category)])
        success_rate = count / total_in_cat * 100 if total_in_cat > 0 else 0
        print(f"  {category:12} : {count:2}/{total_in_cat:2} ({success_rate:5.1f}%)")

    print("\n" + "="*120)
    print("JURISDICTION COVERAGE:")
    print("="*120)
    jur_counts = {}
    for q in QUESTIONS:
        jur = q["jurisdiction"]
        jur_counts[jur] = jur_counts.get(jur, 0) + (1 if results[q["num"]-1] else 0)

    for jur, count in sorted(jur_counts.items()):
        total_jur = len([q for q in QUESTIONS if q["jurisdiction"] == jur])
        success_rate = count / total_jur * 100 if total_jur > 0 else 0
        print(f"  {jur:12} : {count:2}/{total_jur:2} ({success_rate:5.1f}%)")

    # Show failed questions if any
    failed_questions = [q for q, success in zip(QUESTIONS, results) if not success]
    if failed_questions:
        print("\n" + "="*120)
        print("FAILED QUESTIONS:")
        print("="*120)
        for q in failed_questions:
            print(f"  Question {q['num']}: {q['question'][:80]}...")

    # Show sample successful responses
    successful_responses = [(q, resp) for q, resp in zip(QUESTIONS, responses) if resp]
    if successful_responses:
        print("\n" + "="*120)
        print("SAMPLE SUCCESSFUL RESPONSES:")
        print("="*120)
        for i, (q, resp) in enumerate(successful_responses[:5], 1):
            print(f"\n[{i}] {q['category']} ({q['jurisdiction']})")
            print(f"Q: {q['question']}")
            ans = resp.get('answer', '')[:150]
            if len(resp.get('answer', '')) > 150:
                ans += "..."
            print(f"A: {ans}")
            print(f"   Citations: {len(resp.get('citations', []))}, Confidence: {resp.get('confidence', 0):.3f}")

    print("\n" + "="*120)
    print("TEST COMPLETE")
    print("="*120)

    if sum(results) == len(QUESTIONS):
        print("🎉 ALL QUESTIONS ANSWERED SUCCESSFULLY!")
    elif sum(results) >= len(QUESTIONS) * 0.8:
        print("✅ EXCELLENT PERFORMANCE!")
    elif sum(results) >= len(QUESTIONS) * 0.6:
        print("👍 GOOD PERFORMANCE")
    else:
        print("⚠️  NEEDS IMPROVEMENT")

    print("="*120)

    return 0 if sum(results) > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
