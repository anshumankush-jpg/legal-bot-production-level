"""
RTLD (Real-Time Learning Database) Integration Service
Integrates the unified embedding server from artillty folder for multi-modal embeddings
"""

import os
import io
import tempfile
from typing import List, Dict, Optional, Union, Any, Tuple
from pathlib import Path
import numpy as np
import faiss
from PIL import Image
try:
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
import torch
from sentence_transformers import SentenceTransformer
import pandas as pd
from pydantic import BaseModel
import logging

# Document processing imports
try:
    import PyPDF2 as pypdf2
except ImportError:
    pypdf2 = None
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingRequest(BaseModel):
    """Request model for embedding API"""
    content: Optional[str] = None
    file_path: Optional[str] = None
    content_type: Optional[str] = None  # 'text', 'image', 'table', 'document', 'auto'
    metadata: Optional[Dict[str, Any]] = None


class EmbeddingResponse(BaseModel):
    """Response model for embedding API"""
    embeddings: List[List[float]]
    chunk_ids: List[str]
    chunk_texts: List[str]
    content_type: str
    num_chunks: int
    metadata: Optional[Dict[str, Any]] = None


class RTLDService:
    """
    RTLD (Real-Time Learning Database) service that integrates the unified embedding server.
    Handles multi-modal content: Text, Images, Tables, and Documents with automatic content extraction.
    """

    def __init__(
        self,
        text_model_name: str = "all-MiniLM-L6-v2",
        image_model_name: str = "ViT-B/32",
        device: Optional[str] = None
    ):
        """
        Initialize the RTLD service

        Args:
            text_model_name: SentenceTransformer model (default: winner from tests)
            image_model_name: CLIP model for images
            device: 'cuda' or 'cpu'
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing RTLD Service on {self.device}")

        # Initialize text embedding model (SentenceTransformer - winner from tests)
        logger.info("Loading text embedding model (SentenceTransformer)...")
        self.text_model = SentenceTransformer(text_model_name, device=self.device)
        self.text_embedding_dim = self.text_model.get_sentence_embedding_dimension()

        # Initialize image embedding model (CLIP)
        self.image_model = None
        self.image_preprocess = None
        if CLIP_AVAILABLE:
            logger.info("Loading image embedding model (CLIP)...")
            self.image_model, self.image_preprocess = clip.load(image_model_name, device=self.device)
            self.image_embedding_dim = 512  # CLIP ViT-B/32 dimension
        else:
            logger.warning("CLIP not available. Image embedding disabled.")
            self.image_embedding_dim = self.text_embedding_dim  # Fallback

        # Set unified embedding dimension (use text model dimension)
        self.embedding_dim = self.text_embedding_dim

        # Initialize FAISS index for unified storage
        self.index_path = Path(settings.FAISS_INDEX_PATH)
        self.metadata_path = Path(settings.FAISS_METADATA_PATH)

        # Metadata storage
        self.metadata_store: List[Dict] = []
        self.text_store: List[str] = []

        # Initialize or load index
        if self.index_path.exists() and self.metadata_path.exists():
            self.load_index()
        else:
            # Create new IndexFlatIP (inner product) for normalized vectors
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            logger.info(f"Created new FAISS index with dimension {self.embedding_dim}")

        logger.info("RTLD Service initialized successfully")

    def embed_text(self, texts: List[str]) -> Tuple[np.ndarray, List[str]]:
        """
        Embed text content using SentenceTransformer

        Args:
            texts: List of text strings

        Returns:
            Tuple of (embeddings array, chunk texts)
        """
        if not texts:
            return np.array([], dtype=np.float32).reshape(0, self.embedding_dim), []

        # Generate embeddings
        embeddings = self.text_model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        return np.array(embeddings, dtype=np.float32), texts

    def embed_image(self, image_path: str) -> Tuple[np.ndarray, List[str]]:
        """
        Embed image content using CLIP

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (embeddings array, descriptions)
        """
        if not CLIP_AVAILABLE or self.image_model is None:
            # Fallback: return zero embedding with description
            logger.warning("CLIP not available, using zero embedding for image")
            return np.zeros((1, self.embedding_dim), dtype=np.float32), [f"Image: {Path(image_path).name}"]

        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_input = self.image_preprocess(image).unsqueeze(0).to(self.device)

            # Generate embedding
            with torch.no_grad():
                image_features = self.image_model.encode_image(image_input)
                image_features = image_features.cpu().numpy()

            # Normalize
            norms = np.linalg.norm(image_features, axis=1, keepdims=True)
            image_features = image_features / norms

            return image_features.astype(np.float32), [f"Image: {Path(image_path).name}"]

        except Exception as e:
            logger.error(f"Error embedding image {image_path}: {e}")
            return np.zeros((1, self.embedding_dim), dtype=np.float32), [f"Image: {Path(image_path).name} (error)"]

    def extract_text_from_pdf(self, file_path: str) -> List[str]:
        """Extract text from PDF file and chunk it"""
        chunks = []

        try:
            if PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text and text.strip():
                            # Simple chunking: split by paragraphs
                            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                            chunks.extend(paragraphs)
            elif pypdf2:
                with open(file_path, 'rb') as file:
                    pdf_reader = pypdf2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text and text.strip():
                            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                            chunks.extend(paragraphs)
            else:
                logger.error("No PDF processing library available")
                return [f"PDF: {Path(file_path).name} (could not extract text)"]

        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return [f"PDF: {Path(file_path).name} (extraction error)"]

        return chunks if chunks else [f"PDF: {Path(file_path).name} (no text found)"]

    def extract_text_from_docx(self, file_path: str) -> List[str]:
        """Extract text from DOCX file and chunk it"""
        if not DOCX_AVAILABLE:
            return [f"DOCX: {Path(file_path).name} (docx library not available)"]

        chunks = []
        try:
            doc = DocxDocument(file_path)
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    chunks.append(text)
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            return [f"DOCX: {Path(file_path).name} (extraction error)"]

        return chunks if chunks else [f"DOCX: {Path(file_path).name} (no text found)"]

    def extract_text_from_excel(self, file_path: str) -> List[str]:
        """Extract text from Excel file and chunk it"""
        if not EXCEL_AVAILABLE:
            return [f"Excel: {Path(file_path).name} (openpyxl not available)"]

        chunks = []
        try:
            df = pd.read_excel(file_path)
            # Convert each row to a text representation
            for _, row in df.iterrows():
                row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                if row_text:
                    chunks.append(row_text)
        except Exception as e:
            logger.error(f"Error extracting text from Excel {file_path}: {e}")
            return [f"Excel: {Path(file_path).name} (extraction error)"]

        return chunks if chunks else [f"Excel: {Path(file_path).name} (no data found)"]

    def process_document(self, file_path: str) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Process a document file and return embeddings, chunk texts, and chunk IDs

        Args:
            file_path: Path to document file

        Returns:
            Tuple of (embeddings, chunk_texts, chunk_ids)
        """
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()

        # Extract text based on file type
        if file_ext == '.pdf':
            chunks = self.extract_text_from_pdf(str(file_path))
        elif file_ext in ['.docx', '.doc']:
            chunks = self.extract_text_from_docx(str(file_path))
        elif file_ext in ['.xlsx', '.xls']:
            chunks = self.extract_text_from_excel(str(file_path))
        elif file_ext in ['.txt', '.md']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
            except Exception as e:
                logger.error(f"Error reading text file {file_path}: {e}")
                chunks = [f"Text file: {file_path.name} (read error)"]
        else:
            # Unknown file type
            chunks = [f"Unknown file type: {file_path.name}"]

        # Generate embeddings for chunks
        if chunks:
            embeddings, _ = self.embed_text(chunks)
            chunk_ids = [f"{file_path.name}_chunk_{i}" for i in range(len(chunks))]
            return embeddings, chunks, chunk_ids
        else:
            return np.array([], dtype=np.float32).reshape(0, self.embedding_dim), [], []

    def process_table(self, file_path: str) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Process a table file (CSV) and return embeddings, texts, and IDs

        Args:
            file_path: Path to table file

        Returns:
            Tuple of (embeddings, texts, ids)
        """
        try:
            df = pd.read_csv(file_path)
            # Convert rows to text representations
            texts = []
            for _, row in df.iterrows():
                row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                texts.append(row_text)

            if texts:
                embeddings, _ = self.embed_text(texts)
                chunk_ids = [f"{Path(file_path).name}_row_{i}" for i in range(len(texts))]
                return embeddings, texts, chunk_ids
            else:
                return np.array([], dtype=np.float32).reshape(0, self.embedding_dim), [], []

        except Exception as e:
            logger.error(f"Error processing table {file_path}: {e}")
            return np.array([], dtype=np.float32).reshape(0, self.embedding_dim), [], []

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Main embedding method that handles different content types

        Args:
            request: EmbeddingRequest with content, file_path, content_type, metadata

        Returns:
            EmbeddingResponse with embeddings, chunk info, and metadata
        """
        content_type = request.content_type or 'auto'

        # Determine content type and process accordingly
        if request.file_path:
            file_path = request.file_path
            file_ext = Path(file_path).suffix.lower()

            if content_type == 'auto':
                # Auto-detect based on file extension
                if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                    content_type = 'image'
                elif file_ext == '.csv':
                    content_type = 'table'
                elif file_ext in ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls']:
                    content_type = 'document'
                else:
                    content_type = 'document'  # Default fallback

            if content_type == 'image':
                embeddings, chunk_texts = self.embed_image(file_path)
                chunk_ids = [f"{Path(file_path).name}"]
            elif content_type == 'table':
                embeddings, chunk_texts, chunk_ids = self.process_table(file_path)
            elif content_type == 'document':
                embeddings, chunk_texts, chunk_ids = self.process_document(file_path)
            else:
                # Fallback to text processing
                embeddings, chunk_texts = self.embed_text([f"File: {Path(file_path).name}"])
                chunk_ids = [f"{Path(file_path).name}"]

        elif request.content:
            # Process text content
            content_type = 'text'
            embeddings, chunk_texts = self.embed_text([request.content])
            chunk_ids = ["text_content"]

        else:
            raise ValueError("Either content or file_path must be provided")

        # Convert embeddings to list format for response
        embeddings_list = embeddings.tolist() if embeddings.size > 0 else []

        return EmbeddingResponse(
            embeddings=embeddings_list,
            chunk_ids=chunk_ids,
            chunk_texts=chunk_texts,
            content_type=content_type,
            num_chunks=len(chunk_texts),
            metadata=request.metadata
        )

    def add_to_index(self, embeddings: np.ndarray, metadatas: List[Dict], texts: List[str]) -> List[int]:
        """
        Add embeddings to the FAISS index

        Args:
            embeddings: numpy array of shape (N, D)
            metadatas: List of metadata dicts
            texts: List of text chunks

        Returns:
            List of FAISS IDs
        """
        if len(embeddings) == 0:
            return []

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)

        # Add to FAISS index
        self.index.add(embeddings)

        # Get IDs
        start_id = len(self.metadata_store)
        ids = list(range(start_id, start_id + len(embeddings)))

        # Store metadata and texts
        self.metadata_store.extend(metadatas)
        self.text_store.extend(texts)

        logger.info(f"Added {len(embeddings)} vectors to RTLD index (IDs: {ids[0]}-{ids[-1]})")
        return ids

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search the index for similar content

        Args:
            query: Search query string
            top_k: Number of results to return

        Returns:
            List of result dictionaries with similarity, metadata, and text
        """
        if self.index.ntotal == 0:
            return []

        # Embed query
        query_embedding, _ = self.embed_text([query])
        if query_embedding.size == 0:
            return []

        # Normalize query
        faiss.normalize_L2(query_embedding)

        # Search
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata_store):
                continue

            result = {
                'similarity': float(score),
                'metadata': self.metadata_store[idx],
                'text': self.text_store[idx],
                'id': idx
            }
            results.append(result)

        return results

    def save_index(self):
        """Save index and metadata to disk"""
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        logger.info(f"Saved FAISS index to {self.index_path}")

        # Save metadata as JSONL
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            for i, (meta, text) in enumerate(zip(self.metadata_store, self.text_store)):
                record = {
                    'faiss_id': i,
                    'metadata': meta,
                    'text': text
                }
                import json
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

        logger.info(f"Saved {len(self.metadata_store)} metadata records to {self.metadata_path}")

    def load_index(self):
        """Load index and metadata from disk"""
        # Load FAISS index
        self.index = faiss.read_index(str(self.index_path))
        self.embedding_dim = self.index.d
        logger.info(f"Loaded FAISS index from {self.index_path} (dim={self.embedding_dim}, size={self.index.ntotal})")

        # Load metadata
        self.metadata_store = []
        self.text_store = []

        if self.metadata_path.exists():
            import json
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                for line in f:
                    record = json.loads(line.strip())
                    self.metadata_store.append(record['metadata'])
                    self.text_store.append(record['text'])

            logger.info(f"Loaded {len(self.metadata_store)} metadata records from {self.metadata_path}")

    def get_stats(self) -> Dict:
        """Get statistics about the index"""
        return {
            'total_vectors': self.index.ntotal,
            'dimension': self.embedding_dim,
            'text_model': 'all-MiniLM-L6-v2',
            'image_support': CLIP_AVAILABLE,
            'device': self.device
        }


# Global singleton instance
_rtld_service: Optional[RTLDService] = None


def get_rtld_service() -> RTLDService:
    """Get or create the global RTLD service instance"""
    global _rtld_service
    if _rtld_service is None:
        _rtld_service = RTLDService()
    return _rtld_service