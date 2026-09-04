import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from config import Config

logger = logging.getLogger(__name__)

_model_instance = None


def get_embedding_model() -> SentenceTransformer:
    """Returns a singleton instance of the SentenceTransformer model."""
    global _model_instance
    if _model_instance is None:
        model_name = Config.EMBEDDING_MODEL
        logger.info(f"Loading SentenceTransformer model: {model_name}")
        _model_instance = SentenceTransformer(model_name)
    return _model_instance


class EmbeddingService:
    def __init__(self, model: SentenceTransformer = None):
        self.model = model or get_embedding_model()

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generates L2-normalized vector embeddings for a list of text strings.
        Normalizing vectors ensures inner product (FAISS IndexFlatIP) equals cosine similarity.
        """
        if not texts:
            return np.empty((0, 384), dtype=np.float32)

        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        # Normalize vectors for Cosine Similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10  # Prevent division by zero
        normalized_embeddings = (embeddings / norms).astype(np.float32)
        return normalized_embeddings

    def embed_raw_items(self, raw_items: List[Dict[str, Any]]) -> np.ndarray:
        """
        Combines headline and body for each raw news item and computes normalized embeddings.
        """
        texts = [f"{item.get('headline', '')}\n{item.get('body', '')}" for item in raw_items]
        return self.generate_embeddings(texts)
