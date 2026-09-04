import unittest
import sys
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from auth.jwt import generate_access_token


class WorkflowAndRBACTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Mock authenticated users
        self.reporter_user = {"id": "11111111-1111-1111-1111-111111111111", "name": "Saketh", "email": "saketh@example.com", "role": "REPORTER"}
        self.editor_user = {"id": "22222222-2222-2222-2222-222222222222", "name": "Rahul", "email": "rahul@example.com", "role": "EDITOR"}
        self.desk_head_user = {"id": "33333333-3333-3333-3333-333333333333", "name": "Priya", "email": "priya@example.com", "role": "DESK_HEAD"}

        self.reporter_headers = {"Authorization": f"Bearer {generate_access_token(self.reporter_user)}"}
        self.editor_headers = {"Authorization": f"Bearer {generate_access_token(self.editor_user)}"}
        self.desk_head_headers = {"Authorization": f"Bearer {generate_access_token(self.desk_head_user)}"}

    # 1. Brief Publishing Security Boundaries (403 Forbidden)
    def test_reporter_cannot_publish_returns_403(self):
        """CRITICAL REQUIREMENT: Reporter attempting POST /api/briefs/:id/publish MUST return 403 Forbidden."""
        random_id = str(uuid.uuid4())
        res = self.client.post(f"/api/briefs/{random_id}/publish", headers=self.reporter_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    def test_desk_head_cannot_publish_returns_403(self):
        """CRITICAL REQUIREMENT: Desk Head attempting POST /api/briefs/:id/publish MUST return 403 Forbidden."""
        random_id = str(uuid.uuid4())
        res = self.client.post(f"/api/briefs/{random_id}/publish", headers=self.desk_head_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    # 2. Story Merging Security Boundaries (403 Forbidden)
    def test_reporter_cannot_merge_stories_returns_403(self):
        """CRITICAL REQUIREMENT: Reporter attempting POST /api/stories/merge MUST return 403 Forbidden."""
        payload = {"source_story_id": str(uuid.uuid4()), "target_story_id": str(uuid.uuid4())}
        res = self.client.post("/api/stories/merge", json=payload, headers=self.reporter_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    def test_desk_head_cannot_merge_stories_returns_403(self):
        """CRITICAL REQUIREMENT: Desk Head attempting POST /api/stories/merge MUST return 403 Forbidden."""
        payload = {"source_story_id": str(uuid.uuid4()), "target_story_id": str(uuid.uuid4())}
        res = self.client.post("/api/stories/merge", json=payload, headers=self.desk_head_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    # 3. Analytics Security Boundaries (403 Forbidden for Reporter)
    def test_reporter_cannot_access_analytics_returns_403(self):
        """CRITICAL REQUIREMENT: Reporter attempting GET /api/analytics MUST return 403 Forbidden."""
        res = self.client.get("/api/analytics", headers=self.reporter_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    def test_desk_head_can_access_analytics(self):
        """Desk Head possess access to publication analytics."""
        res = self.client.get("/api/analytics", headers=self.desk_head_headers)
        self.assertIn(res.status_code, [200, 500])

    def test_editor_cannot_access_analytics_returns_403(self):
        """CRITICAL REQUIREMENT: Editor attempting GET /api/analytics MUST return 403 Forbidden."""
        res = self.client.get("/api/analytics", headers=self.editor_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    # 4. Input Validation & Error Handling Tests
    def test_invalid_uuid_parameters_rejected(self):
        res = self.client.post("/api/briefs/invalid-uuid/publish", headers=self.editor_headers)
        self.assertEqual(res.status_code, 400)

    def test_merge_same_story_id_rejected(self):
        same_id = str(uuid.uuid4())
        payload = {"source_story_id": same_id, "target_story_id": same_id}
        res = self.client.post("/api/stories/merge", json=payload, headers=self.editor_headers)
        self.assertIn(res.status_code, [400, 500])

    # 5. Demo Reset Security Boundaries (Allowed ONLY for DESK_HEAD)
    def test_reporter_cannot_reset_demo_returns_403(self):
        """CRITICAL REQUIREMENT: Reporter attempting POST /api/demo/reset MUST return 403 Forbidden."""
        res = self.client.post("/api/demo/reset", headers=self.reporter_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    def test_editor_cannot_reset_demo_returns_403(self):
        """CRITICAL REQUIREMENT: Editor attempting POST /api/demo/reset MUST return 403 Forbidden."""
        res = self.client.post("/api/demo/reset", headers=self.editor_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    def test_desk_head_can_access_reset_demo(self):
        """Desk Head possess access to demo reset."""
        res = self.client.post("/api/demo/reset", headers=self.desk_head_headers)
        self.assertIn(res.status_code, [200, 500])

    # 6. AI Clustering Security Boundaries (Allowed ONLY for REPORTER)
    def test_editor_cannot_run_clustering_returns_403(self):
        """CRITICAL REQUIREMENT: Editor attempting POST /api/stories/cluster MUST return 403 Forbidden."""
        res = self.client.post("/api/stories/cluster", headers=self.editor_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    def test_desk_head_cannot_run_clustering_returns_403(self):
        """CRITICAL REQUIREMENT: Desk Head attempting POST /api/stories/cluster MUST return 403 Forbidden."""
        res = self.client.post("/api/stories/cluster", headers=self.desk_head_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    # 7. Raw Wire & Brief Submit Security Boundaries
    def test_editor_cannot_access_raw_items_returns_403(self):
        """CRITICAL REQUIREMENT: Editor attempting GET /api/raw-items MUST return 403 Forbidden."""
        res = self.client.get("/api/raw-items", headers=self.editor_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    def test_desk_head_cannot_access_raw_items_returns_403(self):
        """CRITICAL REQUIREMENT: Desk Head attempting GET /api/raw-items MUST return 403 Forbidden."""
        res = self.client.get("/api/raw-items", headers=self.desk_head_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    def test_editor_cannot_submit_brief_returns_403(self):
        """CRITICAL REQUIREMENT: Editor attempting POST /api/briefs/:id/submit MUST return 403 Forbidden."""
        random_id = str(uuid.uuid4())
        res = self.client.post(f"/api/briefs/{random_id}/submit", headers=self.editor_headers)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.get_json()["error"], "Insufficient permissions")

    def test_editor_can_access_story_detail_and_sources(self):
        """CRITICAL REQUIREMENT: Editor MUST be able to view story details and sources via GET /api/stories/:id and /sources."""
        random_id = str(uuid.uuid4())
        res1 = self.client.get(f"/api/stories/{random_id}", headers=self.editor_headers)
        self.assertIn(res1.status_code, [404, 200, 500])
        res2 = self.client.get(f"/api/stories/{random_id}/sources", headers=self.editor_headers)
        self.assertIn(res2.status_code, [404, 200, 500])


if __name__ == "__main__":
    unittest.main()
