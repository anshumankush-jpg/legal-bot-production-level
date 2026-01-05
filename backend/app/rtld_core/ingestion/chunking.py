"""Text chunking utilities for RTLD system."""

import logging
from typing import List, Dict, Any, Optional
from ..schemas import Chunk

logger = logging.getLogger(__name__)


class TextChunker:
    """Text chunking with semantic awareness."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """Initialize chunker."""
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(
        self,
        text: str,
        doc_id: str,
        source_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """Split text into overlapping chunks with metadata."""
        if not text.strip():
            return []

        metadata = metadata or {}

        # Split into paragraphs first (preserve semantic units)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        # If no paragraphs found, treat the whole text as one paragraph
        if not paragraphs:
            paragraphs = [text]

        chunks = []
        current_chunk = ""
        chunk_index = 0

        for paragraph in paragraphs:
            # Split long paragraphs into smaller chunks
            if len(paragraph) <= self.chunk_size:
                # Paragraph fits in a chunk
                if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                    # Finalize current chunk
                    chunk = self._create_chunk(
                        text=current_chunk.strip(),
                        doc_id=doc_id,
                        chunk_index=chunk_index,
                        source_name=source_name,
                        metadata=metadata
                    )
                    chunks.append(chunk)
                    chunk_index += 1

                    # Start new chunk with overlap
                    words = current_chunk.split()
                    if len(words) > 5:
                        overlap_words = min(len(words) // 4, self.overlap // 6)  # Rough word estimate
                        overlap_text = ' '.join(words[-overlap_words:]) if overlap_words > 0 else ""
                        current_chunk = overlap_text + (' ' if overlap_text else '') + paragraph
                    else:
                        current_chunk = paragraph
                else:
                    current_chunk += ('\n\n' if current_chunk else '') + paragraph
            else:
                # Long paragraph - split it
                words = paragraph.split()
                temp_chunk = current_chunk

                for i, word in enumerate(words):
                    if len(temp_chunk) + len(word) + 1 > self.chunk_size and temp_chunk:
                        # Save current chunk
                        chunk = self._create_chunk(
                            text=temp_chunk.strip(),
                            doc_id=doc_id,
                            chunk_index=chunk_index,
                            source_name=source_name,
                            metadata=metadata
                        )
                        chunks.append(chunk)
                        chunk_index += 1

                        # Start new chunk with overlap
                        chunk_words = temp_chunk.split()
                        if len(chunk_words) > 5:
                            overlap_words = min(len(chunk_words) // 4, self.overlap // 6)
                            temp_chunk = ' '.join(chunk_words[-overlap_words:]) if overlap_words > 0 else ""
                        else:
                            temp_chunk = ""
                        temp_chunk += ' ' + word
                    else:
                        temp_chunk += (' ' if temp_chunk else '') + word

                current_chunk = temp_chunk

        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk(
                text=current_chunk.strip(),
                doc_id=doc_id,
                chunk_index=chunk_index,
                source_name=source_name,
                metadata=metadata
            )
            chunks.append(chunk)

        logger.info(f"Chunked document {doc_id} into {len(chunks)} chunks")
        return chunks

    def _create_chunk(
        self,
        text: str,
        doc_id: str,
        chunk_index: int,
        source_name: str,
        metadata: Dict[str, Any]
    ) -> Chunk:
        """Create a Chunk object."""
        return Chunk(
            id=f"{doc_id}_chunk_{chunk_index}",
            content=text,
            doc_id=doc_id,
            chunk_index=chunk_index,
            metadata={
                **metadata,
                'source_name': source_name,
                'source_file': source_name,  # For backward compatibility
                'chunk_index': chunk_index
            }
        )


class DocumentChunker:
    """Chunk documents with awareness of document structure."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """Initialize document chunker."""
        self.text_chunker = TextChunker(chunk_size, overlap)

    def chunk_document(
        self,
        content: str,
        doc_id: str,
        source_name: str,
        content_type: str = "document",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """Chunk document content based on type."""
        metadata = metadata or {}
        metadata['content_type'] = content_type

        if content_type == "table":
            return self._chunk_table(content, doc_id, source_name, metadata)
        else:
            return self.text_chunker.chunk_text(content, doc_id, source_name, metadata)

    def _chunk_table(
        self,
        csv_content: str,
        doc_id: str,
        source_name: str,
        metadata: Dict[str, Any]
    ) -> List[Chunk]:
        """Chunk CSV/table content row by row."""
        lines = csv_content.strip().split('\n')
        if not lines:
            return []

        chunks = []
        for i, line in enumerate(lines[1:], 1):  # Skip header
            if line.strip():
                chunk = Chunk(
                    id=f"{doc_id}_row_{i}",
                    text=f"Row {i}: {line}",
                    doc_id=doc_id,
                    chunk_index=i,
                    source_name=source_name,
                    metadata={**metadata, 'row_number': i, 'is_table_row': True}
                )
                chunks.append(chunk)

        return chunks


def chunk_document_text(
    text: str,
    doc_id: str = "test_doc",
    source_name: str = "test_source",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    metadata: Optional[Dict[str, Any]] = None
) -> List[Chunk]:
    """Convenience function to chunk document text."""
    chunker = TextChunker(chunk_size, chunk_overlap)
    return chunker.chunk_text(text, doc_id, source_name, metadata)