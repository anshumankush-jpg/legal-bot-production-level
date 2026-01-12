"""
Multi-Modal Embedding Service for PLAZA-AI
Handles text (SentenceTransformers) and image (CLIP) embeddings in unified 384D space
"""

import numpy as np
import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
import clip
from PIL import Image
from typing import List, Union, Optional, Tuple
import logging
import os

logger = logging.getLogger(__name__)


class EmbeddingProjector(nn.Module):
    """Projects 512D CLIP embeddings to 384D unified space."""

    def __init__(self, input_dim: int = 512, output_dim: int = 384):
        super().__init__()
        self.projection = nn.Linear(input_dim, output_dim, bias=False)
        # Initialize with identity-like transformation for better preservation
        nn.init.orthogonal_(self.projection.weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Project embeddings to unified space and normalize."""
        projected = self.projection(x)
        # L2 normalize for cosine similarity
        return torch.nn.functional.normalize(projected, p=2, dim=-1)

    def project_numpy(self, embedding: np.ndarray) -> np.ndarray:
        """Project single numpy embedding."""
        with torch.no_grad():
            x = torch.tensor(embedding, dtype=torch.float32)
            projected = self.forward(x)
            return projected.numpy()


class MultiModalEmbeddingService:
    """
    Multi-modal embedding service for PLAZA-AI.

    Features:
    - Text embeddings: SentenceTransformers (all-MiniLM-L6-v2) → 384D
    - Image embeddings: CLIP (ViT-B/32) → 512D → projected to 384D
    - Unified 384D vector space for both modalities
    - L2 normalization for cosine similarity
    """

    def __init__(
        self,
        text_model_name: str = "all-MiniLM-L6-v2",
        clip_model_name: str = "ViT-B/32",
        device: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize the multi-modal embedding service.

        Args:
            text_model_name: SentenceTransformer model name
            clip_model_name: CLIP model name
            device: 'cuda' or 'cpu' (auto-detect if None)
            cache_dir: Directory to cache models
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.cache_dir = cache_dir

        logger.info(f"🚀 Initializing Multi-Modal Embedding Service on {self.device}")

        # Initialize text embedding model (SentenceTransformers)
        logger.info("📝 Loading SentenceTransformer model...")
        self.text_model = SentenceTransformer(
            text_model_name,
            device=self.device,
            cache_folder=self.cache_dir
        )
        self.text_embedding_dim = self.text_model.get_sentence_embedding_dimension()
        logger.info(f"✅ Text model loaded: {text_model_name} ({self.text_embedding_dim}D)")

        # Initialize image embedding model (CLIP)
        logger.info("🖼️ Loading CLIP model...")
        try:
            self.clip_model, self.clip_preprocess = clip.load(
                clip_model_name,
                device=self.device,
                download_root=self.cache_dir
            )
            self.clip_available = True
            logger.info(f"✅ CLIP model loaded: {clip_model_name}")
        except Exception as e:
            logger.warning(f"❌ CLIP model failed to load: {e}")
            self.clip_model = None
            self.clip_preprocess = None
            self.clip_available = False

        # Initialize projection layer (512D → 384D for CLIP embeddings)
        if self.clip_available:
            self.projection_layer = EmbeddingProjector(input_dim=512, output_dim=384)
            self.projection_layer.eval()
            logger.info("✅ Projection layer initialized (512D → 384D)")
        else:
            self.projection_layer = None

        # Unified embedding dimension
        self.unified_dim = 384
        logger.info(f"🎯 Unified embedding space: {self.unified_dim}D")

    def embed_text(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Embed text using SentenceTransformer.

        Args:
            texts: Single text string or list of texts
            normalize: Whether to L2 normalize embeddings
            batch_size: Batch size for processing

        Returns:
            Numpy array of shape (N, 384) where N is number of texts
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.array([]).reshape(0, self.unified_dim)

        logger.debug(f"📝 Embedding {len(texts)} text chunks...")

        # Generate embeddings using SentenceTransformer
        embeddings = self.text_model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
            show_progress_bar=False,
            batch_size=batch_size
        )

        # Ensure correct shape
        if len(embeddings.shape) == 1:
            embeddings = embeddings.reshape(1, -1)

        logger.debug(f"✅ Text embeddings generated: {embeddings.shape}")
        return embeddings

    def embed_image(
        self,
        image: Union[str, Image.Image],
        normalize: bool = True
    ) -> np.ndarray:
        """
        Embed image using CLIP and project to unified space.

        Args:
            image: Image file path or PIL Image object
            normalize: Whether to L2 normalize final embedding

        Returns:
            Numpy array of shape (384,) - unified embedding space
        """
        if not self.clip_available:
            raise RuntimeError("CLIP model not available. Cannot embed images.")

        # Load image if path provided
        if isinstance(image, str):
            try:
                image = Image.open(image).convert('RGB')
            except Exception as e:
                raise ValueError(f"Failed to load image from path {image}: {e}")

        logger.debug("🖼️ Processing image for CLIP...")

        # Preprocess image for CLIP
        image_tensor = self.clip_preprocess(image).unsqueeze(0).to(self.device)

        # Generate CLIP embedding
        with torch.no_grad():
            image_features = self.clip_model.encode_image(image_tensor)

            # CLIP embeddings are already normalized internally
            # Shape: (1, 512)

            # Project to unified 384D space
            if self.projection_layer is not None:
                image_features_384d = self.projection_layer(image_features)
            else:
                # Fallback: take first 384 dimensions
                image_features_384d = image_features[:, :384]

            # Convert to numpy
            embedding = image_features_384d.cpu().numpy()[0]

            # Final normalization if requested
            if normalize:
                embedding = embedding / np.linalg.norm(embedding)

        logger.debug(f"✅ Image embedding generated: {embedding.shape}")
        return embedding

    def embed_table(
        self,
        table_data,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Embed table data by converting to text description.

        Args:
            table_data: Pandas DataFrame or similar tabular data
            normalize: Whether to normalize embedding

        Returns:
            Numpy array of shape (384,) - unified embedding space
        """
        try:
            import pandas as pd
            if not isinstance(table_data, pd.DataFrame):
                table_data = pd.DataFrame(table_data)
        except ImportError:
            # Convert to list of lists if pandas not available
            if hasattr(table_data, 'values'):
                table_data = table_data.values.tolist()
            elif not isinstance(table_data, list):
                table_data = [list(table_data)]

        # Convert table to text descriptions
        text_descriptions = []

        # Add summary
        num_rows, num_cols = len(table_data), len(table_data[0]) if table_data else 0
        summary = f"Table with {num_rows} rows and {num_cols} columns"
        text_descriptions.append(summary)

        # Add row descriptions (limit to first 10 rows for performance)
        for i, row in enumerate(table_data[:10]):
            if hasattr(row, 'values'):
                row_values = row.values
            else:
                row_values = list(row)

            # Convert row to text
            row_text = f"Row {i}: " + ", ".join([f"col_{j}={val}" for j, val in enumerate(row_values)])
            text_descriptions.append(row_text)

        # Combine all text and embed
        combined_text = " | ".join(text_descriptions)
        return self.embed_text(combined_text, normalize=normalize)

    def embed_document(
        self,
        content: str,
        content_type: str = "text",
        normalize: bool = True
    ) -> np.ndarray:
        """
        Embed document content based on type.

        Args:
            content: Document content (text, image path, etc.)
            content_type: Type of content ('text', 'image', 'table')
            normalize: Whether to normalize embedding

        Returns:
            Numpy array in unified embedding space
        """
        if content_type == "text":
            return self.embed_text(content, normalize=normalize)
        elif content_type == "image":
            return self.embed_image(content, normalize=normalize)
        elif content_type == "table":
            return self.embed_table(content, normalize=normalize)
        else:
            # Default to text embedding
            logger.warning(f"Unknown content type '{content_type}', treating as text")
            return self.embed_text(str(content), normalize=normalize)

    def get_model_info(self) -> dict:
        """Get information about loaded models."""
        return {
            "text_model": {
                "name": self.text_model.get_sentence_embedding_dimension() and "all-MiniLM-L6-v2",
                "dimension": self.text_embedding_dim,
                "device": self.device
            },
            "clip_model": {
                "available": self.clip_available,
                "name": "ViT-B/32" if self.clip_available else None,
                "native_dimension": 512,
                "projected_dimension": 384,
                "device": self.device
            },
            "unified_dimension": self.unified_dim,
            "device": self.device
        }

    def __str__(self) -> str:
        """String representation of the service."""
        info = self.get_model_info()
        return (f"MultiModalEmbeddingService(\n"
                f"  Text: {info['text_model']['name']} ({info['text_model']['dimension']}D)\n"
                f"  Image: {'CLIP ' + info['clip_model']['name'] if info['clip_model']['available'] else 'Not available'}\n"
                f"  Unified: {info['unified_dimension']}D\n"
                f"  Device: {info['device']}\n"
                f")")


# Global service instance (lazy loading)
_service_instance = None

def get_embedding_service(
    text_model_name: str = "all-MiniLM-L6-v2",
    clip_model_name: str = "ViT-B/32",
    device: Optional[str] = None
) -> MultiModalEmbeddingService:
    """Get or create global embedding service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = MultiModalEmbeddingService(
            text_model_name=text_model_name,
            clip_model_name=clip_model_name,
            device=device
        )
    return _service_instance