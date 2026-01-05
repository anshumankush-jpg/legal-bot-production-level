"""Test random legal questions from the comprehensive dataset."""
import requests
import json
import random
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"
DATA_DIR = Path("collected_legal_data")

# Random test questions covering different legal areas
RANDOM_QUESTIONS = [
    # USA Federal Criminal
    "What are the penalties for mail fraud under federal law?",
    "What constitutes money laundering?",
    "What are the elements of wire fraud?",
    "What are the penalties for bank robbery?",
    "When is a firearm considered illegal?",

    # USA State Traffic
    "What is the speed limit in California?",
    "How many points for speeding in Texas?",
    "What are DUI penalties in Florida?",
    "What is the speed limit in New York?",
    "How does the point system work in Pennsylvania?",

    # Canada Federal Criminal
    "What is the legal BAC limit in Canada?",
    "What constitutes assault with a weapon?",
    "What are the penalties for impaired driving?",
    "What is the difference between summary and indictable offences?",

    # Canada Provincial
    "What are DUI penalties in Ontario?",
    "How many demerit points for speeding in British Columbia?",
    "What are speeding fines in Alberta?",
    "What are traffic laws in Quebec?",
    "What are criminal penalties in Manitoba?",

    # Case Studies
    "What did Birchfield v. North Dakota decide about DUI?",
    "What is the Grant test for evidence exclusion?",
    "Can police demand breath tests without suspicion in Canada?",
    "What are Miranda rights?",
    "What is reasonable suspicion under the Fourth Amendment?",

    # Constitutional Law
    "What are Charter rights in Canada?",
    "How does Section 8 of the Charter work?",
    "What is the Fifth Amendment?",
    "Can evidence be excluded for Charter violations?",

    # Random specific questions
    "Can you be charged with both conspiracy and the underlying crime?",
    "What is the statute of limitations for wire fraud?",
    "Can police search your trash without a warrant?",
    "What is spousal privilege in Canada?",
    "Can a parent be charged with kidnapping their own child?",
    "What is the difference between impaired driving and over 80?",
    "How long do demerit points stay on record?",
    "Can you refuse a breathalyzer test in Canada?",
    "What constitutes mischief under Canadian law?",
    "What are the rights of crime victims?"
]

def test_random_question():
    """Test a randomly selected legal question."""
    print("=" * 80)
    print("RANDOM LEGAL QUESTION TEST")
    print("=" * 80)

    # Pick a random question
    question = random.choice(RANDOM_QUESTIONS)

    print(f"\nRANDOM QUESTION: '{question}'")
    print(f"Endpoint: {BASE_URL}/api/artillery/chat")
    print("\nSending request to backend...\n")

    try:
        payload = {
            "message": question,
            "top_k": 15,
            "province": None  # Search all jurisdictions
        }

        response = requests.post(
            f"{BASE_URL}/api/artillery/chat",
            json=payload,
            timeout=120
        )

        if response.status_code == 200:
            result = response.json()

            print("=" * 80)
            print("BACKEND ANSWER:")
            print("=" * 80)
            print(result.get('answer', 'No answer provided'))

            print("\n" + "=" * 80)
            print("DETAILS:")
            print("=" * 80)
            print(f"Citations Found: {len(result.get('citations', []))}")
            print(f"Chunks Used: {result.get('chunks_used', 0)}")
            print(f"Confidence Score: {result.get('confidence', 0.0)}")

            citations = result.get('citations', [])
            if citations:
                print(f"\nTop Sources:")
                for i, citation in enumerate(citations[:3], 1):
                    filename = citation.get('filename', 'Unknown')
                    score = citation.get('score', 0)
                    print(f"  {i}. {filename} (Relevance: {score:.3f})")

            print("\n" + "=" * 80)
            print("TEST COMPLETE - Answer generated!")
            print("=" * 80)

            # Show what category this question belongs to
            if any(term in question.lower() for term in ['federal', 'mail fraud', 'wire fraud', 'money laundering', 'bank robbery', 'firearm']):
                category = "USA Federal Criminal Law"
            elif any(term in question.lower() for term in ['speed', 'point', 'california', 'texas', 'florida', 'new york', 'pennsylvania']):
                category = "USA State Traffic Law"
            elif any(term in question.lower() for term in ['bac', 'impaired', 'canada', 'assault', 'summary', 'indictable']):
                category = "Canada Criminal Law"
            elif any(term in question.lower() for term in ['ontario', 'british columbia', 'alberta', 'quebec', 'manitoba']):
                category = "Canada Provincial Law"
            elif any(term in question.lower() for term in ['birchfield', 'grant', 'miranda', 'reasonable suspicion']):
                category = "Case Study/Supreme Court"
            elif any(term in question.lower() for term in ['charter', 'amendment', 'constitutional']):
                category = "Constitutional Law"
            else:
                category = "General Legal Question"

            print(f"Question Category: {category}")

            return True
        else:
            print(f"❌ ERROR: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend.")
        print("Make sure the backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def show_dataset_stats():
    """Show current dataset statistics."""
    print("\nCURRENT LEGAL DATASET STATUS:")
    print("-" * 50)

    try:
        with open(DATA_DIR / "complete_legal_dataset.json", 'r', encoding='utf-8') as f:
            data = json.load(f)

        total = sum(len(v) for v in data.values())
        print(f"Total Legal Items: {total}")

        for category, items in data.items():
            if items:
                print(f"  - {category}: {len(items)} items")

        print(f"\nAvailable Test Questions: {len(RANDOM_QUESTIONS)}")
        print("-" * 50)

    except FileNotFoundError:
        print("❌ Dataset not found. Run data collection scripts first.")
        return False

    return True

def main():
    """Main function."""
    print("RANDOM LEGAL QUESTION TESTER")
    print("Tests random questions from the comprehensive legal dataset")

    # Show dataset stats
    if not show_dataset_stats():
        return

    # Check backend
    try:
        response = requests.get(f"{BASE_URL}/api/artillery/health", timeout=5)
        if response.status_code != 200:
            print("Backend not healthy. Start backend first:")
            print("   cd backend && python -m uvicorn app.main:app --reload")
            return
    except Exception as e:
        print(f"Backend not running: {e}")
        print("Start with: cd backend && python -m uvicorn app.main:app --reload")
        return

    # Run random test
    success = test_random_question()

    if success:
        print("\nSUCCESS! The legal dataset can answer random questions!")
        print("Try running this script multiple times to test different questions.")
    else:
        print("\nFAILED! Check backend and dataset.")

if __name__ == "__main__":
    main()
