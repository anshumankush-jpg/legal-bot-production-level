"""Endpoints for ingesting documents."""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pathlib import Path
import tempfile
import shutil
from typing import Optional

from app.models.schemas import (
    IngestTextRequest,
    IngestTextResponse,
    IngestFileResponse,
    IngestImageResponse
)
from app.rag.rag_service import get_rag_service
from app.ocr.ocr_service import get_ocr_service
from app.services.matter_service import get_matter_service
from app.services.workflow_service import get_workflow_service, WorkflowEvent
from app.services.document_service import get_document_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("/text", response_model=IngestTextResponse)
async def ingest_text(
    request: IngestTextRequest,
    organization: Optional[str] = Query(None, description="Organization name"),
    subject: Optional[str] = Query(None, description="Document subject")
):
    """
    Ingest plain text into the vector store with parent-child chunking.
    
    Body:
    - text: Text content
    - source_name: Identifier for the source
    - tags: Optional tags
    - metadata: Optional additional metadata
    
    Query params:
    - organization: Optional organization name
    - subject: Optional document subject
    """
    try:
        rag_service = get_rag_service()
        result = rag_service.ingest_text(
            text=request.text,
            source_name=request.source_name,
            source_type="text",
            tags=request.tags,
            metadata=request.metadata,
            organization=organization,
            subject=subject
        )
        return IngestTextResponse(**result)
    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file", response_model=IngestFileResponse)
async def ingest_file(
    file: UploadFile = File(...),
    organization: Optional[str] = Query(None, description="Organization name"),
    subject: Optional[str] = Query(None, description="Document subject")
):
    """
    Ingest a file (PDF, .txt, or .html) into the vector store.
    
    Supports:
    - PDF files (extracted as text)
    - Text files (.txt)
    - HTML files (extracted as text)
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_ext = Path(file.filename).suffix.lower()
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        # Check if RTLD is available and use it for multi-modal processing
        from app.core.config import settings
        if settings.EMBEDDING_PROVIDER == "rtld":
            # Use RTLD for direct file processing
            rag_service = get_rag_service()
            result = rag_service.ingest_file_rtld(
                file_path=tmp_path,
                source_name=file.filename,
                content_type="document",  # RTLD will auto-detect
                tags=[],
                metadata={'original_filename': file.filename, 'organization': organization, 'subject': subject}
            )
        else:
            # Legacy processing: extract text first, then ingest
            # Extract text based on file type
            if file_ext == '.pdf':
                text = _extract_text_from_pdf(tmp_path)
            elif file_ext == '.txt':
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            elif file_ext in ['.html', '.htm']:
                text = _extract_text_from_html(tmp_path)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file_ext}. Supported: .pdf, .txt, .html"
                )

            if not text.strip():
                raise HTTPException(status_code=400, detail="File appears to be empty or unreadable")

            # Ingest the text
            rag_service = get_rag_service()
            result = rag_service.ingest_text(
                text=text,
                source_name=file.filename,
                source_type="pdf" if file_ext == '.pdf' else ("html" if file_ext in ['.html', '.htm'] else "text"),
                tags=[],
                metadata={'original_filename': file.filename},
                organization=organization,
                subject=subject
            )

        # Register document
        document_service = get_document_service()
        document_service.register_document(
            doc_id=result['doc_id'],
            source_name=file.filename,
            source_type="pdf" if file_ext == '.pdf' else ("html" if file_ext in ['.html', '.htm'] else "text"),
            organization=organization,
            subject=subject,
            tags=[],
            metadata={'original_filename': file.filename}
        )
        document_service.update_document(result['doc_id'], chunk_count=result.get('chunks', 0))
        
        return IngestFileResponse(
            doc_id=result['doc_id'],
            chunks=result['chunks'],
            source_name=result['source_name'],
            file_type=file_ext
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/image", response_model=IngestImageResponse)
async def ingest_image(file: UploadFile = File(...)):
    """
    Ingest an image (ticket, summons, etc.) using OCR.
    
    Supports:
    - JPG/JPEG
    - PNG
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in ['.jpg', '.jpeg', '.png']:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type: {file_ext}. Supported: .jpg, .jpeg, .png"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        # Check if RTLD is available for direct image processing
        from app.core.config import settings
        if settings.EMBEDDING_PROVIDER == "rtld":
            # Use RTLD for direct image processing
            rag_service = get_rag_service()
            result = rag_service.ingest_file_rtld(
                file_path=tmp_path,
                source_name=file.filename,
                content_type="image",
                tags=['image', 'ticket'],
                metadata={'original_filename': file.filename, 'processed_by': 'rtld'}
            )
        else:
            # Legacy OCR processing
            # Extract text using OCR
            ocr_service = get_ocr_service()
            text = ocr_service.extract_text_from_image(tmp_path)

            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract text from image. Image may be unreadable or contain no text."
                )

            # Ingest the extracted text
            rag_service = get_rag_service()
            result = rag_service.ingest_text(
                text=text,
                source_name=file.filename,
                source_type="image_ticket",
                tags=['ocr', 'ticket'],
                metadata={'original_filename': file.filename, 'ocr_engine': ocr_service.engine}
            )
        
        return IngestImageResponse(
            doc_id=result['doc_id'],
            chunks=result['chunks'],
            source_name=result['source_name'],
            extracted_text_preview=text[:200] + '...' if len(text) > 200 else text
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)


def _extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF file with multiple fallback methods.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text
    """
    text_parts = []
    
    # Method 1: Try pdfplumber (best for text-based PDFs, handles tables well)
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                # Also extract tables if present
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            if row:
                                table_row = " | ".join(str(cell) if cell else "" for cell in row)
                                text_parts.append(table_row)
        if text_parts:
            return '\n'.join(text_parts)
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}, trying PyPDF2")
    
    # Method 2: Try PyPDF2 (fallback)
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        if text_parts:
            return '\n'.join(text_parts)
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"PyPDF2 extraction failed: {e}, trying pypdf")
    
    # Method 3: Try pypdf (newer alternative)
    try:
        import pypdf
        with open(pdf_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        if text_parts:
            return '\n'.join(text_parts)
    except ImportError:
        pass
    except Exception as e:
        logger.warning(f"pypdf extraction failed: {e}")
    
    # If all methods failed, raise error
    if not text_parts:
        raise HTTPException(
            status_code=500,
            detail="Failed to extract text from PDF. PDF may be image-based (scanned) or corrupted. Install PDF libraries: pip install pdfplumber PyPDF2 pypdf"
        )
    
    return '\n'.join(text_parts)


def _extract_text_from_html(html_path: str) -> str:
    """
    Extract text from HTML file.
    
    Args:
        html_path: Path to HTML file
        
    Returns:
        Extracted text
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        # Fallback to html.parser if BeautifulSoup not available
        import html.parser
        import html
        
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        # Simple HTML tag removal using html.parser
        class HTMLTextExtractor(html.parser.HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
            
            def handle_data(self, data):
                self.text.append(data.strip())
            
            def get_text(self):
                return ' '.join(self.text)
        
        parser = HTMLTextExtractor()
        parser.feed(html_content)
        return parser.get_text()
    else:
        # Use BeautifulSoup (preferred)
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text

