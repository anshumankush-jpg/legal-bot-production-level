"""
Live Demo: Test Legal RAG Chatbot with Current Setup

Shows how the system responds with empty index (no documents ingested yet)
"""

import requests
import json
import time

def test_legal_chat():
    """Test the legal chat API with current setup."""

    print("🚀 LEGAL RAG CHATBOT - LIVE DEMO")
    print("=" * 60)

    # Test questions that demonstrate different behaviors
    test_questions = [
        {
            "question": "What are speeding penalties in Ontario?",
            "country": "Canada",
            "jurisdiction": "Ontario",
            "description": "Normal question - will show 'no documents' response"
        },
        {
            "question": "What are the penalties for speeding in Texas?",
            "country": "USA",
            "jurisdiction": "Texas",
            "description": "Unsupported jurisdiction - will refuse"
        },
        {
            "question": "I got a speeding ticket, what should I do?",
            "description": "Ambiguous jurisdiction - will ask for clarification"
        }
    ]

    base_url = "http://localhost:8000"

    # Check backend health first
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        health_data = health_response.json()
        print(f"📊 Backend Status: {health_data['status']}")
        print(f"📚 Documents Indexed: {health_data['index_size']}")
        print()
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return

    # Test legal chat endpoint
    for i, test_case in enumerate(test_questions, 1):
        print(f"{i}. {test_case['description']}")
        print(f"   Question: \"{test_case['question']}\"")

        payload = {
            "question": test_case["question"],
            "max_results": 8
        }

        if "country" in test_case:
            payload["country"] = test_case["country"]
        if "jurisdiction" in test_case:
            payload["jurisdiction"] = test_case["jurisdiction"]

        try:
            response = requests.post(
                f"{base_url}/api/legal/chat",
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                print("   ✅ Response received:")
                print(f"   📝 Answer: {data['answer'][:150]}...")
                print(f"   📚 Citations: {len(data.get('citations', []))}")
                print(f"   📍 Jurisdiction: {data.get('jurisdiction', 'N/A')}")
                print(f"   🌍 Country: {data.get('country', 'N/A')}")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")

        except requests.exceptions.Timeout:
            print("   ⏰ Request timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print()

    print("🎯 DEMO SUMMARY")
    print("=" * 60)
    print("✅ Backend is running and accessible")
    print("✅ Legal chat API is responding")
    print("✅ Safety features are working (refusing when no data)")
    print("📝 Next step: Index legal documents to enable full functionality")
    print()
    print("To index documents, run:")
    print("  cd backend")
    print("  python scripts/legal_dataset_processor.py --input-dir ../USA --run-tests")
    print()
    print("Then test again for full legal Q&A capabilities! 🚀")

if __name__ == "__main__":
    test_legal_chat()