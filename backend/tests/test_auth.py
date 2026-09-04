import unittest
import sys
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from auth.jwt import generate_access_token
from auth.password import hash_password


class AuthAndRBACTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Mock user objects for direct JWT generation testing
        self.reporter_user = {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "Saketh",
            "email": "saketh@example.com",
            "role": "REPORTER"
        }
        self.editor_user = {
            "id": "22222222-2222-2222-2222-222222222222",
            "name": "Rahul",
            "email": "rahul@example.com",
            "role": "EDITOR"
        }
        self.desk_head_user = {
            "id": "33333333-3333-3333-3333-333333333333",
            "name": "Priya",
            "email": "priya@example.com",
            "role": "DESK_HEAD"
        }

        self.reporter_token = generate_access_token(self.reporter_user)
        self.editor_token = generate_access_token(self.editor_user)
        self.desk_head_token = generate_access_token(self.desk_head_user)

    # ----------------------------------------------------
    # 1. Unauthenticated Requests (401)
    # ----------------------------------------------------
    def test_unauthenticated_access_returns_401(self):
        endpoints = ["/api/auth/me", "/api/raw-items", "/api/test/publish", "/api/test/reporter-action"]
        for ep in endpoints:
            res = self.client.get(ep) if "raw-items" in ep or "me" in ep else self.client.post(ep)
            self.assertEqual(res.status_code, 401, f"Expected 401 for unauthenticated request to {ep}")
            data = res.get_json()
            self.assertEqual(data["error"], "Authentication required")

    # ----------------------------------------------------
    # 2. Invalid & Malformed Tokens (401)
    # ----------------------------------------------------
    def test_invalid_token_returns_401(self):
        headers = {"Authorization": "Bearer invalid.jwt.token"}
        res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.get_json()["error"], "Authentication required")

    def test_malformed_header_format_returns_401(self):
        headers = {"Authorization": f"Basic {self.reporter_token}"}
        res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res.status_code, 401)

    # ----------------------------------------------------
    # 3. Invalid Login Credentials (401)
    # ----------------------------------------------------
    def test_login_missing_fields_returns_400(self):
        res = self.client.post("/api/auth/login", json={"email": "saketh@example.com"})
        self.assertEqual(res.status_code, 400)

    # ----------------------------------------------------
    # 4. Valid Tokens & /api/auth/me (200)
    # ----------------------------------------------------
    def test_valid_reporter_auth_me(self):
        headers = {"Authorization": f"Bearer {self.reporter_token}"}
        res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["email"], "saketh@example.com")
        self.assertEqual(data["role"], "REPORTER")

    def test_valid_editor_auth_me(self):
        headers = {"Authorization": f"Bearer {self.editor_token}"}
        res = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["role"], "EDITOR")

    # ----------------------------------------------------
    # 5. Backend-Enforced RBAC Checks
    # ----------------------------------------------------
    def test_reporter_cannot_publish_returns_403(self):
        """CRITICAL REQUIREMENT: Reporter attempting POST /api/test/publish MUST return 403 Forbidden."""
        headers = {"Authorization": f"Bearer {self.reporter_token}"}
        res = self.client.post("/api/test/publish", headers=headers)
        self.assertEqual(res.status_code, 403, "Reporter must be rejected from publishing with 403 Forbidden")
        data = res.get_json()
        self.assertEqual(data["error"], "Insufficient permissions")

    def test_editor_can_publish_returns_200(self):
        """Editor possesses permission to execute publication action."""
        headers = {"Authorization": f"Bearer {self.editor_token}"}
        res = self.client.post("/api/test/publish", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")

    def test_reporter_can_execute_reporter_action(self):
        headers = {"Authorization": f"Bearer {self.reporter_token}"}
        res = self.client.post("/api/test/reporter-action", headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_desk_head_can_access_analytics(self):
        headers = {"Authorization": f"Bearer {self.desk_head_token}"}
        res = self.client.get("/api/test/deskhead-analytics", headers=headers)
        self.assertEqual(res.status_code, 200)

    def test_reporter_cannot_access_deskhead_analytics(self):
        headers = {"Authorization": f"Bearer {self.reporter_token}"}
        res = self.client.get("/api/test/deskhead-analytics", headers=headers)
        self.assertEqual(res.status_code, 403)


if __name__ == "__main__":
    unittest.main()
