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
        repo = self.app.config.get("INVENTORY_REPO")
        if repo is not None:
            repo.close()
        self.temp_dir.cleanup()

    def test_health_check(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_root_route_lists_endpoints(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("message", payload)
        self.assertIn("endpoints", payload)
        self.assertIn("GET /items", payload["endpoints"])

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

    def test_checkout_rejects_invalid_due_date(self):
        self.client.post(
            "/items",
            json={
                "category": "general",
                "name": "Camera",
                "quantity": 1,
            },
        )
        response = self.client.post(
            "/items/Camera/checkout",
            json={"user": "Evan", "due_date": "04-30-2026"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("YYYY-MM-DD", response.get_json()["error"])

    def test_patch_item_updates_fields(self):
        self.client.post(
            "/items",
            json={
                "category": "general",
                "name": "Tablet",
                "quantity": 1,
                "department": "IT",
                "location": "SET 100",
            },
        )
        response = self.client.patch(
            "/items/Tablet",
            json={"quantity": 4, "location": "SET 210"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["quantity"], 4)
        self.assertEqual(payload["location"], "SET 210")

    def test_patch_item_rejects_negative_quantity(self):
        self.client.post(
            "/items",
            json={"category": "general", "name": "Monitor", "quantity": 1},
        )
        response = self.client.patch("/items/Monitor", json={"quantity": -1})

        self.assertEqual(response.status_code, 400)
        self.assertIn("0 or greater", response.get_json()["error"])

    def test_delete_item_removes_record(self):
        self.client.post(
            "/items",
            json={"category": "general", "name": "Wrench", "quantity": 1},
        )
        delete_response = self.client.delete("/items/Wrench")
        get_response = self.client.get("/items/Wrench")

        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(get_response.status_code, 404)

    def test_get_items_filters_by_status(self):
        self.client.post(
            "/items",
            json={"category": "general", "name": "Laptop A", "quantity": 1},
        )
        self.client.post(
            "/items",
            json={"category": "general", "name": "Laptop B", "quantity": 1},
        )
        self.client.post(
            "/items/Laptop B/checkout",
            json={"user": "Evan", "due_date": "2026-05-01"},
        )

        response = self.client.get("/items?status=checked_out")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["name"], "Laptop B")
        self.assertEqual(payload[0]["status"], "checked_out")

    def test_get_items_rejects_invalid_status(self):
        response = self.client.get("/items?status=damaged")

        self.assertEqual(response.status_code, 400)
        self.assertIn("status must be one of", response.get_json()["error"])


if __name__ == "__main__":
    unittest.main()
