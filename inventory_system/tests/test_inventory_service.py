import unittest
from datetime import datetime, timedelta

from inventory_system.core.models.item import Item
from inventory_system.core.models.perishable_item import PerishableItem
from inventory_system.core.patterns.sorting_strategy import SortByQuantity
from inventory_system.core.services.inventory_service import InventoryService


class FakeRepository:
    def __init__(self, items=None):
        self.items = list(items or [])
        self.checkouts = []

    def insert(self, item):
        self.items.append(item)

    def get_all(self):
        return list(self.items)

    def get_by_name(self, name):
        for item in self.items:
            if item.name == name:
                return item
        return None

    def update(self, updated_item):
        for index, item in enumerate(self.items):
            if item.name == updated_item.name:
                self.items[index] = updated_item
                return

    def delete(self, name):
        self.items = [item for item in self.items if item.name != name]

    def insert_checkout(self, item_name, borrower, due_date):
        self.checkouts.append(
            {
                "item_name": item_name,
                "borrower": borrower,
                "due_date": due_date,
                "returned_at": None,
            }
        )

    def return_oldest_checkout(self, item_name):
        for checkout in self.checkouts:
            if checkout["item_name"] == item_name and checkout["returned_at"] is None:
                checkout["returned_at"] = "returned"
                return True
        return False

    def count_active_checkouts(self, item_name):
        return sum(
            1
            for checkout in self.checkouts
            if checkout["item_name"] == item_name and checkout["returned_at"] is None
        )


class TestInventoryService(unittest.TestCase):
    def test_add_item_creates_and_stores_general_item(self):
        repo = FakeRepository()
        service = InventoryService(repo)

        item = service.add_item(
            "general",
            "Laptop",
            5,
            department="IT",
            location="SET 101",
        )

        self.assertEqual(item.name, "Laptop")
        self.assertEqual(len(repo.get_all()), 1)
        self.assertEqual(repo.get_all()[0].department, "IT")

    def test_add_item_creates_perishable_item(self):
        repo = FakeRepository()
        service = InventoryService(repo)

        item = service.add_item(
            "perishable",
            "Chemical",
            2,
            department="Science",
            location="Lab 2",
            expiration_date="2026-12-31",
        )

        self.assertIsInstance(item, PerishableItem)
        self.assertEqual(repo.get_all()[0].category, "perishable")

    def test_search_items_matches_name_case_insensitively(self):
        repo = FakeRepository(
            [
                Item("Laptop Cart", 1, "general"),
                Item("Projector", 1, "general"),
            ]
        )
        service = InventoryService(repo)

        results = service.search_items("laptop")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Laptop Cart")

    def test_check_out_item_updates_existing_item(self):
        repo = FakeRepository([Item("Camera", 1, "general")])
        service = InventoryService(repo)

        item = service.check_out_item("Camera", "Evan", "2026-04-10")

        self.assertEqual(item.status, "checked_out")
        self.assertEqual(item.checked_out_by, "Evan")

    def test_check_in_item_restores_available_status(self):
        item = Item("Tablet", 0, "general", status="checked_out")
        repo = FakeRepository([item])
        repo.insert_checkout("Tablet", "Evan", "2026-04-10")
        service = InventoryService(repo)

        updated_item = service.check_in_item("Tablet")

        self.assertEqual(updated_item.status, "available")
        self.assertIsNone(updated_item.checked_out_by)

    def test_filter_methods_return_matching_items(self):
        repo = FakeRepository(
            [
                Item("Laptop", 2, "general", department="IT", location="SET 101"),
                Item("Wrench", 3, "general", department="Facilities", location="Shop"),
            ]
        )
        service = InventoryService(repo)

        self.assertEqual(len(service.filter_by_department("IT")), 1)
        self.assertEqual(len(service.filter_by_location("Shop")), 1)

    def test_check_out_item_allows_multiple_borrowers_until_stock_runs_out(self):
        repo = FakeRepository([Item("Camera", 2, "general")])
        service = InventoryService(repo)

        first = service.check_out_item("Camera", "Evan", "2026-04-10")
        self.assertEqual(first.quantity, 1)

        second = service.check_out_item("Camera", "Alex", "2026-04-11")

        self.assertEqual(second.quantity, 0)
        self.assertEqual(repo.count_active_checkouts("Camera"), 2)

        with self.assertRaises(ValueError):
            service.check_out_item("Camera", "Taylor", "2026-04-12")

    def test_get_overdue_items_returns_past_due_checked_out_items(self):
        overdue_date = (datetime.now().date() - timedelta(days=3)).isoformat()
        future_date = (datetime.now().date() + timedelta(days=3)).isoformat()

        overdue_item = Item("Laptop", 1, "general")
        overdue_item.check_out("Evan", overdue_date)

        current_item = Item("Monitor", 1, "general")
        current_item.check_out("Evan", future_date)

        repo = FakeRepository([overdue_item, current_item])
        service = InventoryService(repo)

        overdue = service.get_overdue_items()

        self.assertEqual(len(overdue), 1)
        self.assertEqual(overdue[0].name, "Laptop")

    def test_set_sort_strategy_changes_list_order(self):
        repo = FakeRepository(
            [
                Item("Laptop", 5, "general"),
                Item("Cable", 1, "general"),
            ]
        )
        service = InventoryService(repo)
        service.set_sort_strategy(SortByQuantity())

        items = service.list_items()

        self.assertEqual([item.name for item in items], ["Cable", "Laptop"])

    def test_check_in_blocks_items_marked_lost(self):
        item = Item("LostCamera", 0, "general", status="lost")
        repo = FakeRepository([item])
        repo.insert_checkout("LostCamera", "Evan", "2026-04-10")
        service = InventoryService(repo)

        with self.assertRaises(ValueError):
            service.check_in_item("LostCamera")

        self.assertEqual(repo.count_active_checkouts("LostCamera"), 1)
        self.assertEqual(repo.get_by_name("LostCamera").status, "lost")


if __name__ == "__main__":
    unittest.main()
