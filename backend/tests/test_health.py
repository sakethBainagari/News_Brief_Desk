import unittest
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import create_app


class HealthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_api_root(self):
        response = self.client.get("/api")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("News Brief Desk API", data["name"])
        self.assertIn("endpoints", data)

    def test_health_endpoint(self):
        response = self.client.get("/api/health")
        self.assertIn(response.status_code, [200, 503])
        data = response.get_json()
        self.assertIn("service", data)
        self.assertIn("database", data)


if __name__ == "__main__":
    unittest.main()
