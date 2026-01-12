#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTIMATE LEGAL AI TEST - 25 Questions
Comprehensive test covering all legal categories, jurisdictions, and scenarios
"""
import requests
import json
import sys
import time
import random

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:8000"

# 25 Ultimate Questions covering all legal areas
QUESTIONS = [
    # FEDERAL CRIMINAL LAW (4 questions)
    {"num": 1, "category": "FEDERAL CRIMINAL", "question": "What are the federal criminal penalties for drug trafficking in Canada?", "jurisdiction": "Canada"},
    {"num": 2, "category": "FEDERAL CRIMINAL", "question": "What constitutes money laundering under Canadian federal law?", "jurisdiction": "Canada"},
    {"num": 3, "category": "FEDERAL CRIMINAL", "question": "What are the penalties for human trafficking in Canada?", "jurisdiction": "Canada"},
    {"num": 4, "category": "FEDERAL CRIMINAL", "question": "What are the federal penalties for cybercrime in Canada?", "jurisdiction": "Canada"},

    # FEDERAL IMMIGRATION & ADMINISTRATIVE (3 questions)
    {"num": 5, "category": "FEDERAL IMMIGRATION", "question": "What are the federal immigration requirements for permanent residency?", "jurisdiction": "Canada"},
    {"num": 6, "category": "FEDERAL ADMINISTRATIVE", "question": "How do I appeal an immigration decision in Canada?", "jurisdiction": "Canada"},
    {"num": 7, "category": "FEDERAL ADMINISTRATIVE", "question": "What are the requirements for refugee status in Canada?", "jurisdiction": "Canada"},

    # TRAFFIC LAW (4 questions)
    {"num": 8, "category": "TRAFFIC LAW", "question": "What are the penalties for speeding in Ontario?", "jurisdiction": "Ontario"},
    {"num": 9, "category": "TRAFFIC LAW", "question": "What happens if I get a DUI ticket in Canada?", "jurisdiction": "Canada"},
    {"num": 10, "category": "TRAFFIC LAW", "question": "What are the requirements for commercial vehicle operators in Canada?", "jurisdiction": "Canada"},
    {"num": 11, "category": "TRAFFIC LAW", "question": "What are the penalties for running a red light in British Columbia?", "jurisdiction": "British Columbia"},

    # CRIMINAL LAW (4 questions)
    {"num": 12, "category": "CRIMINAL LAW", "question": "What is the difference between assault and aggravated assault?", "jurisdiction": "Canada"},
    {"num": 13, "category": "CRIMINAL LAW", "question": "What are the penalties for theft under $5,000 in Canada?", "jurisdiction": "Canada"},
    {"num": 14, "category": "CRIMINAL LAW", "question": "What constitutes fraud under Canadian criminal law?", "jurisdiction": "Canada"},
    {"num": 15, "category": "CRIMINAL LAW", "question": "What are the defenses to murder charges in Canada?", "jurisdiction": "Canada"},

    # CIVIL & CONTRACT LAW (3 questions)
    {"num": 16, "category": "CIVIL LAW", "question": "What makes a contract legally binding in Canada?", "jurisdiction": "Canada"},
    {"num": 17, "category": "CIVIL LAW", "question": "What are the elements of negligence in Canadian tort law?", "jurisdiction": "Canada"},
    {"num": 18, "category": "CONTRACT LAW", "question": "What are the remedies for breach of contract in Ontario?", "jurisdiction": "Ontario"},

    # FAMILY LAW (2 questions)
    {"num": 19, "category": "FAMILY LAW", "question": "What are the grounds for divorce in Canada?", "jurisdiction": "Canada"},
    {"num": 20, "category": "FAMILY LAW", "question": "How is child custody determined in Ontario?", "jurisdiction": "Ontario"},

    # PROPERTY & REAL ESTATE LAW (2 questions)
    {"num": 21, "category": "PROPERTY LAW", "question": "What are a landlord's obligations under Ontario tenancy law?", "jurisdiction": "Ontario"},
    {"num": 22, "category": "PROPERTY LAW", "question": "What are the requirements for property transfer tax in British Columbia?", "jurisdiction": "British Columbia"},

    # EMPLOYMENT & BUSINESS LAW (2 questions)
    {"num": 23, "category": "EMPLOYMENT LAW", "question": "What are employee rights regarding termination in Ontario?", "jurisdiction": "Ontario"},
    {"num": 24, "category": "BUSINESS LAW", "question": "What are the requirements for incorporating a company in Canada?", "jurisdiction": "Canada"},

    # TAX LAW (1 question)
    {"num": 25, "category": "TAX LAW", "question": "What are the federal tax implications for self-employed individuals in Canada?", "jurisdiction": "Canada"}
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

    print("\n" + "="*130)
    print(f"QUESTION {num:2}: {category} ({jurisdiction})")
    print("="*130)
    print(f"Q: {question}")
    print("-"*130)

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

            print("\n" + "-"*130)
            print("GENERATED ANSWER:")
            print("-"*130)
            answer = result.get('answer', 'No answer')
            print(answer)

            print("\n" + "-"*130)
            print("STATISTICS:")
            print("-"*130)
            citations = result.get('citations', [])
            print(f"Citations Found: {len(citations)}")
            print(f"Chunks Used: {result.get('chunks_used', 0)}")
            print(f"Confidence Score: {result.get('confidence', 0.0):.3f}")
            print(f"Jurisdiction: {jurisdiction}")

            if citations:
                print("\n" + "-"*130)
                print("SOURCE CITATIONS:")
                print("-"*130)
                for i, citation in enumerate(citations[:6], 1):
                    filename = citation.get('filename', 'Unknown')
                    page = citation.get('page', 'N/A')
                    score = citation.get('score', 0)
                    print(f"\n  [{i}] {filename}")
                    print(f"      Page: {page}")
                    print(f"      Relevance Score: {score:.3f}")

            print("\n" + "="*130)
            return True, result
        else:
            print(f"\n[ERROR] Status {response.status_code}: {response.text}")
            return False, None

    except requests.exceptions.ConnectionError:
        print(f"\n[ERROR] Cannot connect to backend at {BASE_URL}")
        return False, None
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        return False, None

def main():
    """Main function."""
    print("\n" + "="*130)
    print("ULTIMATE LEGAL AI TEST - 25 QUESTIONS")
    print("="*130)
    print("Testing ALL legal categories: Federal, Provincial, Criminal, Civil, Family, Property, Employment, Tax")
    print("="*130)

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
    print(f"\n[*] Testing {len(QUESTIONS)} ultimate legal questions...")

    results = []
    responses = []
    category_counts = {}
    jurisdiction_counts = {}

    # Randomize order to avoid any sequential bias
    question_order = list(range(len(QUESTIONS)))
    random.shuffle(question_order)

    for idx in question_order:
        q_data = QUESTIONS[idx]
        success, response = test_question(q_data)
        results.append((idx, success))
        responses.append((idx, response))

        # Count by category
        cat = q_data["category"].split()[0]  # First word
        if cat not in category_counts:
            category_counts[cat] = [0, 0]  # [success, total]
        category_counts[cat][1] += 1
        if success:
            category_counts[cat][0] += 1

        # Count by jurisdiction
        jur = q_data["jurisdiction"]
        if jur not in jurisdiction_counts:
            jurisdiction_counts[jur] = [0, 0]
        jurisdiction_counts[jur][1] += 1
        if success:
            jurisdiction_counts[jur][0] += 1

        time.sleep(0.8)  # Slightly longer delay

    # Sort results back to original order
    results.sort(key=lambda x: x[0])
    responses.sort(key=lambda x: x[0])

    # Final summary
    print("\n" + "="*130)
    print("ULTIMATE TEST RESULTS")
    print("="*130)

    successful_answers = sum(1 for _, success in results if success)
    total_questions = len(QUESTIONS)
    success_rate = successful_answers / total_questions * 100

    print(f"Total Questions: {total_questions}")
    print(f"Successful: {successful_answers}")
    print(f"Failed: {total_questions - successful_answers}")
    print(f"Success Rate: {success_rate:.1f}%")

    print("\n" + "="*130)
    print("RESULTS BY LEGAL CATEGORY:")
    print("="*130)
    for category, (success, total) in sorted(category_counts.items()):
        rate = success / total * 100 if total > 0 else 0
        print(f"  {category:15} : {success:2}/{total:2} ({rate:5.1f}%)")

    print("\n" + "="*130)
    print("RESULTS BY JURISDICTION:")
    print("="*130)
    for jurisdiction, (success, total) in sorted(jurisdiction_counts.items()):
        rate = success / total * 100 if total > 0 else 0
        print(f"  {jurisdiction:15} : {success:2}/{total:2} ({rate:5.1f}%)")

    # Performance analysis
    print("\n" + "="*130)
    print("PERFORMANCE ANALYSIS:")
    print("="*130)

    # Calculate average confidence
    confidences = [resp.get('confidence', 0) for _, resp in responses if resp]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0

    # Calculate average citations
    citations_counts = [len(resp.get('citations', [])) for _, resp in responses if resp]
    avg_citations = sum(citations_counts) / len(citations_counts) if citations_counts else 0

    print(f"Average Confidence Score: {avg_confidence:.3f}")
    print(f"Average Citations per Answer: {avg_citations:.1f}")
    print(f"Total Citations Generated: {sum(citations_counts)}")

    # Show top performing categories
    print("\nTop Performing Categories:")
    category_rates = [(cat, success/total*100) for cat, (success, total) in category_counts.items()]
    category_rates.sort(key=lambda x: x[1], reverse=True)
    for cat, rate in category_rates[:5]:
        print(f"  • {cat}: {rate:.1f}% success rate")

    # Show failed questions if any
    failed_questions = [(QUESTIONS[idx], idx+1) for idx, success in results if not success]
    if failed_questions:
        print("\n" + "="*130)
        print("QUESTIONS THAT FAILED:")
        print("="*130)
        for q_data, num in failed_questions[:10]:  # Show first 10
            print(f"  Question {num}: {q_data['question'][:70]}...")

    # Show sample successful responses
    successful_responses = [(QUESTIONS[idx], resp) for idx, resp in responses if resp]
    if successful_responses:
        print("\n" + "="*130)
        print("SAMPLE SUCCESSFUL RESPONSES:")
        print("="*130)
        for i, (q, resp) in enumerate(successful_responses[:8], 1):  # Show first 8
            print(f"\n[{i}] {q['category']} ({q['jurisdiction']})")
            print(f"Q: {q['question']}")
            ans = resp.get('answer', '')[:120]
            if len(resp.get('answer', '')) > 120:
                ans += "..."
            print(f"A: {ans}")
            print(f"   Citations: {len(resp.get('citations', []))}, Confidence: {resp.get('confidence', 0):.3f}")

    print("\n" + "="*130)
    print("TEST COMPLETE")
    print("="*130)

    if success_rate == 100:
        print("🎉 PERFECT SCORE! ALL QUESTIONS ANSWERED SUCCESSFULLY!")
    elif success_rate >= 90:
        print("🏆 EXCELLENT PERFORMANCE!")
    elif success_rate >= 80:
        print("✅ VERY GOOD PERFORMANCE")
    elif success_rate >= 70:
        print("👍 GOOD PERFORMANCE")
    else:
        print("⚠️ NEEDS IMPROVEMENT")

    print("="*130)

    return 0 if successful_answers > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
