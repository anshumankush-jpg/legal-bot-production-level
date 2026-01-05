"""
Legal Dataset Processor - Agent Mode Implementation

This script implements the complete workflow for making legal datasets searchable:
1. Extract text from HTML and PDFs if needed
2. Chunk the text appropriately
3. Create embeddings using SentenceTransformer
4. Index the embeddings so the search engine can query them
5. Ensure the search engine retrieves results based on the embedded datasets and responds accordingly

Enhanced features:
- PDF link extraction from HTML index files
- Automatic PDF downloading and processing
- Performance comparison between HTML and PDF sources
- Comprehensive benchmarking
"""

import sys
import logging
import requests
import json
import time
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple
import hashlib
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('legal_dataset_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"


class LegalDatasetProcessor:
    """
    Comprehensive processor for legal datasets with PDF link extraction,
    text processing, embedding, and search indexing.
    """

    def __init__(self, api_url: str = API_BASE_URL, max_workers: int = 4):
        self.api_url = api_url
        self.max_workers = max_workers
        self.downloaded_pdfs = set()
        self.processed_files = {
            'html_index_files': 0,
            'pdf_links_found': 0,
            'pdfs_downloaded': 0,
            'pdfs_processed': 0,
            'documents_indexed': 0,
            'chunks_created': 0
        }

    def check_backend_health(self) -> bool:
        """Check if backend is running and healthy."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                health = response.json()
                index_size = health.get('index_size', 0)
                logger.info(f"✓ Backend is healthy - {index_size} documents indexed")
                return True
            else:
                logger.error(f"✗ Backend returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ Cannot connect to backend: {e}")
            return False

    def extract_pdf_links_from_html(self, html_file: Path) -> List[Dict[str, str]]:
        """
        Extract PDF links from HTML index files.

        Looks for:
        - <a href="*.pdf"> links
        - Handles relative and absolute URLs
        - Extracts link text as titles
        """
        pdf_links = []

        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find all links to PDFs
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and href.lower().endswith('.pdf'):
                    # Get link text as title
                    title = link.get_text().strip()
                    if not title:
                        title = href.split('/')[-1].replace('.pdf', '')

                    # Convert relative URLs to absolute if possible
                    if href.startswith('/'):
                        # Try to reconstruct base URL from filename or content
                        base_url = self._guess_base_url_from_html(html_file, soup)
                        if base_url:
                            full_url = urljoin(base_url, href)
                        else:
                            continue
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue

                    pdf_links.append({
                        'url': full_url,
                        'title': title,
                        'source_html': str(html_file),
                        'link_text': link.get_text().strip(),
                        'html_filename': html_file.name
                    })

            logger.info(f"Found {len(pdf_links)} PDF links in {html_file.name}")

        except Exception as e:
            logger.error(f"Error extracting PDF links from {html_file}: {e}")

        return pdf_links

    def _guess_base_url_from_html(self, html_file: Path, soup) -> Optional[str]:
        """Guess base URL from HTML file content."""
        # Common legal website patterns
        filename = html_file.name.lower()

        # Oklahoma State Courts Network
        if 'oklahoma' in filename:
            return "https://www.oscn.net/"

        # Try to find base URL in HTML
        base_tag = soup.find('base', href=True)
        if base_tag:
            return base_tag.get('href')

        # Try to find canonical URL or og:url
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            parsed = urlparse(canonical.get('href'))
            return f"{parsed.scheme}://{parsed.netloc}"

        # Look for OSCN pattern in links
        oscn_links = soup.find_all('a', href=re.compile(r'https?://www\.oscn\.net'))
        if oscn_links:
            return "https://www.oscn.net/"

        return None

    def download_pdf(self, pdf_info: Dict[str, str], download_dir: Path) -> Optional[Path]:
        """Download a PDF file with error handling and deduplication."""
        url = pdf_info['url']
        title = pdf_info['title']

        # Create safe filename
        safe_title = re.sub(r'[^\w\-_\.]', '_', title)[:80]
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"{safe_title}_{url_hash}.pdf"
        pdf_path = download_dir / filename

        # Skip if already downloaded
        if pdf_path.exists() and pdf_path.stat().st_size > 0:
            logger.debug(f"✓ PDF already exists: {filename}")
            return pdf_path

        try:
            logger.info(f"Downloading: {title} from {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, timeout=30, headers=headers, stream=True)
            response.raise_for_status()

            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Verify PDF
            if pdf_path.stat().st_size < 1000:  # Less than 1KB
                logger.warning(f"Downloaded file too small: {filename} ({pdf_path.stat().st_size} bytes)")
                pdf_path.unlink()
                return None

            logger.info(f"✓ Downloaded: {filename} ({pdf_path.stat().st_size} bytes)")
            return pdf_path

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to download {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"✗ Unexpected error downloading {url}: {e}")
            return None

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from PDF using multiple methods with enhanced error handling.

        Priority:
        1. pdfplumber (best for text-based PDFs with tables)
        2. PyPDF2 (reliable fallback)
        3. pypdf (modern alternative)
        4. OCR for image-based PDFs (if OCR service available)
        """
        text_parts = []

        # Method 1: pdfplumber (best for text-based PDFs)
        try:
            import pdfplumber
            logger.debug(f"Using pdfplumber for {pdf_path.name}")
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}")

                    # Extract tables if present
                    tables = page.extract_tables()
                    if tables:
                        for table_idx, table in enumerate(tables):
                            table_text = f"\nTable {table_idx + 1} on Page {page_num}:\n"
                            for row in table:
                                if row:
                                    table_text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                            text_parts.append(table_text)

            if text_parts:
                full_text = '\n\n'.join(text_parts)
                logger.info(f"✓ Extracted {len(full_text)} chars using pdfplumber from {pdf_path.name}")
                return full_text

        except ImportError:
            logger.debug("pdfplumber not available")
        except Exception as e:
            logger.warning(f"pdfplumber failed for {pdf_path.name}: {e}")

        # Method 2: PyPDF2
        try:
            import PyPDF2
            logger.debug(f"Using PyPDF2 for {pdf_path.name}")
            text_parts = []
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}")

            if text_parts:
                full_text = '\n\n'.join(text_parts)
                logger.info(f"✓ Extracted {len(full_text)} chars using PyPDF2 from {pdf_path.name}")
                return full_text

        except ImportError:
            logger.debug("PyPDF2 not available")
        except Exception as e:
            logger.warning(f"PyPDF2 failed for {pdf_path.name}: {e}")

        # Method 3: pypdf
        try:
            import pypdf
            logger.debug(f"Using pypdf for {pdf_path.name}")
            text_parts = []
            with open(pdf_path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}")

            if text_parts:
                full_text = '\n\n'.join(text_parts)
                logger.info(f"✓ Extracted {len(full_text)} chars using pypdf from {pdf_path.name}")
                return full_text

        except ImportError:
            logger.debug("pypdf not available")
        except Exception as e:
            logger.warning(f"pypdf failed for {pdf_path.name}: {e}")

        # Method 4: OCR for image-based PDFs
        try:
            logger.info(f"Attempting OCR for {pdf_path.name} (may be image-based PDF)")
            from app.ocr.ocr_service import get_ocr_service
            ocr_service = get_ocr_service()

            # For multi-page PDFs, we'd need to convert to images first
            # This is a simplified version - in production you'd convert each page to image
            logger.warning(f"OCR for multi-page PDFs requires additional image processing setup")
            return ""

        except Exception as e:
            logger.error(f"OCR attempt failed for {pdf_path.name}: {e}")

        logger.error(f"Failed to extract text from PDF {pdf_path.name} using all methods")
        return ""

    def extract_text_from_html(self, html_path: Path) -> str:
        """Extract clean text from HTML files."""
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
                element.decompose()

            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)

            logger.info(f"✓ Extracted {len(clean_text)} chars from HTML {html_path.name}")
            return clean_text

        except Exception as e:
            logger.error(f"Error extracting text from HTML {html_path}: {e}")
            return ""

    def chunk_text_appropriately(self, text: str, source_type: str = "document") -> List[str]:
        """
        Chunk text using appropriate strategy based on content type.

        Uses the same chunking logic as the RAG service for consistency.
        """
        if not text or len(text.strip()) < 100:
            return []

        # Use RAG service chunking for consistency
        from app.rag.rag_service import get_rag_service
        rag_service = get_rag_service()

        # For documents, use child chunk size with overlap
        chunk_size = rag_service.child_chunk_size
        overlap = rag_service.child_chunk_overlap

        chunks = rag_service.chunk_text(text, chunk_size, overlap)

        # Filter out very small chunks
        chunks = [chunk for chunk in chunks if len(chunk.strip()) >= 50]

        logger.info(f"✓ Created {len(chunks)} chunks from {len(text)} chars")
        return chunks

    def create_embeddings_and_index(self, text: str, source_name: str, source_type: str = "document",
                                   organization: Optional[str] = None, subject: Optional[str] = None,
                                   metadata: Optional[Dict] = None) -> Dict:
        """
        Create embeddings using SentenceTransformer and index them for search.

        This uses the existing RAG service ingestion pipeline.
        """
        try:
            from app.rag.rag_service import get_rag_service
            rag_service = get_rag_service()

            # Ingest text using RAG service
            result = rag_service.ingest_text(
                text=text,
                source_name=source_name,
                source_type=source_type,
                organization=organization,
                subject=subject,
                metadata=metadata or {}
            )

            logger.info(f"✓ Indexed document '{source_name}' with {result.get('chunks', 0)} chunks")
            return result

        except Exception as e:
            logger.error(f"✗ Failed to create embeddings and index for {source_name}: {e}")
            return {'error': str(e)}

    def process_html_index_file(self, html_file: Path, pdf_download_dir: Path) -> Dict[str, int]:
        """
        Process a single HTML index file:
        1. Extract PDF links
        2. Download PDFs
        3. Extract text and index
        """
        results = {
            'pdf_links_found': 0,
            'pdfs_downloaded': 0,
            'pdfs_processed': 0,
            'documents_indexed': 0,
            'chunks_created': 0
        }

        logger.info(f"Processing HTML index: {html_file.name}")

        # Extract PDF links
        pdf_links = self.extract_pdf_links_from_html(html_file)
        results['pdf_links_found'] = len(pdf_links)

        if not pdf_links:
            logger.info(f"No PDF links found in {html_file.name}")
            return results

        # Download PDFs concurrently
        downloaded_paths = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_pdf = {
                executor.submit(self.download_pdf, pdf_info, pdf_download_dir): pdf_info
                for pdf_info in pdf_links
            }

            for future in as_completed(future_to_pdf):
                pdf_info = future_to_pdf[future]
                try:
                    pdf_path = future.result()
                    if pdf_path:
                        downloaded_paths.append((pdf_path, pdf_info))
                        results['pdfs_downloaded'] += 1
                except Exception as e:
                    logger.error(f"Error downloading {pdf_info['url']}: {e}")

        # Process downloaded PDFs
        for pdf_path, pdf_info in downloaded_paths:
            try:
                # Extract text
                text = self.extract_text_from_pdf(pdf_path)
                if not text or len(text.strip()) < 500:  # Minimum content threshold
                    logger.warning(f"Skipping {pdf_path.name}: insufficient text")
                    continue

                # Index the document
                metadata = {
                    'original_filename': str(pdf_path),
                    'source_url': pdf_info['url'],
                    'source_html': pdf_info['source_html'],
                    'title': pdf_info['title'],
                    'downloaded_at': time.time()
                }

                # Extract organization from HTML filename
                organization = self._extract_organization_from_filename(pdf_info['html_filename'])

                result = self.create_embeddings_and_index(
                    text=text,
                    source_name=f"{pdf_info['title']} ({pdf_path.name})",
                    source_type="pdf",
                    organization=organization,
                    subject="Legal Document",
                    metadata=metadata
                )

                if 'doc_id' in result:
                    results['pdfs_processed'] += 1
                    results['documents_indexed'] += 1
                    results['chunks_created'] += result.get('chunks', 0)

            except Exception as e:
                logger.error(f"Error processing PDF {pdf_path}: {e}")

        return results

    def _extract_organization_from_filename(self, filename: str) -> Optional[str]:
        """Extract organization/state from filename."""
        filename_lower = filename.lower()

        # State mappings
        states = {
            'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
            'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
            'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana',
            'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota',
            'mississippi', 'missouri', 'montana', 'nebraska', 'nevada',
            'new_hampshire', 'new_jersey', 'new_mexico', 'new_york',
            'north_carolina', 'north_dakota', 'ohio', 'oklahoma', 'oregon',
            'pennsylvania', 'rhode_island', 'south_carolina', 'south_dakota',
            'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington',
            'west_virginia', 'wisconsin', 'wyoming', 'canada', 'ontario',
            'british_columbia', 'quebec'
        }

        for state in states:
            if state in filename_lower:
                return state.title().replace('_', ' ')

        return None

    def process_directory(self, input_dir: Path, pdf_download_dir: Path) -> Dict[str, int]:
        """
        Process all HTML and PDF files in a directory.

        Workflow:
        1. Find HTML index files and extract PDF links
        2. Download and process PDFs
        3. Process standalone PDF and HTML files
        """
        logger.info(f"Starting legal dataset processing in: {input_dir}")

        # Ensure download directory exists
        pdf_download_dir.mkdir(parents=True, exist_ok=True)

        total_results = {
            'html_files_processed': 0,
            'pdf_links_found': 0,
            'pdfs_downloaded': 0,
            'pdfs_processed': 0,
            'standalone_pdfs_processed': 0,
            'standalone_htmls_processed': 0,
            'documents_indexed': 0,
            'chunks_created': 0
        }

        # Process HTML index files first
        html_files = list(input_dir.glob("*.html")) + list(input_dir.glob("*.htm"))
        logger.info(f"Found {len(html_files)} HTML files to process")

        for html_file in html_files:
            try:
                results = self.process_html_index_file(html_file, pdf_download_dir)

                # Update totals
                for key, value in results.items():
                    total_results[key] += value
                total_results['html_files_processed'] += 1

            except Exception as e:
                logger.error(f"Error processing HTML file {html_file}: {e}")

        # Process standalone PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} standalone PDF files")

        for pdf_file in pdf_files:
            try:
                # Skip downloaded PDFs
                if pdf_file.parent == pdf_download_dir:
                    continue

                text = self.extract_text_from_pdf(pdf_file)
                if not text or len(text.strip()) < 500:
                    logger.warning(f"Skipping {pdf_file.name}: insufficient text")
                    continue

                organization = self._extract_organization_from_filename(pdf_file.name)

                result = self.create_embeddings_and_index(
                    text=text,
                    source_name=pdf_file.name,
                    source_type="pdf",
                    organization=organization,
                    subject="Legal Document",
                    metadata={'original_filename': str(pdf_file)}
                )

                if 'doc_id' in result:
                    total_results['standalone_pdfs_processed'] += 1
                    total_results['documents_indexed'] += 1
                    total_results['chunks_created'] += result.get('chunks', 0)

            except Exception as e:
                logger.error(f"Error processing standalone PDF {pdf_file}: {e}")

        # Process standalone HTML files (not index files)
        for html_file in html_files:
            try:
                # Skip if already processed as index file
                if html_file.stat().st_mtime < time.time() - 3600:  # Processed more than 1 hour ago
                    continue

                text = self.extract_text_from_html(html_file)
                if not text or len(text.strip()) < 500:
                    logger.warning(f"Skipping {html_file.name}: insufficient text")
                    continue

                organization = self._extract_organization_from_filename(html_file.name)

                result = self.create_embeddings_and_index(
                    text=text,
                    source_name=html_file.name,
                    source_type="html",
                    organization=organization,
                    subject="Legal Index",
                    metadata={'original_filename': str(html_file)}
                )

                if 'doc_id' in result:
                    total_results['standalone_htmls_processed'] += 1
                    total_results['documents_indexed'] += 1
                    total_results['chunks_created'] += result.get('chunks', 0)

            except Exception as e:
                logger.error(f"Error processing standalone HTML {html_file}: {e}")

        return total_results

    def run_search_test(self, question: str) -> Dict:
        """Run a search test and analyze results."""
        try:
            response = requests.post(
                f"{self.api_url}/api/query/answer",
                json={"question": question},
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                sources = data.get('sources', [])

                # Analyze sources by type
                pdf_sources = [s for s in sources if '.pdf' in s.get('source_name', '').lower()]
                html_sources = [s for s in sources if any(ext in s.get('source_name', '').lower()
                                                        for ext in ['.html', '.htm'])]

                return {
                    'question': question,
                    'success': True,
                    'answer': data.get('answer', ''),
                    'total_sources': len(sources),
                    'pdf_sources': len(pdf_sources),
                    'html_sources': len(html_sources),
                    'sources': sources[:10]  # First 10 sources
                }
            else:
                return {
                    'question': question,
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                'question': question,
                'success': False,
                'error': str(e)
            }

    def generate_report(self, results: Dict, test_results: List[Dict] = None) -> str:
        """Generate a comprehensive processing report."""
        report = []
        report.append("=" * 80)
        report.append("LEGAL DATASET PROCESSOR - EXECUTION REPORT")
        report.append("=" * 80)
        report.append("")

        # Processing Summary
        report.append("📊 PROCESSING SUMMARY:")
        report.append("-" * 40)
        report.append(f"HTML index files processed: {results.get('html_files_processed', 0)}")
        report.append(f"PDF links found: {results.get('pdf_links_found', 0)}")
        report.append(f"PDFs downloaded: {results.get('pdfs_downloaded', 0)}")
        report.append(f"PDFs processed: {results.get('pdfs_processed', 0)}")
        report.append(f"Standalone PDFs processed: {results.get('standalone_pdfs_processed', 0)}")
        report.append(f"Standalone HTMLs processed: {results.get('standalone_htmls_processed', 0)}")
        report.append(f"Total documents indexed: {results.get('documents_indexed', 0)}")
        report.append(f"Total chunks created: {results.get('chunks_created', 0)}")
        report.append("")

        # Performance Analysis
        if results.get('chunks_created', 0) > 0 and results.get('documents_indexed', 0) > 0:
            avg_chunks_per_doc = results['chunks_created'] / results['documents_indexed']
            report.append("📈 PERFORMANCE METRICS:")
            report.append("-" * 40)
            report.append(f"Average chunks per document: {avg_chunks_per_doc:.1f}")
            report.append("")

        # Search Test Results
        if test_results:
            report.append("🔍 SEARCH PERFORMANCE TEST:")
            report.append("-" * 40)

            successful_tests = [t for t in test_results if t.get('success', False)]
            if successful_tests:
                total_sources = sum(t.get('total_sources', 0) for t in successful_tests)
                pdf_sources = sum(t.get('pdf_sources', 0) for t in successful_tests)
                html_sources = sum(t.get('html_sources', 0) for t in successful_tests)

                avg_total_sources = total_sources / len(successful_tests)
                pdf_percentage = (pdf_sources / total_sources * 100) if total_sources > 0 else 0
                html_percentage = (html_sources / total_sources * 100) if total_sources > 0 else 0

                report.append(f"Test queries run: {len(test_results)}")
                report.append(f"Successful queries: {len(successful_tests)}")
                report.append(f"Average sources per query: {avg_total_sources:.1f}")
                report.append(f"PDF sources: {pdf_percentage:.1f}%")
                report.append(f"HTML sources: {html_percentage:.1f}%")

                if pdf_percentage > html_percentage:
                    report.append("→ PDFs are providing more relevant search results")
                elif html_percentage > pdf_percentage:
                    report.append("→ HTML files are providing more relevant search results")
                else:
                    report.append("→ PDF and HTML sources are equally relevant")
            else:
                report.append("❌ All search tests failed")
            report.append("")

        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        report.append("-" * 40)
        if results.get('pdfs_processed', 0) > 0:
            report.append("✓ PDF processing is working - PDFs provide rich legal content")
        if results.get('html_files_processed', 0) > 0:
            report.append("✓ HTML index processing is working - Good for navigation and links")
        if results.get('chunks_created', 0) > 1000:
            report.append("✓ Large document corpus indexed - Good for comprehensive search")
        if test_results and len([t for t in test_results if t.get('success', False)]) > 0:
            report.append("✓ Search functionality is operational")
        report.append("")

        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Legal Dataset Processor - Make legal documents searchable",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process USA legal documents
  python legal_dataset_processor.py --input-dir ../USA --run-tests

  # Process with custom settings
  python legal_dataset_processor.py --input-dir ../canada_criminal_law --workers 2 --no-tests

  # Just run search tests on existing index
  python legal_dataset_processor.py --test-only
        """
    )

    parser.add_argument(
        '--input-dir',
        type=str,
        default='../USA',
        help='Input directory containing HTML and PDF files (default: ../USA)'
    )

    parser.add_argument(
        '--download-dir',
        type=str,
        default='../data/downloaded_pdfs',
        help='Directory to store downloaded PDFs (default: ../data/downloaded_pdfs)'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of concurrent workers for downloading (default: 4)'
    )

    parser.add_argument(
        '--run-tests',
        action='store_true',
        help='Run search performance tests after processing'
    )

    parser.add_argument(
        '--test-only',
        action='store_true',
        help='Only run search tests, skip document processing'
    )

    parser.add_argument(
        '--api-url',
        type=str,
        default='http://localhost:8000',
        help='Backend API URL (default: http://localhost:8000)'
    )

    args = parser.parse_args()

    # Initialize processor
    processor = LegalDatasetProcessor(api_url=args.api_url, max_workers=args.workers)

    # Check backend health
    if not processor.check_backend_health():
        logger.error("❌ Backend not available. Please start it first:")
        logger.error("  cd backend")
        logger.error("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return 1

    input_dir = Path(args.input_dir)
    download_dir = Path(args.download_dir)

    if args.test_only:
        # Run only search tests
        logger.info("Running search performance tests only...")
        test_questions = [
            "What are the penalties for speeding in Oklahoma?",
            "What is the statute of limitations for traffic violations?",
            "What are the requirements for a driver's license renewal?",
            "What is considered reckless driving?",
            "How many demerit points do you get for careless driving?"
        ]

        test_results = []
        for question in test_questions:
            logger.info(f"Testing: {question}")
            result = processor.run_search_test(question)
            test_results.append(result)

        # Generate report
        report = processor.generate_report({}, test_results)
        print("\n" + report)

        # Save test results
        results_file = Path("search_test_results.json")
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        logger.info(f"✓ Search test results saved to {results_file}")

    else:
        # Full processing workflow
        if not input_dir.exists():
            logger.error(f"Input directory does not exist: {input_dir}")
            return 1

        # Process documents
        results = processor.process_directory(input_dir, download_dir)

        # Run tests if requested
        test_results = None
        if args.run_tests:
            logger.info("Running search performance tests...")
            test_questions = [
                "What are the penalties for speeding in Oklahoma?",
                "What is the statute of limitations for traffic violations?",
                "What are the requirements for a driver's license renewal?",
                "What is considered reckless driving?",
                "How many demerit points do you get for careless driving?"
            ]

            test_results = []
            for question in test_questions:
                logger.info(f"Testing: {question}")
                result = processor.run_search_test(question)
                test_results.append(result)

        # Generate and display report
        report = processor.generate_report(results, test_results)
        print("\n" + report)

        # Save results
        results_file = Path("processing_results.json")
        with open(results_file, 'w') as f:
            json.dump({
                'processing_results': results,
                'test_results': test_results,
                'timestamp': time.time(),
                'input_dir': str(input_dir),
                'download_dir': str(download_dir)
            }, f, indent=2, default=str)

        logger.info(f"✓ Processing results saved to {results_file}")

    logger.info("🎉 Legal dataset processing complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())