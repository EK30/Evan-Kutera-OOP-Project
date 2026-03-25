import unittest
from datetime import date

from inventory_system.core.models.item import Item


class TestItem(unittest.TestCase):
    def test_init_parses_due_date(self):
        item = Item(
            name="Laptop",
            quantity=3,
            category="general",
            due_date="2026-04-01",
        )

        self.assertEqual(item.name, "Laptop")
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.category, "general")
        self.assertEqual(item.due_date, date(2026, 4, 1))

    def test_init_rejects_negative_quantity(self):
        with self.assertRaises(ValueError):
            Item(name="Monitor", quantity=-1, category="general")

    def test_update_quantity_changes_stock(self):
        item = Item(name="Cable", quantity=5, category="general")

        item.update_quantity(-2)
        self.assertEqual(item.quantity, 3)

        item.update_quantity(4)
        self.assertEqual(item.quantity, 7)

    def test_update_quantity_rejects_negative_result(self):
        item = Item(name="Mouse", quantity=1, category="general")

        with self.assertRaises(ValueError):
            item.update_quantity(-2)

    def test_check_out_and_check_in_updates_status_fields(self):
        item = Item(name="Projector", quantity=1, category="general")

        item.check_out("Evan", "2026-04-15")
        self.assertEqual(item.status, "checked_out")
        self.assertEqual(item.checked_out_by, "Evan")
        self.assertEqual(item.due_date, date(2026, 4, 15))

        item.check_in()
        self.assertEqual(item.status, "available")
        self.assertIsNone(item.checked_out_by)
        self.assertIsNone(item.due_date)

    def test_to_dict_returns_expected_fields(self):
        item = Item(
            name="Laptop",
            quantity=2,
            category="general",
            department="IT",
            location="SET 101",
            status="checked_out",
            checked_out_by="Evan",
            due_date="2026-04-20",
        )

        self.assertEqual(
            item.to_dict(),
            {
                "name": "Laptop",
                "quantity": 2,
                "category": "general",
                "department": "IT",
                "location": "SET 101",
                "status": "checked_out",
                "checked_out_by": "Evan",
                "due_date": "2026-04-20",
            },
        )


if __name__ == "__main__":
    unittest.main()
