"""
Comprehensive Search Benchmark: HTML vs PDF Performance Comparison

This script:
1. Extracts PDF links from HTML index files
2. Downloads and processes PDFs
3. Compares search performance between HTML and PDF sources
4. Benchmarks retrieval speed and accuracy
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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8000"


class SearchBenchmark:
    """Comprehensive search benchmark for HTML vs PDF comparison."""

    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.downloaded_pdfs = set()
        self.test_results = []

    def check_backend_health(self) -> bool:
        """Check if backend is running."""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                logger.info(f"✓ Backend running - Index size: {health.get('index_size', 0)} documents")
                return True
            return False
        except Exception as e:
            logger.error(f"✗ Backend not accessible: {e}")
            return False

    def extract_pdf_links_from_html(self, html_file: Path) -> List[Dict[str, str]]:
        """Extract PDF links from HTML index files."""
        pdf_links = []

        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()

            # Parse HTML to find PDF links
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
                        # Try to reconstruct base URL from filename
                        base_url = self._guess_base_url_from_filename(html_file.name)
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
                        'link_text': link.get_text().strip()
                    })

        except Exception as e:
            logger.error(f"Error extracting PDF links from {html_file}: {e}")

        return pdf_links

    def _guess_base_url_from_filename(self, filename: str) -> Optional[str]:
        """Guess base URL from HTML filename."""
        # Common OSCN (Oklahoma State Courts Network) pattern
        if 'oklahoma' in filename.lower():
            return "https://www.oscn.net/"
        # Add more patterns as needed
        return None

    def download_pdf(self, pdf_info: Dict[str, str], download_dir: Path) -> Optional[Path]:
        """Download a PDF file."""
        url = pdf_info['url']
        title = pdf_info['title']

        # Create safe filename
        safe_title = re.sub(r'[^\w\-_\.]', '_', title)[:100]
        filename = f"{safe_title}_{hashlib.md5(url.encode()).hexdigest()[:8]}.pdf"
        pdf_path = download_dir / filename

        # Skip if already downloaded
        if pdf_path.exists():
            logger.info(f"✓ PDF already exists: {filename}")
            return pdf_path

        try:
            logger.info(f"Downloading: {title}")
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"✓ Downloaded: {filename} ({len(response.content)} bytes)")
            return pdf_path

        except Exception as e:
            logger.error(f"✗ Failed to download {url}: {e}")
            return None

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using multiple methods."""
        text = ""

        # Method 1: pdfplumber (best for text-based PDFs)
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    # Extract tables too
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            if row:
                                text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
            if text.strip():
                return text
        except Exception as e:
            logger.warning(f"pdfplumber failed for {pdf_path.name}: {e}")

        # Method 2: PyPDF2
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text
        except Exception as e:
            logger.warning(f"PyPDF2 failed for {pdf_path.name}: {e}")

        # Method 3: pypdf
        try:
            import pypdf
            with open(pdf_path, 'rb') as f:
                pdf_reader = pypdf.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                return text
        except Exception as e:
            logger.warning(f"pypdf failed for {pdf_path.name}: {e}")

        return text

    def index_document(self, file_path: Path, source_info: Dict = None) -> bool:
        """Index a document via the API."""
        try:
            file_ext = file_path.suffix.lower()

            if file_ext == '.pdf':
                text = self.extract_text_from_pdf(file_path)
                source_type = 'pdf'
            elif file_ext in ['.html', '.htm']:
                text = self.extract_text_from_html(file_path)
                source_type = 'html'
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return False

            if not text.strip() or len(text.strip()) < 100:
                logger.warning(f"Skipping {file_path.name}: insufficient text")
                return False

            # Prepare metadata
            metadata = {
                "original_filename": str(file_path),
                "file_type": file_ext[1:],
                "indexed_at": time.time()
            }

            if source_info:
                metadata.update(source_info)

            # Extract organization from path
            organization = self._extract_organization_from_path(file_path)

            params = {}
            if organization:
                params['organization'] = organization

            # Index via API
            response = requests.post(
                f"{self.api_url}/api/ingest/text",
                json={
                    "text": text,
                    "source_name": file_path.name,
                    "tags": [source_type, file_ext[1:]],
                    "metadata": metadata
                },
                params=params,
                timeout=300
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✓ Indexed {file_path.name} - {result.get('chunks', 0)} chunks")
                return True
            else:
                logger.error(f"✗ Failed to index {file_path.name}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"✗ Error indexing {file_path.name}: {e}")
            return False

    def extract_text_from_html(self, html_path: Path) -> str:
        """Extract text from HTML file."""
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove scripts, styles, and navigation
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return '\n'.join(chunk for chunk in chunks if chunk)

        except Exception as e:
            logger.error(f"Error reading HTML {html_path}: {e}")
            return ""

    def _extract_organization_from_path(self, file_path: Path) -> Optional[str]:
        """Extract organization/state from file path."""
        path_str = str(file_path).lower()

        states = {
            'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut',
            'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa',
            'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan',
            'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new_hampshire',
            'new_jersey', 'new_mexico', 'new_york', 'north_carolina', 'north_dakota', 'ohio',
            'oklahoma', 'oregon', 'pennsylvania', 'rhode_island', 'south_carolina', 'south_dakota',
            'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west_virginia',
            'wisconsin', 'wyoming', 'canada', 'ontario', 'british_columbia', 'quebec'
        }

        for state in states:
            if state in path_str:
                return state.title().replace('_', ' ')

        return None

    def run_search_test(self, question: str) -> Dict:
        """Run a search test and return detailed results."""
        start_time = time.time()

        try:
            response = requests.post(
                f"{self.api_url}/api/query/answer",
                json={"question": question},
                timeout=60
            )

            end_time = time.time()
            response_time = end_time - start_time

            if response.status_code == 200:
                data = response.json()

                # Analyze sources
                sources = data.get('sources', [])
                pdf_sources = [s for s in sources if '.pdf' in s.get('source_name', '').lower()]
                html_sources = [s for s in sources if any(ext in s.get('source_name', '').lower()
                                                        for ext in ['.html', '.htm'])]

                return {
                    'question': question,
                    'success': True,
                    'response_time': response_time,
                    'answer': data.get('answer', ''),
                    'total_sources': len(sources),
                    'pdf_sources': len(pdf_sources),
                    'html_sources': len(html_sources),
                    'answer_length': len(data.get('answer', '')),
                    'sources': sources[:5]  # First 5 sources
                }
            else:
                return {
                    'question': question,
                    'success': False,
                    'response_time': response_time,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {
                'question': question,
                'success': False,
                'response_time': time.time() - start_time,
                'error': str(e)
            }

    def process_html_index_files(self, html_dir: Path, pdf_download_dir: Path) -> Dict:
        """Process HTML index files to extract and download PDFs."""
        results = {
            'html_files_processed': 0,
            'pdf_links_found': 0,
            'pdfs_downloaded': 0,
            'pdfs_indexed': 0,
            'errors': []
        }

        html_files = list(html_dir.glob("*.html")) + list(html_dir.glob("*.htm"))

        for html_file in html_files:
            logger.info(f"Processing HTML index: {html_file.name}")
            results['html_files_processed'] += 1

            try:
                pdf_links = self.extract_pdf_links_from_html(html_file)

                if pdf_links:
                    logger.info(f"Found {len(pdf_links)} PDF links in {html_file.name}")
                    results['pdf_links_found'] += len(pdf_links)

                    # Download PDFs concurrently
                    with ThreadPoolExecutor(max_workers=3) as executor:
                        future_to_pdf = {
                            executor.submit(self.download_pdf, pdf_info, pdf_download_dir): pdf_info
                            for pdf_info in pdf_links
                        }

                        for future in as_completed(future_to_pdf):
                            pdf_info = future_to_pdf[future]
                            try:
                                pdf_path = future.result()
                                if pdf_path:
                                    results['pdfs_downloaded'] += 1

                                    # Index the downloaded PDF
                                    if self.index_document(pdf_path, {
                                        'source_html': pdf_info['source_html'],
                                        'original_url': pdf_info['url'],
                                        'title': pdf_info['title']
                                    }):
                                        results['pdfs_indexed'] += 1

                            except Exception as e:
                                results['errors'].append(f"Error processing {pdf_info['url']}: {e}")

                # Also index the HTML file itself
                self.index_document(html_file)

            except Exception as e:
                results['errors'].append(f"Error processing {html_file}: {e}")

        return results

    def run_performance_benchmark(self, test_questions: List[str], runs_per_question: int = 3) -> Dict:
        """Run comprehensive performance benchmark."""
        logger.info("=" * 60)
        logger.info("Running Search Performance Benchmark")
        logger.info("=" * 60)

        results = {
            'test_questions': test_questions,
            'runs_per_question': runs_per_question,
            'individual_results': [],
            'summary': {}
        }

        for question in test_questions:
            logger.info(f"\nTesting: {question}")
            question_results = []

            for run in range(runs_per_question):
                logger.info(f"  Run {run + 1}/{runs_per_question}...")
                result = self.run_search_test(question)
                question_results.append(result)

                status = "✓" if result['success'] else "✗"
                response_time = result.get('response_time', 0)
                sources = result.get('total_sources', 0)
                logger.info(f"    {status} {response_time:.2f}s - {sources} sources")

            # Calculate averages for this question
            successful_runs = [r for r in question_results if r['success']]
            if successful_runs:
                avg_response_time = sum(r['response_time'] for r in successful_runs) / len(successful_runs)
                avg_sources = sum(r.get('total_sources', 0) for r in successful_runs) / len(successful_runs)
                avg_pdf_sources = sum(r.get('pdf_sources', 0) for r in successful_runs) / len(successful_runs)
                avg_html_sources = sum(r.get('html_sources', 0) for r in successful_runs) / len(successful_runs)

                question_summary = {
                    'question': question,
                    'success_rate': len(successful_runs) / runs_per_question,
                    'avg_response_time': avg_response_time,
                    'avg_total_sources': avg_sources,
                    'avg_pdf_sources': avg_pdf_sources,
                    'avg_html_sources': avg_html_sources,
                    'runs': question_results
                }
            else:
                question_summary = {
                    'question': question,
                    'success_rate': 0,
                    'error': 'All runs failed',
                    'runs': question_results
                }

            results['individual_results'].append(question_summary)

        # Calculate overall summary
        all_successful_runs = [r for qr in results['individual_results']
                              for r in qr.get('runs', []) if r.get('success', False)]

        if all_successful_runs:
            results['summary'] = {
                'total_runs': len(test_questions) * runs_per_question,
                'successful_runs': len(all_successful_runs),
                'success_rate': len(all_successful_runs) / (len(test_questions) * runs_per_question),
                'avg_response_time': sum(r['response_time'] for r in all_successful_runs) / len(all_successful_runs),
                'avg_sources_per_query': sum(r.get('total_sources', 0) for r in all_successful_runs) / len(all_successful_runs),
                'avg_pdf_sources': sum(r.get('pdf_sources', 0) for r in all_successful_runs) / len(all_successful_runs),
                'avg_html_sources': sum(r.get('html_sources', 0) for r in all_successful_runs) / len(all_successful_runs)
            }

        return results

    def print_benchmark_report(self, results: Dict):
        """Print detailed benchmark report."""
        print("\n" + "=" * 80)
        print("SEARCH PERFORMANCE BENCHMARK REPORT")
        print("=" * 80)

        if 'summary' in results and results['summary']:
            summary = results['summary']
            print("\nOVERALL SUMMARY:")
            print(f"  Total Runs: {summary['total_runs']}")
            print(f"  Success Rate: {summary['success_rate']:.1%}")
            print(f"  Avg Response Time: {summary['avg_response_time']:.2f}s")
            print(f"  Avg Sources per Query: {summary['avg_sources_per_query']:.1f}")
            print(f"  Avg PDF Sources: {summary['avg_pdf_sources']:.1f}")
            print(f"  Avg HTML Sources: {summary['avg_html_sources']:.1f}")

            # Performance analysis
            pdf_percentage = summary['avg_pdf_sources'] / summary['avg_sources_per_query'] * 100 if summary['avg_sources_per_query'] > 0 else 0
            html_percentage = summary['avg_html_sources'] / summary['avg_sources_per_query'] * 100 if summary['avg_sources_per_query'] > 0 else 0

            print("\nSOURCE ANALYSIS:")
            print(f"  PDF Sources: {pdf_percentage:.1f}% of total sources")
            print(f"  HTML Sources: {html_percentage:.1f}% of total sources")

            if pdf_percentage > html_percentage:
                print("  → PDFs are providing more relevant results")
            elif html_percentage > pdf_percentage:
                print("  → HTML files are providing more relevant results")
            else:
                print("  → PDF and HTML sources are equally relevant")

        print("\nDETAILED RESULTS BY QUESTION:")
        for i, qr in enumerate(results['individual_results'], 1):
            print(f"\n{i}. {qr['question']}")
            print(".1f")
            if 'avg_response_time' in qr:
                print(".2f")
                print(".1f")
                print(".1f")
        print("\n" + "=" * 80)


def main():
    """Main function to run comprehensive benchmark."""
    benchmark = SearchBenchmark()

    print("=" * 80)
    print("COMPREHENSIVE SEARCH BENCHMARK: HTML vs PDF")
    print("=" * 80)

    # Check backend
    if not benchmark.check_backend_health():
        print("\n❌ Backend not running. Please start it first:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return

    # Define test questions focused on legal content
    test_questions = [
        "What are the penalties for speeding in Oklahoma?",
        "What is the statute of limitations for traffic violations?",
        "How many demerit points do you get for careless driving?",
        "What are the requirements for a driver's license renewal?",
        "What is considered reckless driving?",
        "What are the fines for running a red light?",
        "How long does a traffic ticket stay on your record?",
        "What are the penalties for DUI in different states?"
    ]

    # Create download directory for PDFs
    pdf_download_dir = Path(__file__).parent.parent.parent / "data" / "downloaded_pdfs"
    pdf_download_dir.mkdir(parents=True, exist_ok=True)

    # Process HTML index files to extract and download PDFs
    print("\n1. Processing HTML Index Files...")
    usa_dir = Path(__file__).parent.parent.parent / "USA"

    if usa_dir.exists():
        processing_results = benchmark.process_html_index_files(usa_dir, pdf_download_dir)
        print("\nHTML Processing Results:")
        print(f"  HTML files processed: {processing_results['html_files_processed']}")
        print(f"  PDF links found: {processing_results['pdf_links_found']}")
        print(f"  PDFs downloaded: {processing_results['pdfs_downloaded']}")
        print(f"  PDFs indexed: {processing_results['pdfs_indexed']}")
        if processing_results['errors']:
            print(f"  Errors: {len(processing_results['errors'])}")

    # Run performance benchmark
    print("\n2. Running Search Performance Benchmark...")
    benchmark_results = benchmark.run_performance_benchmark(test_questions, runs_per_question=2)

    # Print report
    benchmark.print_benchmark_report(benchmark_results)

    # Save results to file
    results_file = Path(__file__).parent / "benchmark_results.json"
    with open(results_file, 'w') as f:
        json.dump(benchmark_results, f, indent=2, default=str)

    print(f"\n✓ Results saved to: {results_file}")
    print("\nBenchmark complete!")


if __name__ == "__main__":
    main()