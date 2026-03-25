import os
import tempfile
import unittest

try:
    from inventory_system.api.app import create_app
except ModuleNotFoundError:
    create_app = None


@unittest.skipIf(create_app is None, "Flask is not installed.")
class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "api_test.db")
        self.app = create_app(self.db_path)
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health_check(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_add_and_get_item(self):
        response = self.client.post(
            "/items",
            json={
                "category": "general",
                "name": "Laptop",
                "quantity": 3,
                "department": "IT",
                "location": "SET 101",
            },
        )
        self.assertEqual(response.status_code, 201)

        saved_item = self.client.get("/items/Laptop")
        self.assertEqual(saved_item.status_code, 200)
        self.assertEqual(saved_item.get_json()["name"], "Laptop")

    def test_checkout_item(self):
        self.client.post(
            "/items",
            json={
                "category": "general",
                "name": "Projector",
                "quantity": 1,
            },
        )

        response = self.client.post(
            "/items/Projector/checkout",
            json={"user": "Evan", "due_date": "2026-04-30"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "checked_out")


if __name__ == "__main__":
    unittest.main()
