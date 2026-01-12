"""
Comprehensive Legal Source & Citation Test
Tests if the system provides relevant articles and law sources for different types of legal questions
"""

import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Test questions covering different law types and provinces
TEST_QUESTIONS = [
    # 1. Criminal Law - Canada Federal
    {
        "category": "Criminal Law - Canada Federal",
        "province": "Federal",
        "question": "What are the penalties for assault under the Canadian Criminal Code?",
        "expected_sources": ["Criminal Code", "C-46", "assault", "section"],
        "expected_law_type": "criminal"
    },
    
    # 2. Traffic Law - Ontario
    {
        "category": "Traffic Law - Ontario",
        "province": "Ontario",
        "question": "What are the penalties for distracted driving in Ontario?",
        "expected_sources": ["Highway Traffic Act", "Ontario", "distracted driving", "fine"],
        "expected_law_type": "traffic"
    },
    
    # 3. Traffic Law - California (USA)
    {
        "category": "Traffic Law - California",
        "province": "California",
        "question": "What is the penalty for DUI in California?",
        "expected_sources": ["California", "DUI", "Vehicle Code", "penalty"],
        "expected_law_type": "traffic"
    },
    
    # 4. Criminal Law - USA Federal
    {
        "category": "Criminal Law - USA Federal",
        "province": "Federal USA",
        "question": "What is wire fraud under federal law?",
        "expected_sources": ["18 U.S.C.", "wire fraud", "1343", "federal"],
        "expected_law_type": "criminal"
    },
    
    # 5. Family Law - Divorce
    {
        "category": "Family Law - Divorce",
        "province": "General",
        "question": "What are the grounds for divorce in Canada?",
        "expected_sources": ["divorce", "grounds", "separation", "Canada"],
        "expected_law_type": "family"
    },
    
    # 6. Traffic Law - British Columbia
    {
        "category": "Traffic Law - British Columbia",
        "province": "British Columbia",
        "question": "What are the speed limits in school zones in BC?",
        "expected_sources": ["British Columbia", "speed", "school zone", "Motor Vehicle Act"],
        "expected_law_type": "traffic"
    },
    
    # 7. Criminal Law - Money Laundering
    {
        "category": "Criminal Law - Money Laundering",
        "province": "Federal USA",
        "question": "What constitutes money laundering under federal law?",
        "expected_sources": ["money laundering", "18 U.S.C.", "1956", "financial"],
        "expected_law_type": "criminal"
    },
    
    # 8. Traffic Law - Alberta
    {
        "category": "Traffic Law - Alberta",
        "province": "Alberta",
        "question": "What are the penalties for speeding in Alberta?",
        "expected_sources": ["Alberta", "speeding", "Traffic Safety Act", "fine"],
        "expected_law_type": "traffic"
    },
    
    # 9. Copyright Law
    {
        "category": "Copyright Law",
        "province": "USA",
        "question": "What is fair use under copyright law?",
        "expected_sources": ["copyright", "fair use", "DMCA", "intellectual property"],
        "expected_law_type": "copyright"
    },
    
    # 10. Commercial Vehicle Law
    {
        "category": "Commercial Vehicle Law",
        "province": "Federal USA",
        "question": "What are the cargo securement requirements for trucks?",
        "expected_sources": ["FMCSR", "cargo", "securement", "commercial vehicle"],
        "expected_law_type": "commercial"
    },
    
    # 11. Charter Rights - Canada
    {
        "category": "Constitutional Law - Canada",
        "province": "Federal Canada",
        "question": "What are my rights under the Canadian Charter during a police stop?",
        "expected_sources": ["Charter", "rights", "police", "section"],
        "expected_law_type": "constitutional"
    },
    
    # 12. Traffic Law - Texas
    {
        "category": "Traffic Law - Texas",
        "province": "Texas",
        "question": "What are the penalties for running a red light in Texas?",
        "expected_sources": ["Texas", "red light", "traffic", "violation"],
        "expected_law_type": "traffic"
    },
    
    # 13. Criminal Law - Firearms
    {
        "category": "Criminal Law - Firearms",
        "province": "Federal USA",
        "question": "What are the federal laws on firearm possession?",
        "expected_sources": ["18 U.S.C.", "922", "firearm", "possession"],
        "expected_law_type": "criminal"
    },
    
    # 14. Traffic Law - Quebec
    {
        "category": "Traffic Law - Quebec",
        "province": "Quebec",
        "question": "What are the demerit points for speeding in Quebec?",
        "expected_sources": ["Quebec", "demerit", "speeding", "points"],
        "expected_law_type": "traffic"
    },
    
    # 15. Case Law - DUI
    {
        "category": "Case Law - DUI",
        "province": "Canada",
        "question": "What was the ruling in R v. St-Onge Lamoureux regarding DUI?",
        "expected_sources": ["R v", "St-Onge", "DUI", "SCC"],
        "expected_law_type": "case_law"
    }
]


def check_backend_health() -> bool:
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def ask_question(question: str, top_k: int = 5) -> Dict[str, Any]:
    """Ask a question to the legal chatbot"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/artillery/chat",
            json={
                "message": question,
                "top_k": top_k,
                "user_id": "test_user"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
    except Exception as e:
        return {
            "error": str(e)
        }


def analyze_response(response: Dict[str, Any], expected_sources: List[str]) -> Dict[str, Any]:
    """Analyze if the response contains relevant sources and citations"""
    
    analysis = {
        "has_answer": False,
        "has_citations": False,
        "citation_count": 0,
        "found_sources": [],
        "missing_sources": [],
        "relevance_score": 0,
        "response_text": ""
    }
    
    # Check if response has error
    if "error" in response:
        analysis["error"] = response["error"]
        return analysis
    
    # Extract answer and citations
    answer = response.get("answer", "")
    citations = response.get("citations", [])
    
    analysis["has_answer"] = len(answer) > 0
    analysis["has_citations"] = len(citations) > 0
    analysis["citation_count"] = len(citations)
    analysis["response_text"] = answer[:200] + "..." if len(answer) > 200 else answer
    
    # Check for expected sources in answer and citations
    combined_text = answer.lower()
    
    # Add citation text
    for citation in citations:
        if isinstance(citation, dict):
            citation_text = citation.get("text", "")
            source = citation.get("source", "")
            combined_text += " " + citation_text.lower() + " " + source.lower()
    
    # Check each expected source
    for expected in expected_sources:
        if expected.lower() in combined_text:
            analysis["found_sources"].append(expected)
        else:
            analysis["missing_sources"].append(expected)
    
    # Calculate relevance score (percentage of expected sources found)
    if expected_sources:
        analysis["relevance_score"] = (len(analysis["found_sources"]) / len(expected_sources)) * 100
    
    return analysis


def print_test_result(test_num: int, test_case: Dict, response: Dict, analysis: Dict):
    """Print formatted test result"""
    
    print(f"\n{'='*80}")
    print(f"TEST #{test_num}: {test_case['category']}")
    print(f"{'='*80}")
    print(f"Province/Jurisdiction: {test_case['province']}")
    print(f"Question: {test_case['question']}")
    print(f"\n--- RESPONSE ANALYSIS ---")
    
    if "error" in analysis:
        print(f"[X] ERROR: {analysis['error']}")
        return False
    
    # Check if answer exists
    if analysis["has_answer"]:
        print(f"[OK] Answer received: {analysis['response_text']}")
    else:
        print(f"[X] No answer received")
        return False
    
    # Check citations
    if analysis["has_citations"]:
        print(f"[OK] Citations found: {analysis['citation_count']} sources")
    else:
        print(f"[!] No citations provided")
    
    # Check source relevance
    print(f"\n--- SOURCE VERIFICATION ---")
    print(f"Relevance Score: {analysis['relevance_score']:.1f}%")
    
    if analysis["found_sources"]:
        print(f"[OK] Found sources: {', '.join(analysis['found_sources'])}")
    
    if analysis["missing_sources"]:
        print(f"[!] Missing sources: {', '.join(analysis['missing_sources'])}")
    
    # Print citations details
    if analysis["has_citations"]:
        print(f"\n--- CITATION DETAILS ---")
        citations = response.get("citations", [])
        for i, citation in enumerate(citations[:3], 1):  # Show first 3 citations
            if isinstance(citation, dict):
                source = citation.get("source", "Unknown")
                text = citation.get("text", "")[:150]
                print(f"{i}. Source: {source}")
                print(f"   Text: {text}...")
    
    # Determine if test passed
    passed = (
        analysis["has_answer"] and
        analysis["relevance_score"] >= 50  # At least 50% of expected sources found
    )
    
    if passed:
        print(f"\n[PASS] TEST PASSED")
    else:
        print(f"\n[FAIL] TEST FAILED - Insufficient source relevance")
    
    return passed


def main():
    """Run comprehensive legal source test"""
    
    print("="*80)
    print("COMPREHENSIVE LEGAL SOURCE & CITATION TEST")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Total Tests: {len(TEST_QUESTIONS)}")
    print("="*80)
    
    # Check backend health
    print("\n[*] Checking backend health...")
    if not check_backend_health():
        print("[X] Backend is not running! Please start the backend server.")
        print("Run: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    print("[OK] Backend is running!")
    
    # Run tests
    results = []
    passed_tests = 0
    failed_tests = 0
    
    for i, test_case in enumerate(TEST_QUESTIONS, 1):
        print(f"\n\n{'#'*80}")
        print(f"Running Test {i}/{len(TEST_QUESTIONS)}")
        print(f"{'#'*80}")
        
        # Ask question
        response = ask_question(test_case["question"])
        
        # Analyze response
        analysis = analyze_response(response, test_case["expected_sources"])
        
        # Print result
        passed = print_test_result(i, test_case, response, analysis)
        
        # Store result
        results.append({
            "test_number": i,
            "category": test_case["category"],
            "province": test_case["province"],
            "question": test_case["question"],
            "passed": passed,
            "relevance_score": analysis.get("relevance_score", 0),
            "citation_count": analysis.get("citation_count", 0),
            "found_sources": analysis.get("found_sources", []),
            "missing_sources": analysis.get("missing_sources", [])
        })
        
        if passed:
            passed_tests += 1
        else:
            failed_tests += 1
        
        # Wait between requests
        time.sleep(2)
    
    # Print summary
    print(f"\n\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {len(TEST_QUESTIONS)}")
    print(f"[OK] Passed: {passed_tests} ({(passed_tests/len(TEST_QUESTIONS)*100):.1f}%)")
    print(f"[X] Failed: {failed_tests} ({(failed_tests/len(TEST_QUESTIONS)*100):.1f}%)")
    
    # Category breakdown
    print(f"\n--- RESULTS BY CATEGORY ---")
    categories = {}
    for result in results:
        cat = result["category"].split(" - ")[0]  # Get main category
        if cat not in categories:
            categories[cat] = {"passed": 0, "total": 0}
        categories[cat]["total"] += 1
        if result["passed"]:
            categories[cat]["passed"] += 1
    
    for cat, stats in categories.items():
        success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"{cat}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
    
    # Average metrics
    avg_relevance = sum(r["relevance_score"] for r in results) / len(results)
    avg_citations = sum(r["citation_count"] for r in results) / len(results)
    
    print(f"\n--- AVERAGE METRICS ---")
    print(f"Average Relevance Score: {avg_relevance:.1f}%")
    print(f"Average Citations per Response: {avg_citations:.1f}")
    
    # Save results to file
    output_file = f"legal_source_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(TEST_QUESTIONS),
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/len(TEST_QUESTIONS)*100),
            "avg_relevance_score": avg_relevance,
            "avg_citations": avg_citations,
            "results": results
        }, f, indent=2)
    
    print(f"\n[FILE] Detailed results saved to: {output_file}")
    
    print(f"\n{'='*80}")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Final verdict
    if passed_tests == len(TEST_QUESTIONS):
        print("\n[SUCCESS] ALL TESTS PASSED! The system provides relevant sources and citations.")
    elif passed_tests >= len(TEST_QUESTIONS) * 0.8:
        print("\n[GOOD] MOST TESTS PASSED! The system generally provides good sources.")
    elif passed_tests >= len(TEST_QUESTIONS) * 0.5:
        print("\n[WARNING] SOME TESTS FAILED. The system needs improvement in source relevance.")
    else:
        print("\n[ERROR] MANY TESTS FAILED. The system needs significant improvement.")


if __name__ == "__main__":
    main()
