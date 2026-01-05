"""Script to index all HTML legal documents from the project folders."""
import sys
import logging
from pathlib import Path
import requests
from typing import Optional
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"


def extract_metadata_from_path(file_path: Path) -> tuple[Optional[str], Optional[str], list[str]]:
    """
    Extract organization, subject, and tags from file path.
    
    Returns:
        (organization, subject, tags)
    """
    organization = None
    subject = None
    tags = []
    
    # Get parent folder names
    parts = file_path.parts
    
    # Check for jurisdiction/province
    jurisdiction_map = {
        'alberta': 'Alberta',
        'british_columbia': 'British Columbia',
        'bc': 'British Columbia',
        'manitoba': 'Manitoba',
        'new_brunswick': 'New Brunswick',
        'newfoundland': 'Newfoundland',
        'nova_scotia': 'Nova Scotia',
        'ontario': 'Ontario',
        'pei': 'PEI',
        'prince_edward_island': 'PEI',
        'quebec': 'Quebec',
        'saskatchewan': 'Saskatchewan',
        'canada': 'Canada'
    }
    
    # Check for document type
    doc_type_map = {
        'traffic': 'traffic',
        'criminal': 'criminal',
        'highway': 'traffic',
        'motor_vehicle': 'traffic',
        'provincial_offences': 'traffic',
        'safety': 'traffic'
    }
    
    path_lower = str(file_path).lower()
    
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
    
    # Add file type tag
    tags.append('html')
    
    return organization, subject, tags


def index_html_file(file_path: Path, api_url: str = API_BASE_URL) -> bool:
    """Index a single HTML file."""
    try:
        logger.info(f"Indexing: {file_path.name}")
        
        # Extract metadata
        organization, subject, tags = extract_metadata_from_path(file_path)
        
        # Read file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        # Extract text using BeautifulSoup if available, otherwise use simple method
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
        except ImportError:
            # Simple fallback
            import re
            text = re.sub(r'<[^>]+>', '', html_content)
            text = ' '.join(text.split())
        
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
                    "file_type": "html",
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


def find_html_files(base_path: Path) -> list[Path]:
    """Find all HTML files in the project."""
    html_files = []
    
    # Directories to search
    search_dirs = [
        base_path.parent / "canada criminal and federal law",
        base_path.parent / "CANADA TRAFFIC FILES",
        base_path.parent / "canada_traffic_acts",
        base_path.parent / "canada_criminal_law",
        base_path.parent / "DATA SET",
        base_path.parent / "us_traffic_laws",
        base_path.parent / "usa_criminal_law",
        base_path.parent / "us_state_codes",
    ]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            logger.info(f"Searching in: {search_dir}")
            html_files.extend(search_dir.glob("*.html"))
            html_files.extend(search_dir.glob("*.htm"))
        else:
            logger.warning(f"Directory not found: {search_dir}")
    
    return html_files


def main():
    """Main function to index all HTML documents."""
    base_path = Path(__file__).parent.parent
    
    logger.info("=" * 60)
    logger.info("HTML Document Indexing Script")
    logger.info("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            logger.error(f"API health check failed. Is the backend running at {API_BASE_URL}?")
            return
        logger.info(f"✓ Backend API is running at {API_BASE_URL}")
    except requests.exceptions.RequestException as e:
        logger.error(f"✗ Cannot connect to backend API at {API_BASE_URL}")
        logger.error("Please start the backend server first: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return
    
    # Find all HTML files
    logger.info("\nSearching for HTML files...")
    html_files = find_html_files(base_path)
    
    if not html_files:
        logger.warning("No HTML files found!")
        return
    
    logger.info(f"Found {len(html_files)} HTML files to index\n")
    
    # Index files
    success_count = 0
    fail_count = 0
    
    for i, html_file in enumerate(html_files, 1):
        logger.info(f"[{i}/{len(html_files)}] Processing: {html_file.name}")
        
        if index_html_file(html_file):
            success_count += 1
        else:
            fail_count += 1
        
        # Small delay to avoid overwhelming the API
        time.sleep(0.5)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Indexing Complete!")
    logger.info(f"Successfully indexed: {success_count}")
    logger.info(f"Failed: {fail_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

