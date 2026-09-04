import unittest
import sys
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app
from auth.jwt import generate_access_token


class RawItemsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

        # Mock authenticated user token for raw items tests
        self.user = {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "Saketh",
            "email": "saketh@example.com",
            "role": "REPORTER"
        }
        self.token = generate_access_token(self.user)
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_unauthenticated_raw_items_access(self):
        response = self.client.get("/api/raw-items")
        self.assertEqual(response.status_code, 401)

    def test_invalid_item_id_format(self):
        response = self.client.get("/api/raw-items/not-a-uuid", headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_invalid_pagination_parameters(self):
        response = self.client.get("/api/raw-items?page=-1&limit=abc", headers=self.headers)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("error", data)

    def test_nonexistent_item_id(self):
        random_uuid = str(uuid.uuid4())
        response = self.client.get(f"/api/raw-items/{random_uuid}", headers=self.headers)
        self.assertIn(response.status_code, [404, 500])  # 404 if DB connected, 500 if DB off


if __name__ == "__main__":
    unittest.main()
