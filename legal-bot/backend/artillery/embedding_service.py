"""
Artillery Embedding Service for PLAZA-AI
Multi-modal embedding service with SentenceTransformer + CLIP integration
"""

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
import clip
from PIL import Image
from typing import List, Union, Optional
import logging

logger = logging.getLogger(__name__)


class ArtilleryEmbeddingService:
    """
    Artillery Embedding Service for PLAZA-AI.

    Features:
    - Text embeddings: SentenceTransformer (all-MiniLM-L6-v2) → 384D
    - Image embeddings: CLIP (ViT-B/32) → 512D → project to 384D
    - Unified 384D vector space for both modalities
    - L2 normalization for cosine similarity
    - Batch processing support
    """

    def __init__(self, device: str = None):
        """
        Initialize the Artillery embedding service.

        Args:
            device: 'cuda' or 'cpu' (auto-detect if None)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"🚀 Initializing Artillery Embedding Service on {self.device}")

        # Initialize text embedding model (SentenceTransformers - 384D output)
        logger.info("📝 Loading SentenceTransformer model...")
        try:
            self.text_model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
            self.text_embedding_dim = self.text_model.get_sentence_embedding_dimension()
            logger.info(f"✅ SentenceTransformer loaded: {self.text_embedding_dim}D")
        except Exception as e:
            logger.error(f"❌ Failed to load SentenceTransformer: {e}")
            raise

        # Initialize image embedding model (CLIP - 512D output, project to 384D)
        logger.info("🖼️ Loading CLIP model...")
        try:
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
            self.clip_available = True
            logger.info("✅ CLIP model loaded")
        except Exception as e:
            logger.warning(f"⚠️ CLIP model failed to load: {e}")
            self.clip_model = None
            self.clip_preprocess = None
            self.clip_available = False

        # Unified embedding dimension
        self.unified_dim = 384
        logger.info(f"🎯 Unified embedding space: {self.unified_dim}D")

    def embed_text(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Embed text using SentenceTransformer.

        Args:
            texts: Single text string or list of texts

        Returns:
            Numpy array of shape (N, 384) where N is number of texts
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.array([]).reshape(0, self.unified_dim)

        logger.debug(f"📝 Embedding {len(texts)} text chunks...")

        try:
            # Generate embeddings using SentenceTransformer
            embeddings = self.text_model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,  # L2 normalization for cosine similarity
                show_progress_bar=False,
                batch_size=32
            )

            # Ensure correct shape
            if len(embeddings.shape) == 1:
                embeddings = embeddings.reshape(1, -1)

            logger.debug(f"✅ Text embeddings generated: {embeddings.shape}")
            return embeddings

        except Exception as e:
            logger.error(f"❌ Text embedding failed: {e}")
            raise

    def embed_image(self, image: Union[Image.Image, str]) -> np.ndarray:
        """
        Embed image using CLIP and project to unified 384D space.

        Args:
            image: PIL Image object or path to image file

        Returns:
            Numpy array of shape (384,) - unified embedding space
        """
        if not self.clip_available:
            raise RuntimeError("CLIP model not available. Cannot embed images.")

        try:
            # Load image if path provided
            if isinstance(image, str):
                image = Image.open(image).convert('RGB')

            logger.debug("🖼️ Processing image for CLIP...")

            # Preprocess image for CLIP
            image_tensor = self.clip_preprocess(image).unsqueeze(0).to(self.device)

            # Generate CLIP embedding
            with torch.no_grad():
                image_features = self.clip_model.encode_image(image_tensor)

                # CLIP embeddings are already normalized internally
                # Shape: (1, 512)

                # Project to unified 384D space (take first 384 dimensions)
                if image_features.shape[-1] >= 384:
                    embedding_384d = image_features[:, :384].cpu().numpy()[0]
                else:
                    # Pad if necessary (unlikely for CLIP)
                    embedding_384d = image_features[0].cpu().numpy()
                    if len(embedding_384d) < 384:
                        padding = np.zeros(384 - len(embedding_384d))
                        embedding_384d = np.concatenate([embedding_384d, padding])

                # Ensure L2 normalization
                embedding_384d = embedding_384d / np.linalg.norm(embedding_384d)

            logger.debug(f"✅ Image embedding generated: {embedding_384d.shape}")
            return embedding_384d

        except Exception as e:
            logger.error(f"❌ Image embedding failed: {e}")
            raise

    def embed_batch(self, content_list: List[Union[str, Image.Image]], content_types: List[str]) -> np.ndarray:
        """
        Embed a batch of mixed content (text and images).

        Args:
            content_list: List of content (strings or PIL Images)
            content_types: List of content types ('text' or 'image')

        Returns:
            Numpy array of shape (N, 384) where N is number of items
        """
        if len(content_list) != len(content_types):
            raise ValueError("content_list and content_types must have same length")

        embeddings = []

        # Group by type for batch processing
        text_items = []
        image_items = []

        for content, content_type in zip(content_list, content_types):
            if content_type == 'text':
                text_items.append(content)
            elif content_type == 'image':
                image_items.append(content)
            else:
                raise ValueError(f"Unknown content type: {content_type}")

        # Process text batch
        if text_items:
            text_embeddings = self.embed_text(text_items)
            embeddings.extend(text_embeddings)

        # Process images individually (CLIP doesn't support batch well for different sizes)
        for image in image_items:
            image_embedding = self.embed_image(image)
            embeddings.append(image_embedding)

        return np.array(embeddings)

    def get_model_info(self) -> dict:
        """Get information about loaded models."""
        return {
            "text_model": {
                "name": "all-MiniLM-L6-v2",
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
        return (f"ArtilleryEmbeddingService(\n"
                f"  Text: SentenceTransformer ({info['text_model']['dimension']}D)\n"
                f"  Image: {'CLIP ' + info['clip_model']['name'] if info['clip_model']['available'] else 'Not available'}\n"
                f"  Unified: {info['unified_dimension']}D\n"
                f"  Device: {info['device']}\n"
                f")")


# Global service instance (lazy loading)
_service_instance = None

def get_artillery_embedding_service(device: Optional[str] = None) -> ArtilleryEmbeddingService:
    """Get or create global Artillery embedding service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ArtilleryEmbeddingService(device=device)
    return _service_instance