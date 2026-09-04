import logging
from typing import List, Dict, Any, Tuple
import faiss
import numpy as np
from config import Config

logger = logging.getLogger(__name__)


class FAISSStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.raw_items: List[Dict[str, Any]] = []

    def build_index(self, raw_items: List[Dict[str, Any]], embeddings: np.ndarray):
        """Populates the FAISS IndexFlatIP store with normalized embeddings."""
        self.index.reset()
        self.raw_items = raw_items

        if embeddings.shape[0] == 0:
            return

        if embeddings.shape[1] != self.dimension:
            self.dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(self.dimension)

        self.index.add(embeddings)
        logger.info(f"Built FAISS index with {self.index.ntotal} vectors.")

    def retrieve_candidate_pairs(
        self,
        embeddings: np.ndarray,
        threshold: float = None,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Queries FAISS for nearest neighbors and returns candidate pairs above similarity threshold.
        Filters out self-matches and duplicate reverse pairs (i >= j).
        """
        threshold = threshold if threshold is not None else Config.FAISS_CANDIDATE_THRESHOLD
        top_k = top_k if top_k is not None else Config.FAISS_TOP_K

        n_items = len(self.raw_items)
        if n_items < 2 or embeddings.shape[0] == 0:
            return []

        # Limit top_k to n_items
        query_k = min(top_k + 1, n_items)
        scores, indices = self.index.search(embeddings, query_k)

        candidate_pairs = []
        seen_pairs = set()

        for i in range(n_items):
            for rank in range(query_k):
                j = indices[i][rank]
                sim_score = float(scores[i][rank])

                if j == -1 or i == j:
                    continue

                if sim_score >= threshold:
                    pair_key = (min(i, j), max(i, j))
                    if pair_key not in seen_pairs:
                        seen_pairs.add(pair_key)
                        candidate_pairs.append({
                            "item_a": self.raw_items[pair_key[0]],
                            "item_b": self.raw_items[pair_key[1]],
                            "similarity": sim_score
                        })

        logger.info(f"Retrieved {len(candidate_pairs)} candidate pairs with similarity >= {threshold}.")
        return candidate_pairs
