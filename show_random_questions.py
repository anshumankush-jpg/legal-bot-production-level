"""Show random legal questions that the comprehensive dataset can answer."""
import random
import json
from pathlib import Path

DATA_DIR = Path("collected_legal_data")

# Random test questions covering different legal areas
SAMPLE_QUESTIONS = [
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

def show_random_questions():
    """Show random legal questions and what they would cover."""
    print("=" * 80)
    print("RANDOM LEGAL QUESTIONS - COMPREHENSIVE DATASET")
    print("=" * 80)
    print(f"\nAvailable Questions: {len(SAMPLE_QUESTIONS)}")
    print("\nHere are 10 random questions the system can answer:")
    print("-" * 60)

    # Show 10 random questions with their categories
    selected_questions = random.sample(SAMPLE_QUESTIONS, 10)

    for i, question in enumerate(selected_questions, 1):
        # Determine category
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

        print(f"{i:2d}. [{category}]")
        print(f"    '{question}'")
        print()

    print("=" * 80)
    print("DATASET COVERAGE SUMMARY")
    print("=" * 80)

    try:
        with open(DATA_DIR / "complete_legal_dataset.json", 'r', encoding='utf-8') as f:
            data = json.load(f)

        total = sum(len(v) for v in data.values())
        print(f"Total Legal Items: {total}")
        print("\nCoverage:")
        print(f"  USA Federal Criminal Laws: {len(data.get('usa_federal_criminal', []))} items")
        print(f"  USA Traffic Laws: {len(data.get('usa_traffic_laws', []))} items (All 50 states)")
        print(f"  Canada Federal Criminal Laws: {len(data.get('canada_federal_criminal', []))} items")
        print(f"  Canada Provincial Laws: {len(data.get('canada_provincial_laws', []))} items (All 13 provinces)")
        print(f"  Case Studies: {len(data.get('case_studies', []))} items (Supreme Court decisions)")

        print(f"\nAvailable Test Questions: {len(SAMPLE_QUESTIONS)}")
        print("\nTo test with backend:")
        print("1. Start backend: cd backend && python -m uvicorn app.main:app --reload")
        print("2. Run: python random_legal_question_test.py")

    except FileNotFoundError:
        print("Dataset not found. Run data collection scripts first.")

    print("=" * 80)

def show_specific_examples():
    """Show specific examples of what each category can answer."""
    print("\n" + "=" * 80)
    print("SPECIFIC EXAMPLES BY CATEGORY")
    print("=" * 80)

    examples = {
        "USA Federal Criminal": [
            "What are the penalties for mail fraud under federal law?",
            "What constitutes money laundering?",
            "What are the elements of conspiracy to defraud the US?"
        ],
        "USA State Traffic": [
            "What is the speed limit in California?",
            "How many points for speeding in Texas?",
            "What are DUI penalties in Florida?"
        ],
        "Canada Criminal": [
            "What is the legal BAC limit in Canada?",
            "What constitutes assault with a weapon?",
            "What are impaired driving penalties?"
        ],
        "Canada Provincial": [
            "What are DUI penalties in Ontario?",
            "How many demerit points for speeding in BC?",
            "What are speeding fines in Alberta?"
        ],
        "Case Studies": [
            "What did Birchfield v. North Dakota decide?",
            "What is the Grant test for evidence?",
            "Can police demand breath tests without suspicion?"
        ],
        "Constitutional": [
            "What are Charter rights in Canada?",
            "What are Miranda rights?",
            "What is reasonable suspicion?"
        ]
    }

    for category, questions in examples.items():
        print(f"\n{category}:")
        for q in questions:
            print(f"  • {q}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    show_random_questions()
    show_specific_examples()
