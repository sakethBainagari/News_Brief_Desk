import unittest
import numpy as np
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from auth.jwt import generate_access_token
from services.embedding_service import EmbeddingService
from services.faiss_service import FAISSStore
from services.gemini_service import GeminiService, _parse_json_from_response
from services.story_clustering import StoryClusteringEngine, build_connected_components


class AIPipelineTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Auth tokens
        self.reporter_user = {"id": "11111111-1111-1111-1111-111111111111", "name": "Saketh", "email": "saketh@example.com", "role": "REPORTER"}
        self.editor_user = {"id": "22222222-2222-2222-2222-222222222222", "name": "Rahul", "email": "rahul@example.com", "role": "EDITOR"}

        self.reporter_token = generate_access_token(self.reporter_user)
        self.editor_token = generate_access_token(self.editor_user)
        self.reporter_headers = {"Authorization": f"Bearer {self.reporter_token}"}
        self.editor_headers = {"Authorization": f"Bearer {self.editor_token}"}

        # Mock items
        self.item1 = {
            "id": "00000000-0000-0000-0000-000000000001",
            "source_name": "Source A",
            "headline": "Hyderabad semiconductor facility receives clearance",
            "body": "Government cleared a $2B chip manufacturing facility in Hyderabad.",
            "category": "Technology"
        }
        self.item2 = {
            "id": "00000000-0000-0000-0000-000000000002",
            "source_name": "Source B",
            "headline": "Government clears $2bn chip plant in Hyderabad",
            "body": "A $2 billion chip manufacturing plant planned for Hyderabad received clearance.",
            "category": "Technology"
        }
        self.item3 = {
            "id": "00000000-0000-0000-0000-000000000003",
            "source_name": "Source C",
            "headline": "Bengaluru technology research center gets $800m commitment",
            "body": "A separate technology research center in Bengaluru secured an $800 million commitment.",
            "category": "Technology"
        }

    # 1. Embedding Service Tests
    def test_embedding_service_dimensions_and_normalization(self):
        service = EmbeddingService()
        embeddings = service.embed_raw_items([self.item1, self.item2])
        self.assertEqual(embeddings.shape[0], 2)
        self.assertEqual(embeddings.shape[1], 384)

        # Check L2 normalization
        norms = np.linalg.norm(embeddings, axis=1)
        np.testing.assert_allclose(norms, 1.0, rtol=1e-5)

    # 2. FAISS Candidate Retrieval Tests
    def test_faiss_candidate_retrieval(self):
        service = EmbeddingService()
        items = [self.item1, self.item2, self.item3]
        embeddings = service.embed_raw_items(items)

        store = FAISSStore(dimension=384)
        store.build_index(items, embeddings)
        pairs = store.retrieve_candidate_pairs(embeddings, threshold=0.50, top_k=5)

        self.assertGreater(len(pairs), 0)
        first_pair = pairs[0]
        self.assertIn("item_a", first_pair)
        self.assertIn("item_b", first_pair)
        self.assertIn("similarity", first_pair)
        self.assertGreaterEqual(first_pair["similarity"], 0.50)

    # 3. Gemini Response Parsing & Validation Tests
    def test_gemini_json_parsing_valid(self):
        raw_text = """```json
        {
          "decision": "SAME_EVENT",
          "confidence": 0.95,
          "reason": "Both reports describe the same $2B semiconductor plant in Hyderabad."
        }
        ```"""
        parsed = _parse_json_from_response(raw_text)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["decision"], "SAME_EVENT")
        self.assertEqual(parsed["confidence"], 0.95)

    def test_gemini_json_parsing_malformed_fallback(self):
        raw_text = "Not a JSON output"
        parsed = _parse_json_from_response(raw_text)
        self.assertIsNone(parsed)

    # 4. Connected Components Graph Clustering Tests
    def test_graph_clustering_same_event_merges(self):
        # 3 items: 0 and 1 are SAME_EVENT, 2 is DIFFERENT_EVENT
        same_event_edges = [(0, 1)]
        components = build_connected_components(3, same_event_edges)

        self.assertEqual(len(components), 2)
        # First component contains items [0, 1]
        self.assertIn(0, components[0])
        self.assertIn(1, components[0])
        # Second component contains isolated item [2]
        self.assertEqual(components[1], [2])

    def test_graph_clustering_different_event_does_not_merge(self):
        # No SAME_EVENT edges
        same_event_edges = []
        components = build_connected_components(3, same_event_edges)
        self.assertEqual(len(components), 3)

    # 5. RBAC Protection on Story APIs
    def test_unauthenticated_stories_api_returns_401(self):
        res = self.client.get("/api/stories")
        self.assertEqual(res.status_code, 401)

    def test_authenticated_reporter_can_access_stories_api(self):
        res = self.client.get("/api/stories", headers=self.reporter_headers)
        self.assertIn(res.status_code, [200, 500])

    def test_reporter_cannot_publish_story(self):
        res = self.client.post("/api/test/publish", headers=self.reporter_headers)
        self.assertEqual(res.status_code, 403)

    def test_editor_can_publish_story(self):
        res = self.client.post("/api/test/publish", headers=self.editor_headers)
        self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
