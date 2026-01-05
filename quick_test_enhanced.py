#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test to verify enhanced legal datasets are working
"""
import requests
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

BASE_URL = "http://localhost:8000"

def test_enhanced_traffic():
    """Test traffic law with enhanced content"""
    print("Testing Enhanced Traffic Law Content")
    print("="*50)

    question = "What should I do if I get a speeding ticket in Ontario?"
    print(f"Question: {question}")

    try:
        payload = {
            "message": question,
            "top_k": 5,
            "province": "Ontario"
        }

        response = requests.post(f"{BASE_URL}/api/artillery/chat", json=payload, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            citations = result.get('citations', [])

            print(f"Citations found: {len(citations)}")
            print(f"Answer preview: {answer[:300]}...")

            # Check for solution keywords
            solution_keywords = ["pay", "contest", "trial", "plead", "court", "fine", "license"]
            found_keywords = [kw for kw in solution_keywords if kw in answer.lower()]

            print(f"Solution keywords found: {found_keywords}")

            if len(citations) > 0 and found_keywords:
                print("✓ ENHANCED CONTENT WORKING - Solutions and citations found!")
                return True
            else:
                print("⚠️ Limited enhanced content - may need re-ingestion")
                return False
        else:
            print(f"✗ Request failed: {response.text}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_enhanced_property():
    """Test property law with enhanced content"""
    print("\nTesting Enhanced Property Law Content")
    print("="*50)

    question = "My landlord won't fix major repairs. What can I do?"
    print(f"Question: {question}")

    try:
        payload = {
            "message": question,
            "top_k": 5,
            "province": "Ontario"
        }

        response = requests.post(f"{BASE_URL}/api/artillery/chat", json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            citations = result.get('citations', [])

            print(f"Citations found: {len(citations)}")
            print(f"Answer preview: {answer[:300]}...")

            # Check for tenant remedy keywords
            remedy_keywords = ["repair", "deduct", "rent", "ltb", "application", "landlord", "tenant"]
            found_remedies = [kw for kw in remedy_keywords if kw in answer.lower()]

            print(f"Remedy keywords found: {found_remedies}")

            if len(citations) > 0 and found_remedies:
                print("✓ PROPERTY LAW ENHANCED - Tenant remedies found!")
                return True
            else:
                print("⚠️ Property remedies not found")
                return False
        else:
            print(f"✗ Request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    """Main test function"""
    print("QUICK TEST: Enhanced Legal Datasets")
    print("="*60)

    # Check backend
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"✗ Backend not running (Status: {response.status_code})")
            return 1
    except:
        print("✗ Cannot connect to backend")
        return 1

    print("✓ Backend is running")

    # Run tests
    traffic_success = test_enhanced_traffic()
    property_success = test_enhanced_property()

    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)

    total_tests = 2
    passed_tests = sum([traffic_success, property_success])

    print(f"Tests run: {total_tests}")
    print(f"Tests passed: {passed_tests}")
    print(".1f")

    if passed_tests == total_tests:
        print("🎉 ALL ENHANCED DATASETS WORKING PERFECTLY!")
        print("\nEnhanced legal content with solutions is now available!")
    elif passed_tests > 0:
        print("👍 PARTIALLY WORKING - Some enhanced content available")
    else:
        print("⚠️ ENHANCED CONTENT NOT FOUND - May need re-ingestion")

    print("\nEnhanced datasets should provide:")
    print("• Traffic tickets: Payment options, contesting procedures, defenses")
    print("• Property disputes: Tenant remedies, LTB applications, rent issues")
    print("• Employment issues: Termination rights, severance, wrongful dismissal")
    print("• Contract breaches: Small claims court, damages, remedies")

    return 0 if passed_tests > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
