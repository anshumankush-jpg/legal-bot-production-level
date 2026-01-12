"""Script to verify that the system is properly configured before ingestion."""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"[OK] Loaded .env file from {env_path}")
else:
    print(f"[WARNING] No .env file found at {env_path}")
    print("  You may need to create one with your API keys")

print("\n" + "="*70)
print("Setup Verification Checklist")
print("="*70)

# Check environment variables
checks = {
    "OpenAI API Key": os.getenv("OPENAI_API_KEY"),
    "Azure OpenAI Endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "Azure OpenAI API Key": os.getenv("AZURE_OPENAI_API_KEY"),
    "Azure Search Endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
    "Azure Search API Key": os.getenv("AZURE_SEARCH_API_KEY"),
}

print("\n1. Environment Variables:")
print("-" * 70)
all_configured = True

# Check LLM provider
llm_provider = os.getenv("LLM_PROVIDER", "openai")
print(f"   LLM Provider: {llm_provider}")

if llm_provider == "openai":
    if checks["OpenAI API Key"]:
        print("   [OK] OPENAI_API_KEY: Configured")
    else:
        print("   [X] OPENAI_API_KEY: Missing (required for OpenAI)")
        all_configured = False
elif llm_provider == "azure":
    if checks["Azure OpenAI Endpoint"] and checks["Azure OpenAI API Key"]:
        print("   [OK] AZURE_OPENAI_ENDPOINT: Configured")
        print("   [OK] AZURE_OPENAI_API_KEY: Configured")
    else:
        print("   [X] AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY: Missing (required for Azure)")
        all_configured = False

# Check vector store
use_azure_search = os.getenv("USE_AZURE_SEARCH", "false").lower() == "true"
if use_azure_search:
    if checks["Azure Search Endpoint"] and checks["Azure Search API Key"]:
        print("   [OK] AZURE_SEARCH_ENDPOINT: Configured")
        print("   [OK] AZURE_SEARCH_API_KEY: Configured")
    else:
        print("   [X] AZURE_SEARCH_ENDPOINT or AZURE_SEARCH_API_KEY: Missing (required for Azure Search)")
        all_configured = False
else:
    print("   [INFO] Using local FAISS (Azure Search not required)")

# Check Python packages
print("\n2. Python Packages:")
print("-" * 70)
required_packages = {
    "fastapi": "FastAPI framework",
    "uvicorn": "ASGI server",
    "openai": "OpenAI SDK",
    "requests": "HTTP library (for bulk ingestion)",
    "beautifulsoup4": "HTML parsing (for bulk ingestion)",
    "PyPDF2": "PDF processing (for bulk ingestion)",
}

missing_packages = []
for package, description in required_packages.items():
    try:
        __import__(package.replace("-", "_"))
        print(f"   [OK] {package}: Installed")
    except ImportError:
        print(f"   [X] {package}: Missing - {description}")
        missing_packages.append(package)

# Check document directories
print("\n3. Document Directories:")
print("-" * 70)
base_path = Path(__file__).parent.parent.parent
expected_dirs = [
    "canada criminal and federal law",
    "CANADA TRAFFIC FILES",
    "canada_traffic_acts",
    "us_traffic_laws",
    "usa_criminal_law",
    "us_state_codes",
    "paralegal_advice_dataset",
]

found_dirs = []
for dir_name in expected_dirs:
    dir_path = base_path / dir_name
    if dir_path.exists():
        # Count files
        pdf_count = len(list(dir_path.glob("*.pdf")))
        html_count = len(list(dir_path.glob("*.html"))) + len(list(dir_path.glob("*.htm")))
        json_count = len(list(dir_path.glob("*.json")))
        total = pdf_count + html_count + json_count
        print(f"   [OK] {dir_name}: Found ({total} files: {pdf_count} PDF, {html_count} HTML, {json_count} JSON)")
        found_dirs.append(dir_name)
    else:
        print(f"   [SKIP] {dir_name}: Not found (optional)")

if not found_dirs:
    print("   ✗ No document directories found!")
    print("   Make sure you're running this from the project root")

# Summary
print("\n" + "="*70)
print("Summary")
print("="*70)

if all_configured and not missing_packages:
    print("[SUCCESS] Configuration looks good!")
    print("\nYou can proceed with:")
    print("  1. Start backend: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("  2. Run bulk ingestion: python scripts/bulk_ingest_documents.py")
else:
    print("[WARNING] Some issues found:")
    if not all_configured:
        print("  - Missing required environment variables")
        print("    Create a .env file in the backend/ directory")
    if missing_packages:
        print(f"  - Missing Python packages: {', '.join(missing_packages)}")
        print("    Install with: pip install -r requirements.txt")
    print("\nPlease fix the issues above before proceeding.")

print("="*70)

