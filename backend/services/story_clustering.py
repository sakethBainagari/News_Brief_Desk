from collections import defaultdict, deque
import logging
from typing import List, Dict, Any, Tuple, Set
from services.embedding_service import EmbeddingService
from services.faiss_service import FAISSStore
from services.gemini_service import GeminiService
from db.story_queries import (
    clear_existing_clusters,
    create_story_cluster,
    link_story_source,
    create_story_brief,
    save_clusters_batch
)
from db.queries import get_raw_items

logger = logging.getLogger(__name__)


def build_connected_components(n_items: int, same_event_edges: List[Tuple[int, int]]) -> List[List[int]]:
    """
    Constructs an adjacency graph and computes connected components.
    Vertices = raw item indices [0 .. n-1]
    Edges = verified SAME_EVENT candidate pairs
    """
    adj = defaultdict(list)
    for u, v in same_event_edges:
        adj[u].append(v)
        adj[v].append(u)

    visited = set()
    components = []

    for i in range(n_items):
        if i not in visited:
            comp = []
            queue = deque([i])
            visited.add(i)

            while queue:
                curr = queue.popleft()
                comp.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            components.append(comp)

    return components


class StoryClusteringEngine:
    def __init__(
        self,
        embedding_service: EmbeddingService = None,
        faiss_store: FAISSStore = None,
        gemini_service: GeminiService = None
    ):
        self.embedding_service = embedding_service or EmbeddingService()
        self.faiss_store = faiss_store or FAISSStore()
        self.gemini_service = gemini_service or GeminiService()

    def process_and_cluster(self, raw_items: List[Dict[str, Any]] = None, save_to_db: bool = True) -> Dict[str, Any]:
        """
        Executes full AI event-grouping pipeline:
        1. Fetch raw items
        2. Generate embeddings
        3. Retrieve FAISS candidate pairs
        4. Gemini event verification
        5. Connected components clustering
        6. Gemini brief generation & DB persistence
        """
        if raw_items is None:
            db_res = get_raw_items(page=1, limit=500)
            raw_items = db_res.get("items", [])

        n_items = len(raw_items)
        if n_items == 0:
            return {"total_items": 0, "total_clusters": 0, "same_event_matches": 0, "clusters": []}

        logger.info(f"Starting AI Event Grouping pipeline on {n_items} raw items...")

        # Step 1: Embeddings
        embeddings = self.embedding_service.embed_raw_items(raw_items)

        # Step 2: FAISS Candidate Retrieval
        self.faiss_store.build_index(raw_items, embeddings)
        candidate_pairs = self.faiss_store.retrieve_candidate_pairs(embeddings)

        # Map item ID -> index
        item_id_to_idx = {item["id"]: idx for idx, item in enumerate(raw_items)}

        # Step 3: Gemini Verification
        same_event_edges = []
        verification_results = {}

        for pair in candidate_pairs:
            item_a = pair["item_a"]
            item_b = pair["item_b"]
            idx_a = item_id_to_idx[item_a["id"]]
            idx_b = item_id_to_idx[item_b["id"]]

            v_res = self.gemini_service.verify_event_match(item_a, item_b)
            pair_key = (min(idx_a, idx_b), max(idx_a, idx_b))
            verification_results[pair_key] = v_res

            if v_res["decision"] == "SAME_EVENT":
                same_event_edges.append(pair_key)

        logger.info(f"Gemini verified {len(same_event_edges)} SAME_EVENT edges out of {len(candidate_pairs)} candidates.")

        # Step 4: Graph Clustering
        components = build_connected_components(n_items, same_event_edges)
        logger.info(f"Built {len(components)} story clusters from {n_items} raw items.")

        clusters_result = []

        for comp_indices in components:
            cluster_items = [raw_items[idx] for idx in comp_indices]

            # Pick canonical headline & category from earliest source
            sorted_items = sorted(
                cluster_items,
                key=lambda x: x.get("source_published_at") or x.get("ingested_at") or ""
            )
            earliest_item = sorted_items[0]
            canonical_headline = earliest_item.get("headline")
            category = earliest_item.get("category", "General")
            first_incoming_at = earliest_item.get("source_published_at") or earliest_item.get("ingested_at")

            # Calculate average confidence if multi-source
            comp_set = set(comp_indices)
            comp_confidences = []
            comp_reasons = []

            for (u, v), v_res in verification_results.items():
                if u in comp_set and v in comp_set and v_res["decision"] == "SAME_EVENT":
                    comp_confidences.append(v_res["confidence"])
                    comp_reasons.append(v_res["reason"])

            avg_confidence = float(sum(comp_confidences) / len(comp_confidences)) if comp_confidences else 1.0
            confidence_reason = "; ".join(comp_reasons[:2]) if comp_reasons else "Single-source item or direct event match."

            # Step 5: Brief Generation
            brief = self.gemini_service.generate_brief_draft(cluster_items)

            clusters_result.append({
                "canonical_headline": canonical_headline,
                "category": category,
                "confidence": avg_confidence,
                "confidence_reason": confidence_reason,
                "first_incoming_at": first_incoming_at,
                "source_count": len(cluster_items),
                "brief": brief,
                "cluster_items": cluster_items,
                "raw_item_ids": [item["id"] for item in cluster_items]
            })

        if save_to_db and clusters_result:
            try:
                save_clusters_batch(clusters_result)
            except Exception as e:
                logger.warning(f"Could not persist clusters to DB: {e}")

        return {
            "total_items": n_items,
            "total_clusters": len(clusters_result),
            "same_event_matches": len(same_event_edges),
            "candidate_pairs_evaluated": len(candidate_pairs),
            "clusters": clusters_result
        }
