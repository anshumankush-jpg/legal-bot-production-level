"""
Embedding models for RTLD core - extracted from artillty/unified_embedding_server.py
"""

import numpy as np
from typing import List, Optional
import logging

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

import torch
from PIL import Image
from .schemas import EmbeddingModel

logger = logging.getLogger(__name__)


class RTLDTextEmbeddingModel(EmbeddingModel):
    """Text embedding model using SentenceTransformer"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: Optional[str] = None):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not installed")

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Loading SentenceTransformer model: {model_name}")
        self.model = SentenceTransformer(model_name, device=self.device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded with dimension: {self.dimension}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )

        return embeddings.tolist()

    def get_dimension(self) -> int:
        return self.dimension


class RTLDImageEmbeddingModel:
    """Image embedding model using CLIP"""

    def __init__(self, model_name: str = "ViT-B/32", device: Optional[str] = None):
        if not CLIP_AVAILABLE:
            raise ImportError("CLIP not available")

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Loading CLIP model: {model_name}")
        self.model, self.preprocess = clip.load(model_name, device=self.device)
        self.dimension = 512  # CLIP ViT-B/32 dimension

    def embed_image(self, image_path: str) -> List[float]:
        """Generate embedding for image"""
        try:
            image = Image.open(image_path).convert('RGB')
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                features = self.model.encode_image(image_input)
                features = features.cpu().numpy()

            # Normalize
            norms = np.linalg.norm(features, axis=1, keepdims=True)
            features = features / norms

            return features[0].tolist()

        except Exception as e:
            logger.error(f"Error embedding image {image_path}: {e}")
            # Return zero vector as fallback
            return [0.0] * self.dimension


class RTLDUnifiedEmbeddingModel:
    """Unified embedding model that handles both text and images"""

    def __init__(
        self,
        text_model_name: str = "all-MiniLM-L6-v2",
        image_model_name: str = "ViT-B/32",
        device: Optional[str] = None
    ):
        self.text_model = RTLDTextEmbeddingModel(text_model_name, device)
        self.image_model = None
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if CLIP_AVAILABLE:
            try:
                self.image_model = RTLDImageEmbeddingModel(image_model_name, device)
                logger.info("CLIP image model loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load CLIP model: {e}")
        else:
            logger.warning("CLIP not available - image embedding disabled")

        # Use text model dimension as primary
        self.dimension = self.text_model.get_dimension()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        return self.text_model.embed_texts(texts)

    def embed_image(self, image_path: str) -> List[float]:
        """Generate embedding for image"""
        if self.image_model:
            return self.image_model.embed_image(image_path)
        else:
            logger.warning("Image embedding not available, returning zero vector")
            return [0.0] * self.dimension

    def get_dimension(self) -> int:
        return self.dimension