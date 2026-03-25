import unittest
from datetime import datetime, timedelta

from inventory_system.core.models.perishable_item import PerishableItem


class TestPerishableItem(unittest.TestCase):
    def test_init_sets_perishable_category(self):
        item = PerishableItem(
            name="Chemical Kit",
            quantity=2,
            expiration_date="2026-12-01",
            department="Science",
            location="Lab 4",
        )

        self.assertEqual(item.category, "perishable")
        self.assertEqual(item.department, "Science")
        self.assertEqual(item.location, "Lab 4")

    def test_init_rejects_invalid_expiration_date(self):
        with self.assertRaises(ValueError):
            PerishableItem(
                name="Battery Pack",
                quantity=4,
                expiration_date="12/01/2026",
            )

    def test_is_expired_returns_true_for_past_date(self):
        yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
        item = PerishableItem(
            name="Gloves",
            quantity=10,
            expiration_date=yesterday,
        )

        self.assertTrue(item.is_expired())

    def test_is_expired_returns_false_for_future_date(self):
        tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
        item = PerishableItem(
            name="Masks",
            quantity=10,
            expiration_date=tomorrow,
        )

        self.assertFalse(item.is_expired())


if __name__ == "__main__":
    unittest.main()
