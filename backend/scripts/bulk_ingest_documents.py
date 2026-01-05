"""Comprehensive script to bulk ingest all legal documents (PDF, HTML, JSON) into the vector database."""
import sys
import logging
from pathlib import Path
import requests
from typing import Optional, List
import time
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"


def extract_metadata_from_path(file_path: Path) -> tuple[Optional[str], Optional[str], List[str]]:
    """
    Extract organization, subject, and tags from file path.
    
    Returns:
        (organization, subject, tags)
    """
    organization = None
    subject = None
    tags = []
    
    path_lower = str(file_path).lower()
    
    # Jurisdiction mapping
    jurisdiction_map = {
        'alberta': 'Alberta', 'british_columbia': 'British Columbia', 'bc': 'British Columbia',
        'manitoba': 'Manitoba', 'new_brunswick': 'New Brunswick', 'newfoundland': 'Newfoundland',
        'nova_scotia': 'Nova Scotia', 'ontario': 'Ontario', 'pei': 'PEI',
        'prince_edward_island': 'PEI', 'quebec': 'Quebec', 'saskatchewan': 'Saskatchewan',
        'canada': 'Canada',
        # US States
        'california': 'California', 'texas': 'Texas', 'florida': 'Florida', 'new_york': 'New York',
        'pennsylvania': 'Pennsylvania', 'illinois': 'Illinois', 'ohio': 'Ohio', 'michigan': 'Michigan',
        'georgia': 'Georgia', 'north_carolina': 'North Carolina', 'new_jersey': 'New Jersey',
        'virginia': 'Virginia', 'washington': 'Washington', 'arizona': 'Arizona', 'massachusetts': 'Massachusetts',
        'tennessee': 'Tennessee', 'indiana': 'Indiana', 'missouri': 'Missouri', 'maryland': 'Maryland',
        'wisconsin': 'Wisconsin', 'colorado': 'Colorado', 'minnesota': 'Minnesota', 'south_carolina': 'South Carolina',
        'alabama': 'Alabama', 'louisiana': 'Louisiana', 'kentucky': 'Kentucky', 'oregon': 'Oregon',
        'oklahoma': 'Oklahoma', 'connecticut': 'Connecticut', 'utah': 'Utah', 'iowa': 'Iowa',
        'nevada': 'Nevada', 'arkansas': 'Arkansas', 'mississippi': 'Mississippi', 'kansas': 'Kansas',
        'new_mexico': 'New Mexico', 'nebraska': 'Nebraska', 'west_virginia': 'West Virginia',
        'idaho': 'Idaho', 'hawaii': 'Hawaii', 'new_hampshire': 'New Hampshire', 'maine': 'Maine',
        'montana': 'Montana', 'rhode_island': 'Rhode Island', 'delaware': 'Delaware', 'south_dakota': 'South Dakota',
        'north_dakota': 'North Dakota', 'alaska': 'Alaska', 'vermont': 'Vermont', 'wyoming': 'Wyoming',
        'usa': 'United States', 'us': 'United States'
    }
    
    # Document type mapping
    doc_type_map = {
        'traffic': 'traffic', 'criminal': 'criminal', 'highway': 'traffic',
        'motor_vehicle': 'traffic', 'provincial_offences': 'traffic', 'safety': 'traffic',
        'vehicle': 'traffic', 'code': 'statute', 'statute': 'statute', 'law': 'law'
    }
    
    # Extract jurisdiction
    for key, value in jurisdiction_map.items():
        if key in path_lower:
            organization = value
            tags.append(value.lower().replace(' ', '_'))
            break
    
    # Extract document type
    for key, value in doc_type_map.items():
        if key in path_lower:
            tags.append(value)
            if not subject:
                subject = value.title() + " Law"
            break
    
    # Extract subject from filename
    filename_lower = file_path.stem.lower()
    if 'traffic' in filename_lower or 'highway' in filename_lower or 'motor_vehicle' in filename_lower:
        subject = "Traffic Law"
        tags.append('traffic')
    elif 'criminal' in filename_lower:
        subject = "Criminal Law"
        tags.append('criminal')
    elif 'case' in filename_lower or 'precedent' in filename_lower:
        subject = "Case Law"
        tags.append('case_law')
    
    # Add file type tag
    if file_path.suffix.lower() == '.pdf':
        tags.append('pdf')
    elif file_path.suffix.lower() in ['.html', '.htm']:
        tags.append('html')
    elif file_path.suffix.lower() == '.json':
        tags.append('json')
    
    return organization, subject, tags


def extract_text_from_html(file_path: Path) -> str:
    """Extract text from HTML file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            return text
        except ImportError:
            import re
            text = re.sub(r'<[^>]+>', '', html_content)
            text = ' '.join(text.split())
            return text
    except Exception as e:
        logger.error(f"Error reading HTML file {file_path}: {e}")
        return ""


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF file with multiple fallback methods."""
    text = ""
    
    # Method 1: Try pdfplumber (best for text-based PDFs, handles tables well)
    try:
        import pdfplumber
        logger.info(f"Using pdfplumber for {file_path.name}")
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                # Also try extracting tables if present
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            if row:
                                text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
        if text.strip():
            logger.info(f"✓ Successfully extracted {len(text)} chars using pdfplumber")
            return text
    except ImportError:
        logger.debug("pdfplumber not available, trying PyPDF2")
    except Exception as e:
        logger.warning(f"pdfplumber failed for {file_path.name}: {e}, trying PyPDF2")
    
    # Method 2: Try PyPDF2 (fallback)
    try:
        import PyPDF2
        logger.info(f"Using PyPDF2 for {file_path.name}")
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            logger.info(f"✓ Successfully extracted {len(text)} chars using PyPDF2")
            return text
    except ImportError:
        logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
    except Exception as e:
        logger.warning(f"PyPDF2 failed for {file_path.name}: {e}, trying pypdf")
    
    # Method 3: Try pypdf (newer alternative)
    try:
        import pypdf
        logger.info(f"Using pypdf for {file_path.name}")
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            logger.info(f"✓ Successfully extracted {len(text)} chars using pypdf")
            return text
    except ImportError:
        logger.debug("pypdf not available")
    except Exception as e:
        logger.warning(f"pypdf failed for {file_path.name}: {e}")
    
    # Method 4: Try OCR if text extraction failed (for scanned PDFs)
    if not text.strip():
        try:
            from app.ocr.ocr_service import get_ocr_service
            logger.info(f"Attempting OCR for {file_path.name} (may be scanned PDF)")
            ocr_service = get_ocr_service()
            # Convert PDF pages to images and OCR them
            # For now, just log that OCR would be needed
            logger.warning(f"PDF {file_path.name} appears to be image-based. OCR support for multi-page PDFs requires additional setup.")
            return ""
        except Exception as e:
            logger.error(f"OCR attempt failed for {file_path.name}: {e}")
    
    if not text.strip():
        logger.error(f"Failed to extract text from PDF {file_path.name} using all methods")
    
    return text


def ingest_json_case_studies(file_path: Path, api_url: str = API_BASE_URL) -> int:
    """Ingest JSON files (case studies, demerit tables, guides, etc.)."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        count = 0
        
        # Determine document type from path
        path_str = str(file_path).lower()
        is_demerit_table = 'demerit' in path_str
        is_fight_guide = 'fight' in path_str or 'process' in path_str
        is_ticket = 'ticket' in path_str
        is_lawyer = 'lawyer' in path_str
        
        # Extract metadata from path
        organization, subject, tags = extract_metadata_from_path(file_path)
        
        # Determine subject based on file type
        if not subject:
            if is_demerit_table:
                subject = 'Demerit Points Table'
                tags.append('demerit_points')
            elif is_fight_guide:
                subject = 'Fight Process Guide'
                tags.append('fight_process')
            elif is_ticket:
                subject = 'Example Ticket'
                tags.append('example_ticket')
            elif is_lawyer:
                subject = 'Lawyer Directory'
                tags.append('lawyer_directory')
            else:
                subject = 'Legal Data'
        
        if isinstance(data, list):
            # Handle array of objects (case studies, etc.)
            for item in data:
                if isinstance(item, dict):
                    # Extract item information
                    item_text = json.dumps(item, indent=2)
                    item_title = item.get('title', item.get('case_name', item.get('name', 'Unknown')))
                    
                    params = {}
                    if organization:
                        params['organization'] = organization
                    if subject:
                        params['subject'] = subject
                    
                    response = requests.post(
                        f"{api_url}/api/ingest/text",
                        json={
                            "text": item_text,
                            "source_name": f"{file_path.stem}_{item_title}",
                            "tags": tags + ['json', 'structured_data'],
                            "metadata": {
                                "original_filename": str(file_path),
                                "item_title": item_title,
                                "file_type": "json",
                                "data_type": "array_item"
                            }
                        },
                        params=params,
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        count += 1
                        logger.info(f"  ✓ Indexed: {item_title}")
                    else:
                        logger.warning(f"  ✗ Failed: {response.status_code}")
                    
                    time.sleep(0.2)  # Rate limiting
        elif isinstance(data, dict):
            # Handle single object (demerit tables, guides, etc.)
            json_text = json.dumps(data, indent=2)
            
            params = {}
            if organization:
                params['organization'] = organization
            if subject:
                params['subject'] = subject
            
            response = requests.post(
                f"{api_url}/api/ingest/text",
                json={
                    "text": json_text,
                    "source_name": file_path.stem,
                    "tags": tags + ['json', 'structured_data'],
                    "metadata": {
                        "original_filename": str(file_path),
                        "file_type": "json",
                        "data_type": "single_object"
                    }
                },
                params=params,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                count = 1
                logger.info(f"  ✓ Indexed {file_path.name} - {result.get('chunks', 0)} chunks")
            else:
                logger.error(f"  ✗ Failed: {response.status_code} - {response.text}")
        
        return count
    except Exception as e:
        logger.error(f"Error processing JSON file {file_path}: {e}")
        return 0


def ingest_file(file_path: Path, api_url: str = API_BASE_URL) -> bool:
    """Ingest a single file (PDF, HTML, or JSON)."""
    try:
        file_ext = file_path.suffix.lower()
        logger.info(f"Indexing: {file_path.name}")
        
        # Extract metadata
        organization, subject, tags = extract_metadata_from_path(file_path)
        
        # Extract text based on file type
        if file_ext == '.json':
            # Handle JSON case studies separately
            count = ingest_json_case_studies(file_path, api_url)
            if count > 0:
                logger.info(f"✓ Indexed {count} cases from {file_path.name}")
                return True
            return False
        
        elif file_ext in ['.html', '.htm']:
            text = extract_text_from_html(file_path)
        elif file_ext == '.pdf':
            text = extract_text_from_pdf(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_ext}")
            return False
        
        if not text.strip() or len(text.strip()) < 100:
            logger.warning(f"Skipping {file_path.name}: extracted text too short or empty")
            return False
        
        # Prepare request
        params = {}
        if organization:
            params['organization'] = organization
        if subject:
            params['subject'] = subject
        
        # Ingest via API
        response = requests.post(
            f"{api_url}/api/ingest/text",
            json={
                "text": text,
                "source_name": file_path.name,
                "tags": tags,
                "metadata": {
                    "original_filename": str(file_path),
                    "file_type": file_ext[1:],  # Remove the dot
                    "jurisdiction": organization or "Unknown"
                }
            },
            params=params,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✓ Indexed {file_path.name} - {result.get('chunks', 0)} chunks")
            return True
        else:
            logger.error(f"✗ Failed to index {file_path.name}: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Error indexing {file_path.name}: {e}")
        return False


def find_all_documents(base_path: Path) -> dict:
    """Find all documents (PDF, HTML, JSON) in the project."""
    documents = {
        'pdf': [],
        'html': [],
        'json': []
    }
    
    # Directories to search
    search_dirs = [
        base_path.parent / "data",  # Main data folder with JSON files
        base_path.parent / "canada criminal and federal law",
        base_path.parent / "CANADA TRAFFIC FILES",
        base_path.parent / "canada_traffic_acts",
        base_path.parent / "canada_criminal_law",
        base_path.parent / "DATA SET",
        base_path.parent / "us_traffic_laws",
        base_path.parent / "usa_criminal_law",
        base_path.parent / "us_state_codes",
        base_path.parent / "paralegal_advice_dataset",
    ]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            logger.info(f"Searching in: {search_dir}")
            # Search recursively for all file types
            documents['pdf'].extend(search_dir.rglob("*.pdf"))
            documents['html'].extend(search_dir.rglob("*.html"))
            documents['html'].extend(search_dir.rglob("*.htm"))
            documents['json'].extend(search_dir.rglob("*.json"))
        else:
            logger.warning(f"Directory not found: {search_dir}")
    
    return documents


def main():
    """Main function to bulk ingest all documents."""
    base_path = Path(__file__).parent.parent
    
    logger.info("=" * 70)
    logger.info("Bulk Document Ingestion Script")
    logger.info("=" * 70)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            logger.error(f"API health check failed. Is the backend running at {API_BASE_URL}?")
            return
        logger.info(f"✓ Backend API is running at {API_BASE_URL}")
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Cannot connect to backend API at {API_BASE_URL}")
        logger.error("Please start the backend server first:")
        logger.error("  cd backend")
        logger.error("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return
    
    # Find all documents
    logger.info("\nSearching for documents...")
    all_docs = find_all_documents(base_path)
    
    total_files = sum(len(files) for files in all_docs.values())
    
    if total_files == 0:
        logger.warning("No documents found!")
        return
    
    logger.info(f"\nFound documents:")
    logger.info(f"  PDF files: {len(all_docs['pdf'])}")
    logger.info(f"  HTML files: {len(all_docs['html'])}")
    logger.info(f"  JSON files: {len(all_docs['json'])}")
    logger.info(f"  Total: {total_files}\n")
    
    # Confirm before proceeding
    response = input("Do you want to proceed with ingestion? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        logger.info("Ingestion cancelled.")
        return
    
    # Ingest files
    success_count = 0
    fail_count = 0
    
    all_files = all_docs['pdf'] + all_docs['html'] + all_docs['json']
    
    for i, file_path in enumerate(all_files, 1):
        logger.info(f"\n[{i}/{total_files}] Processing: {file_path.name}")
        
        if ingest_file(file_path):
            success_count += 1
        else:
            fail_count += 1
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.5)
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("Bulk Ingestion Complete!")
    logger.info(f"Successfully indexed: {success_count}")
    logger.info(f"Failed: {fail_count}")
    logger.info("=" * 70)
    logger.info("\nYou can now query your documents using the chat interface!")


if __name__ == "__main__":
    main()

