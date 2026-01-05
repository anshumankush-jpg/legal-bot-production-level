"""Convert HTML files to PDF for better processing."""
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def convert_html_to_pdf(html_path: Path, output_dir: Path = None):
    """
    Convert HTML file to PDF.
    
    Args:
        html_path: Path to HTML file
        output_dir: Directory to save PDF (default: same as HTML file)
    
    Returns:
        Path to created PDF file, or None if failed
    """
    if output_dir is None:
        output_dir = html_path.parent
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = output_dir / f"{html_path.stem}.pdf"
    
    # Method 1: Try weasyprint (best for HTML to PDF)
    try:
        from weasyprint import HTML
        logger.info(f"Converting {html_path.name} to PDF using weasyprint...")
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        logger.info(f"✅ Created: {pdf_path}")
        return pdf_path
    except ImportError:
        logger.debug("weasyprint not available, trying pdfkit")
    except Exception as e:
        logger.warning(f"weasyprint failed: {e}, trying pdfkit")
    
    # Method 2: Try pdfkit (requires wkhtmltopdf)
    try:
        import pdfkit
        logger.info(f"Converting {html_path.name} to PDF using pdfkit...")
        pdfkit.from_file(str(html_path), str(pdf_path))
        logger.info(f"✅ Created: {pdf_path}")
        return pdf_path
    except ImportError:
        logger.debug("pdfkit not available, trying playwright")
    except Exception as e:
        logger.warning(f"pdfkit failed: {e}, trying playwright")
    
    # Method 3: Try playwright (modern, reliable)
    try:
        from playwright.sync_api import sync_playwright
        logger.info(f"Converting {html_path.name} to PDF using playwright...")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(f"file://{html_path.absolute()}")
            page.pdf(path=str(pdf_path))
            browser.close()
        logger.info(f"✅ Created: {pdf_path}")
        return pdf_path
    except ImportError:
        logger.warning("playwright not available")
    except Exception as e:
        logger.error(f"playwright failed: {e}")
    
    logger.error(f"❌ Failed to convert {html_path.name} - no PDF converter available")
    logger.info("\nTo enable HTML to PDF conversion, install one of:")
    logger.info("  pip install weasyprint")
    logger.info("  pip install pdfkit  # (also requires wkhtmltopdf binary)")
    logger.info("  pip install playwright  # (then run: playwright install chromium)")
    
    return None

def find_html_files(base_path: Path):
    """Find all HTML files in directory."""
    html_files = []
    for ext in ['*.html', '*.htm']:
        html_files.extend(base_path.rglob(ext))
    return html_files

def main():
    """Convert all HTML files to PDF."""
    base_path = Path(__file__).parent.parent.parent
    
    # Directories to convert
    html_dirs = [
        base_path / "us_state_codes",
        base_path / "canada_traffic_acts",
        base_path / "canada criminal and federal law",
    ]
    
    print("=" * 60)
    print("HTML to PDF Converter")
    print("=" * 60)
    print()
    
    # Check for PDF converter
    has_converter = False
    try:
        from weasyprint import HTML
        has_converter = True
        print("✅ weasyprint available")
    except:
        try:
            import pdfkit
            has_converter = True
            print("✅ pdfkit available")
        except:
            try:
                from playwright.sync_api import sync_playwright
                has_converter = True
                print("✅ playwright available")
            except:
                print("❌ No PDF converter available")
                print()
                print("Installing weasyprint (recommended)...")
                import subprocess
                subprocess.run([sys.executable, "-m", "pip", "install", "weasyprint"], check=False)
                print()
                print("Please restart and run again.")
                return
    
    print()
    print("Finding HTML files...")
    
    all_html_files = []
    for html_dir in html_dirs:
        if html_dir.exists():
            files = find_html_files(html_dir)
            all_html_files.extend(files)
            print(f"  Found {len(files)} HTML files in {html_dir.name}")
        else:
            print(f"  ⚠️  Directory not found: {html_dir.name}")
    
    print(f"\nTotal HTML files: {len(all_html_files)}")
    print()
    
    if not all_html_files:
        print("No HTML files found to convert.")
        return
    
    # Create output directory
    pdf_output_dir = base_path / "converted_pdfs"
    pdf_output_dir.mkdir(exist_ok=True)
    print(f"PDFs will be saved to: {pdf_output_dir}")
    print()
    
    # Convert files
    converted = 0
    failed = 0
    
    for html_file in all_html_files:
        print(f"Converting: {html_file.name}...")
        pdf_path = convert_html_to_pdf(html_file, pdf_output_dir)
        if pdf_path:
            converted += 1
        else:
            failed += 1
        print()
    
    print("=" * 60)
    print("Conversion Summary")
    print("=" * 60)
    print(f"✅ Converted: {converted}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Output: {pdf_output_dir}")
    print()
    print("Note: You can now ingest the PDFs instead of HTML files")
    print("      for potentially better extraction quality.")

if __name__ == "__main__":
    main()

