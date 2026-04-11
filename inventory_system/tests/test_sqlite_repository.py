import os
import tempfile
import unittest

from inventory_system.core.models.item import Item
from inventory_system.core.models.perishable_item import PerishableItem
from inventory_system.persistence.init import initialize_database
from inventory_system.persistence.sqlite_repository import SQLiteRepository


class TestSQLiteRepository(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_inventory.db")
        initialize_database(self.db_path)
        self.repo = SQLiteRepository(self.db_path)

    def tearDown(self):
        self.repo.conn.close()
        self.temp_dir.cleanup()

    def test_insert_and_get_by_name_for_general_item(self):
        item = Item(
            name="Laptop",
            quantity=4,
            category="general",
            department="IT",
            location="SET 202",
        )

        self.repo.insert(item)
        saved_item = self.repo.get_by_name("Laptop")

        self.assertIsNotNone(saved_item)
        self.assertEqual(saved_item.name, "Laptop")
        self.assertEqual(saved_item.department, "IT")

    def test_insert_and_get_all_for_perishable_item(self):
        item = PerishableItem(
            name="Chemical",
            quantity=2,
            expiration_date="2026-11-30",
            department="Science",
            location="Lab 3",
        )

        self.repo.insert(item)
        items = self.repo.get_all()

        self.assertEqual(len(items), 1)
        self.assertIsInstance(items[0], PerishableItem)
        self.assertEqual(items[0].name, "Chemical")

    def test_update_persists_changed_fields(self):
        item = Item("Projector", 1, "general", status="available")
        self.repo.insert(item)

        item.status = "lost"
        item.location = "Storage"
        self.repo.update(item)
        updated_item = self.repo.get_by_name("Projector")

        self.assertEqual(updated_item.status, "lost")
        self.assertEqual(updated_item.location, "Storage")

    def test_delete_removes_item(self):
        item = Item("Tablet", 3, "general")
        self.repo.insert(item)

        self.repo.delete("Tablet")

        self.assertIsNone(self.repo.get_by_name("Tablet"))

    def test_checkout_records_affect_item_status(self):
        item = Item("Camera", 2, "general")
        self.repo.insert(item)

        self.repo.insert_checkout("Camera", "Evan", "2026-06-01")
        checked_out_item = self.repo.get_by_name("Camera")
        self.assertEqual(checked_out_item.status, "checked_out")
        self.assertEqual(checked_out_item.checked_out_by, "Evan")

        returned = self.repo.return_oldest_checkout("Camera")
        self.assertTrue(returned)
        available_item = self.repo.get_by_name("Camera")
        self.assertEqual(available_item.status, "available")

    def test_checkout_item_atomic_decrements_quantity_and_creates_checkout(self):
        self.repo.insert(Item("AtomicCamera", 2, "general"))

        updated = self.repo.checkout_item_atomic("AtomicCamera", "Evan", "2026-06-05")

        self.assertEqual(updated.quantity, 1)
        self.assertEqual(updated.status, "checked_out")
        self.assertEqual(self.repo.count_active_checkouts("AtomicCamera"), 1)

    def test_delete_cleans_checkout_history_for_reused_name(self):
        item = Item("ReusedName", 1, "general")
        self.repo.insert(item)
        self.repo.insert_checkout("ReusedName", "Evan", "2026-06-01")

        self.repo.delete("ReusedName")
        self.assertEqual(self.repo.count_active_checkouts("ReusedName"), 0)

        self.repo.insert(Item("ReusedName", 1, "general"))
        recreated = self.repo.get_by_name("ReusedName")
        self.assertEqual(recreated.status, "available")


if __name__ == "__main__":
    unittest.main()
