"""
Advanced Legal Source Test Suite
Tests chatbot responses for specific law types, countries, and source verification
Includes 20+ comprehensive test cases with detailed source tracking
"""

import requests
import json
import time
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Comprehensive test cases - 20+ questions covering all law types and countries
COMPREHENSIVE_TEST_CASES = [
    # CANADA - CRIMINAL LAW (5 tests)
    {
        "id": 1,
        "country": "Canada",
        "law_type": "Criminal Law",
        "province": "Federal",
        "question": "What is the penalty for theft under $5000 in Canada?",
        "expected_sources": ["Criminal Code", "section 334", "theft", "summary conviction"],
        "expected_articles": ["Section 334", "Section 322"],
        "expected_websites": ["laws-lois.justice.gc.ca", "Criminal Code"]
    },
    {
        "id": 2,
        "country": "Canada",
        "law_type": "Criminal Law",
        "province": "Federal",
        "question": "What are the penalties for drug possession in Canada?",
        "expected_sources": ["Controlled Drugs and Substances Act", "CDSA", "possession"],
        "expected_articles": ["Section 4", "Schedule"],
        "expected_websites": ["laws-lois.justice.gc.ca", "CDSA"]
    },
    {
        "id": 3,
        "country": "Canada",
        "law_type": "Criminal Law",
        "province": "Federal",
        "question": "What constitutes sexual assault under Canadian law?",
        "expected_sources": ["Criminal Code", "section 271", "sexual assault"],
        "expected_articles": ["Section 271", "Section 273"],
        "expected_websites": ["Criminal Code", "justice.gc.ca"]
    },
    {
        "id": 4,
        "country": "Canada",
        "law_type": "Criminal Law",
        "province": "Federal",
        "question": "What is the punishment for robbery in Canada?",
        "expected_sources": ["Criminal Code", "section 344", "robbery", "indictable"],
        "expected_articles": ["Section 343", "Section 344"],
        "expected_websites": ["Criminal Code", "laws-lois.justice.gc.ca"]
    },
    {
        "id": 5,
        "country": "Canada",
        "law_type": "Criminal Law",
        "province": "Federal",
        "question": "What are the penalties for impaired driving causing death in Canada?",
        "expected_sources": ["Criminal Code", "section 320.14", "impaired driving", "death"],
        "expected_articles": ["Section 320.14", "Section 320.19"],
        "expected_websites": ["Criminal Code", "justice.gc.ca"]
    },
    
    # CANADA - TRAFFIC LAW (5 tests)
    {
        "id": 6,
        "country": "Canada",
        "law_type": "Traffic Law",
        "province": "Ontario",
        "question": "What is the penalty for stunt driving in Ontario?",
        "expected_sources": ["Highway Traffic Act", "section 172", "stunt driving", "Ontario"],
        "expected_articles": ["Section 172", "HTA"],
        "expected_websites": ["ontario.ca", "Highway Traffic Act"]
    },
    {
        "id": 7,
        "country": "Canada",
        "law_type": "Traffic Law",
        "province": "British Columbia",
        "question": "What are the penalties for excessive speeding in BC?",
        "expected_sources": ["Motor Vehicle Act", "excessive speeding", "British Columbia"],
        "expected_articles": ["Section 146", "MVA"],
        "expected_websites": ["bclaws.gov.bc.ca", "Motor Vehicle Act"]
    },
    {
        "id": 8,
        "country": "Canada",
        "law_type": "Traffic Law",
        "province": "Alberta",
        "question": "What is the penalty for driving without insurance in Alberta?",
        "expected_sources": ["Traffic Safety Act", "insurance", "Alberta"],
        "expected_articles": ["Section 54", "TSA"],
        "expected_websites": ["alberta.ca", "Traffic Safety Act"]
    },
    {
        "id": 9,
        "country": "Canada",
        "law_type": "Traffic Law",
        "province": "Quebec",
        "question": "What are the penalties for using a cell phone while driving in Quebec?",
        "expected_sources": ["Highway Safety Code", "cell phone", "Quebec", "distracted"],
        "expected_articles": ["Section 439.1", "Code de la sécurité routière"],
        "expected_websites": ["saaq.gouv.qc.ca", "Quebec"]
    },
    {
        "id": 10,
        "country": "Canada",
        "law_type": "Traffic Law",
        "province": "Ontario",
        "question": "What happens if you refuse a breathalyzer test in Ontario?",
        "expected_sources": ["Criminal Code", "section 320.15", "refuse", "breathalyzer"],
        "expected_articles": ["Section 320.15", "refusal"],
        "expected_websites": ["Criminal Code", "ontario.ca"]
    },
    
    # USA - CRIMINAL LAW (5 tests)
    {
        "id": 11,
        "country": "USA",
        "law_type": "Criminal Law",
        "province": "Federal",
        "question": "What is the federal penalty for bank fraud?",
        "expected_sources": ["18 U.S.C.", "1344", "bank fraud", "federal"],
        "expected_articles": ["18 USC 1344", "Title 18"],
        "expected_websites": ["uscode.house.gov", "law.cornell.edu"]
    },
    {
        "id": 12,
        "country": "USA",
        "law_type": "Criminal Law",
        "province": "Federal",
        "question": "What constitutes identity theft under federal law?",
        "expected_sources": ["18 U.S.C.", "1028", "identity theft"],
        "expected_articles": ["18 USC 1028", "identity fraud"],
        "expected_websites": ["uscode.house.gov", "justice.gov"]
    },
    {
        "id": 13,
        "country": "USA",
        "law_type": "Criminal Law",
        "province": "Federal",
        "question": "What are the penalties for drug trafficking under federal law?",
        "expected_sources": ["21 U.S.C.", "841", "drug trafficking", "controlled substance"],
        "expected_articles": ["21 USC 841", "Schedule I"],
        "expected_websites": ["uscode.house.gov", "dea.gov"]
    },
    {
        "id": 14,
        "country": "USA",
        "law_type": "Criminal Law",
        "province": "Federal",
        "question": "What is the penalty for tax evasion in the United States?",
        "expected_sources": ["26 U.S.C.", "7201", "tax evasion", "IRS"],
        "expected_articles": ["26 USC 7201", "Internal Revenue Code"],
        "expected_websites": ["uscode.house.gov", "irs.gov"]
    },
    {
        "id": 15,
        "country": "USA",
        "law_type": "Criminal Law",
        "province": "Federal",
        "question": "What constitutes racketeering under RICO?",
        "expected_sources": ["18 U.S.C.", "1961", "RICO", "racketeering"],
        "expected_articles": ["18 USC 1961", "RICO Act"],
        "expected_websites": ["uscode.house.gov", "fbi.gov"]
    },
    
    # USA - TRAFFIC LAW (3 tests)
    {
        "id": 16,
        "country": "USA",
        "law_type": "Traffic Law",
        "province": "California",
        "question": "What is the penalty for reckless driving in California?",
        "expected_sources": ["Vehicle Code", "23103", "reckless driving", "California"],
        "expected_articles": ["VC 23103", "California Vehicle Code"],
        "expected_websites": ["leginfo.legislature.ca.gov", "dmv.ca.gov"]
    },
    {
        "id": 17,
        "country": "USA",
        "law_type": "Traffic Law",
        "province": "Texas",
        "question": "What are the penalties for street racing in Texas?",
        "expected_sources": ["Transportation Code", "545.420", "racing", "Texas"],
        "expected_articles": ["Section 545.420", "Texas Transportation Code"],
        "expected_websites": ["statutes.capitol.texas.gov", "txdmv.gov"]
    },
    {
        "id": 18,
        "country": "USA",
        "law_type": "Traffic Law",
        "province": "New York",
        "question": "What is the penalty for driving with a suspended license in New York?",
        "expected_sources": ["Vehicle and Traffic Law", "VTL 511", "suspended license", "New York"],
        "expected_articles": ["VTL 511", "New York VTL"],
        "expected_websites": ["nysenate.gov", "dmv.ny.gov"]
    },
    
    # FAMILY LAW (2 tests)
    {
        "id": 19,
        "country": "Canada",
        "law_type": "Family Law",
        "province": "Federal",
        "question": "How is child support calculated in Canada?",
        "expected_sources": ["Federal Child Support Guidelines", "child support", "calculation"],
        "expected_articles": ["Section 3", "Guidelines"],
        "expected_websites": ["justice.gc.ca", "Child Support Guidelines"]
    },
    {
        "id": 20,
        "country": "USA",
        "law_type": "Family Law",
        "province": "Federal",
        "question": "What are the requirements for adoption in the United States?",
        "expected_sources": ["adoption", "requirements", "federal", "state law"],
        "expected_articles": ["adoption law", "requirements"],
        "expected_websites": ["childwelfare.gov", "adoption.gov"]
    },
    
    # COPYRIGHT LAW (2 tests)
    {
        "id": 21,
        "country": "USA",
        "law_type": "Copyright Law",
        "province": "Federal",
        "question": "What is the duration of copyright protection in the United States?",
        "expected_sources": ["17 U.S.C.", "302", "copyright", "duration"],
        "expected_articles": ["17 USC 302", "Copyright Act"],
        "expected_websites": ["copyright.gov", "uscode.house.gov"]
    },
    {
        "id": 22,
        "country": "Canada",
        "law_type": "Copyright Law",
        "province": "Federal",
        "question": "What constitutes fair dealing under Canadian copyright law?",
        "expected_sources": ["Copyright Act", "fair dealing", "section 29"],
        "expected_articles": ["Section 29", "Copyright Act"],
        "expected_websites": ["laws-lois.justice.gc.ca", "cipo.gc.ca"]
    },
    
    # EMPLOYMENT LAW (2 tests)
    {
        "id": 23,
        "country": "Canada",
        "law_type": "Employment Law",
        "province": "Ontario",
        "question": "What is the minimum wage in Ontario?",
        "expected_sources": ["Employment Standards Act", "minimum wage", "Ontario"],
        "expected_articles": ["ESA", "minimum wage"],
        "expected_websites": ["ontario.ca", "Employment Standards"]
    },
    {
        "id": 24,
        "country": "USA",
        "law_type": "Employment Law",
        "province": "Federal",
        "question": "What protections does the Fair Labor Standards Act provide?",
        "expected_sources": ["FLSA", "29 U.S.C.", "Fair Labor Standards Act"],
        "expected_articles": ["29 USC 201", "FLSA"],
        "expected_websites": ["dol.gov", "uscode.house.gov"]
    },
    
    # CONSTITUTIONAL LAW (1 test)
    {
        "id": 25,
        "country": "Canada",
        "law_type": "Constitutional Law",
        "province": "Federal",
        "question": "What does Section 8 of the Charter protect against?",
        "expected_sources": ["Charter", "section 8", "unreasonable search", "seizure"],
        "expected_articles": ["Section 8", "Charter of Rights"],
        "expected_websites": ["laws-lois.justice.gc.ca", "Charter"]
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
            timeout=60  # Increased from 30 to 60 seconds
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


def extract_sources_from_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and analyze sources from the chatbot response"""
    
    result = {
        "answer": "",
        "citations": [],
        "found_sources": [],
        "found_articles": [],
        "found_websites": [],
        "source_details": []
    }
    
    if "error" in response:
        result["error"] = response["error"]
        return result
    
    # Extract answer
    result["answer"] = response.get("answer", "")
    
    # Extract citations
    citations = response.get("citations", [])
    result["citations"] = citations
    
    # Analyze citations and answer for sources
    combined_text = result["answer"].lower()
    
    for citation in citations:
        if isinstance(citation, dict):
            source = citation.get("source", "")
            text = citation.get("text", "")
            
            # Store citation details
            result["source_details"].append({
                "source": source,
                "text": text[:200] + "..." if len(text) > 200 else text
            })
            
            combined_text += " " + text.lower() + " " + source.lower()
    
    return result


def analyze_test_case(test_case: Dict, response: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze if the response contains expected sources, articles, and websites"""
    
    analysis = {
        "test_id": test_case["id"],
        "country": test_case["country"],
        "law_type": test_case["law_type"],
        "province": test_case["province"],
        "question": test_case["question"],
        "passed": False,
        "has_answer": False,
        "has_citations": False,
        "citation_count": 0,
        "expected_sources": test_case["expected_sources"],
        "expected_articles": test_case["expected_articles"],
        "expected_websites": test_case["expected_websites"],
        "found_sources": [],
        "found_articles": [],
        "found_websites": [],
        "missing_sources": [],
        "missing_articles": [],
        "missing_websites": [],
        "source_match_percentage": 0,
        "article_match_percentage": 0,
        "website_match_percentage": 0,
        "overall_score": 0,
        "answer_preview": "",
        "citation_details": []
    }
    
    # Check for errors
    if "error" in response:
        analysis["error"] = response["error"]
        return analysis
    
    # Extract response data
    answer = response.get("answer", "")
    citations = response.get("citations", [])
    
    analysis["has_answer"] = len(answer) > 0
    analysis["has_citations"] = len(citations) > 0
    analysis["citation_count"] = len(citations)
    analysis["answer_preview"] = answer[:200] + "..." if len(answer) > 200 else answer
    
    # Combine text for analysis
    combined_text = answer.lower()
    
    for citation in citations:
        if isinstance(citation, dict):
            source = citation.get("source", "")
            text = citation.get("text", "")
            combined_text += " " + text.lower() + " " + source.lower()
            
            analysis["citation_details"].append({
                "source": source,
                "text": text[:150] + "..." if len(text) > 150 else text
            })
    
    # Check expected sources
    for expected_source in test_case["expected_sources"]:
        if expected_source.lower() in combined_text:
            analysis["found_sources"].append(expected_source)
        else:
            analysis["missing_sources"].append(expected_source)
    
    # Check expected articles
    for expected_article in test_case["expected_articles"]:
        if expected_article.lower() in combined_text:
            analysis["found_articles"].append(expected_article)
        else:
            analysis["missing_articles"].append(expected_article)
    
    # Check expected websites
    for expected_website in test_case["expected_websites"]:
        if expected_website.lower() in combined_text:
            analysis["found_websites"].append(expected_website)
        else:
            analysis["missing_websites"].append(expected_website)
    
    # Calculate match percentages
    if test_case["expected_sources"]:
        analysis["source_match_percentage"] = (len(analysis["found_sources"]) / len(test_case["expected_sources"])) * 100
    
    if test_case["expected_articles"]:
        analysis["article_match_percentage"] = (len(analysis["found_articles"]) / len(test_case["expected_articles"])) * 100
    
    if test_case["expected_websites"]:
        analysis["website_match_percentage"] = (len(analysis["found_websites"]) / len(test_case["expected_websites"])) * 100
    
    # Calculate overall score
    analysis["overall_score"] = (
        analysis["source_match_percentage"] * 0.5 +
        analysis["article_match_percentage"] * 0.3 +
        analysis["website_match_percentage"] * 0.2
    )
    
    # Determine if test passed (>= 40% overall score and has answer)
    analysis["passed"] = analysis["has_answer"] and analysis["overall_score"] >= 40
    
    return analysis


def print_test_result(analysis: Dict):
    """Print formatted test result"""
    
    print(f"\n{'='*80}")
    print(f"TEST #{analysis['test_id']}: {analysis['law_type']} - {analysis['country']} ({analysis['province']})")
    print(f"{'='*80}")
    print(f"Question: {analysis['question']}")
    
    if "error" in analysis:
        print(f"\n[X] ERROR: {analysis['error']}")
        return
    
    print(f"\n--- RESPONSE STATUS ---")
    print(f"Answer: {'[OK]' if analysis['has_answer'] else '[X]'} {analysis['answer_preview']}")
    print(f"Citations: {'[OK]' if analysis['has_citations'] else '[!]'} {analysis['citation_count']} sources")
    
    print(f"\n--- SOURCE VERIFICATION ---")
    print(f"Overall Score: {analysis['overall_score']:.1f}%")
    
    # Sources
    print(f"\nExpected Sources: {', '.join(analysis['expected_sources'])}")
    if analysis['found_sources']:
        print(f"[OK] Found: {', '.join(analysis['found_sources'])}")
    if analysis['missing_sources']:
        print(f"[!] Missing: {', '.join(analysis['missing_sources'])}")
    print(f"Match Rate: {analysis['source_match_percentage']:.0f}%")
    
    # Articles
    print(f"\nExpected Articles: {', '.join(analysis['expected_articles'])}")
    if analysis['found_articles']:
        print(f"[OK] Found: {', '.join(analysis['found_articles'])}")
    if analysis['missing_articles']:
        print(f"[!] Missing: {', '.join(analysis['missing_articles'])}")
    print(f"Match Rate: {analysis['article_match_percentage']:.0f}%")
    
    # Websites
    print(f"\nExpected Websites: {', '.join(analysis['expected_websites'])}")
    if analysis['found_websites']:
        print(f"[OK] Found: {', '.join(analysis['found_websites'])}")
    if analysis['missing_websites']:
        print(f"[!] Missing: {', '.join(analysis['missing_websites'])}")
    print(f"Match Rate: {analysis['website_match_percentage']:.0f}%")
    
    # Citations
    if analysis['citation_details']:
        print(f"\n--- CITATION DETAILS (First 3) ---")
        for i, citation in enumerate(analysis['citation_details'][:3], 1):
            print(f"{i}. Source: {citation['source']}")
            print(f"   Text: {citation['text']}")
    
    # Result
    if analysis['passed']:
        print(f"\n[PASS] TEST PASSED")
    else:
        print(f"\n[FAIL] TEST FAILED - Score: {analysis['overall_score']:.1f}%")


def main():
    """Run comprehensive legal source test suite"""
    
    print("="*80)
    print("ADVANCED LEGAL SOURCE TEST SUITE")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Total Tests: {len(COMPREHENSIVE_TEST_CASES)}")
    print("="*80)
    
    # Check backend health
    print("\n[*] Checking backend health...")
    if not check_backend_health():
        print("[X] Backend is not running! Please start the backend server.")
        return
    
    print("[OK] Backend is running!")
    
    # Run tests
    results = []
    passed_tests = 0
    failed_tests = 0
    
    # Group tests by law type and country
    test_groups = {}
    
    for i, test_case in enumerate(COMPREHENSIVE_TEST_CASES, 1):
        print(f"\n\n{'#'*80}")
        print(f"Running Test {i}/{len(COMPREHENSIVE_TEST_CASES)}")
        print(f"{'#'*80}")
        
        # Ask question
        response = ask_question(test_case["question"])
        
        # Analyze response
        analysis = analyze_test_case(test_case, response)
        
        # Print result
        print_test_result(analysis)
        
        # Store result
        results.append(analysis)
        
        if analysis["passed"]:
            passed_tests += 1
        else:
            failed_tests += 1
        
        # Group by law type and country
        key = f"{test_case['country']} - {test_case['law_type']}"
        if key not in test_groups:
            test_groups[key] = {"passed": 0, "total": 0, "tests": []}
        test_groups[key]["total"] += 1
        if analysis["passed"]:
            test_groups[key]["passed"] += 1
        test_groups[key]["tests"].append(analysis)
        
        # Wait between requests
        time.sleep(2)
    
    # Print summary
    print(f"\n\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests: {len(COMPREHENSIVE_TEST_CASES)}")
    print(f"[OK] Passed: {passed_tests} ({(passed_tests/len(COMPREHENSIVE_TEST_CASES)*100):.1f}%)")
    print(f"[X] Failed: {failed_tests} ({(failed_tests/len(COMPREHENSIVE_TEST_CASES)*100):.1f}%)")
    
    # Results by law type and country
    print(f"\n--- RESULTS BY LAW TYPE AND COUNTRY ---")
    for key, stats in sorted(test_groups.items()):
        success_rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"{key}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
    
    # Average scores
    avg_overall = sum(r["overall_score"] for r in results) / len(results)
    avg_source = sum(r["source_match_percentage"] for r in results) / len(results)
    avg_article = sum(r["article_match_percentage"] for r in results) / len(results)
    avg_website = sum(r["website_match_percentage"] for r in results) / len(results)
    avg_citations = sum(r["citation_count"] for r in results) / len(results)
    
    print(f"\n--- AVERAGE SCORES ---")
    print(f"Overall Score: {avg_overall:.1f}%")
    print(f"Source Match: {avg_source:.1f}%")
    print(f"Article Match: {avg_article:.1f}%")
    print(f"Website Match: {avg_website:.1f}%")
    print(f"Citations per Response: {avg_citations:.1f}")
    
    # Save results to file
    output_file = f"advanced_legal_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(COMPREHENSIVE_TEST_CASES),
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests/len(COMPREHENSIVE_TEST_CASES)*100),
            "avg_overall_score": avg_overall,
            "avg_source_match": avg_source,
            "avg_article_match": avg_article,
            "avg_website_match": avg_website,
            "avg_citations": avg_citations,
            "test_groups": {k: {"passed": v["passed"], "total": v["total"]} for k, v in test_groups.items()},
            "results": results
        }, f, indent=2)
    
    print(f"\n[FILE] Detailed results saved to: {output_file}")
    
    print(f"\n{'='*80}")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")
    
    # Final verdict
    if passed_tests >= len(COMPREHENSIVE_TEST_CASES) * 0.8:
        print("\n[SUCCESS] Most tests passed! System provides good source attribution.")
    elif passed_tests >= len(COMPREHENSIVE_TEST_CASES) * 0.6:
        print("\n[GOOD] Majority of tests passed. Some improvements needed.")
    else:
        print("\n[WARNING] Many tests failed. System needs improvement in source attribution.")


if __name__ == "__main__":
    main()
