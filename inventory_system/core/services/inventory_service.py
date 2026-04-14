from inventory_system.core.patterns.item_factory import ItemFactory
from inventory_system.core.patterns.sorting_strategy import SortByName
from inventory_system.logs.init import get_logger

class InventoryService:
    def __init__(self, repository, sorting_strategy=None):
        # The service coordinates business rules between the UI and storage layer.
        self.repo = repository
        self.sorter = sorting_strategy or SortByName()
        self.logger = get_logger()

    # ADD ITEM
    def add_item(self, category, name, quantity, **extra):
        item = ItemFactory.create_item(
            category=category,
            name=name,
            quantity=quantity,
            **extra
        )
        self.repo.insert(item)
        self.logger.info(
            "Added item '%s' (category=%s, quantity=%s, department=%s, location=%s)",
            item.name,
            item.category,
            item.quantity,
            item.department,
            item.location,
        )
        return item

    # LIST ITEMS
    def list_items(self):
        items = self.repo.get_all()
        return self.sorter.sort(items)

    # SEARCH
    def search_items(self, keyword):
        keyword = keyword.lower()
        return [i for i in self.repo.get_all() if keyword in i.name.lower()]

    # CHECK OUT
    def check_out_item(self, name, user, due_date):
        if hasattr(self.repo, "checkout_item_atomic"):
            item = self.repo.checkout_item_atomic(name, user, due_date)
            self.logger.info(
                "Checked out item '%s' to %s with due date %s",
                item.name,
                user,
                item.due_date,
            )
            return item

        item = self.repo.get_by_name(name)
        if not item:
            self.logger.warning("Checkout failed because item '%s' was not found", name)
            raise ValueError("Item not found.")

        item.check_out(user, due_date)
        self.repo.insert_checkout(item.name, user, due_date)
        self.repo.update(item)
        self.logger.info(
            "Checked out item '%s' to %s with due date %s",
            item.name,
            user,
            item.due_date,
        )
        return item

    # CHECK IN
    def check_in_item(self, name):
        item = self.repo.get_by_name(name)
        if not item:
            self.logger.warning("Check-in failed because item '%s' was not found", name)
            raise ValueError("Item not found.")

        if item.status in {"lost", "in_repair"}:
            self.logger.warning(
                "Check-in blocked because item '%s' has status '%s'",
                name,
                item.status,
            )
            raise ValueError("Item is not currently checked out.")

        returned = self.repo.return_oldest_checkout(name)
        if not returned:
            self.logger.warning("Check-in failed because item '%s' had no active checkouts", name)
            raise ValueError("Item is not currently checked out.")

        item.update_quantity(1)
        active_checkouts = self.repo.count_active_checkouts(name)
        item.status = "checked_out" if active_checkouts > 0 else "available"
        item.checked_out_by = None
        item.due_date = None
        self.repo.update(item)
        self.logger.info("Checked in item '%s'", item.name)
        return item

    # MARK IN REPAIR
    def mark_in_repair(self, name):
        item = self.repo.get_by_name(name)
        if not item:
            self.logger.warning("Mark in repair failed because item '%s' was not found", name)
            raise ValueError("Item not found.")
        if hasattr(self.repo, "count_active_checkouts") and self.repo.count_active_checkouts(name) > 0:
            self.logger.warning(
                "Mark in repair blocked because item '%s' still has active checkouts",
                name,
            )
            raise ValueError("Cannot mark item as in repair while it has active checkouts.")
        item.status = "in_repair"
        self.repo.update(item)
        self.logger.info("Marked item '%s' as in_repair", item.name)
        return item

    # MARK LOST
    def mark_lost(self, name):
        item = self.repo.get_by_name(name)
        if not item:
            self.logger.warning("Mark lost failed because item '%s' was not found", name)
            raise ValueError("Item not found.")
        if hasattr(self.repo, "count_active_checkouts") and self.repo.count_active_checkouts(name) > 0:
            self.logger.warning(
                "Mark lost blocked because item '%s' still has active checkouts",
                name,
            )
            raise ValueError("Cannot mark item as lost while it has active checkouts.")
        item.status = "lost"
        self.repo.update(item)
        self.logger.info("Marked item '%s' as lost", item.name)
        return item

    # FILTER BY DEPARTMENT
    def filter_by_department(self, department):
        return [i for i in self.repo.get_all() if i.department == department]

    # FILTER BY LOCATION
    def filter_by_location(self, location):
        return [i for i in self.repo.get_all() if i.location == location]

    # GET OVERDUE ITEMS
    def get_overdue_items(self):
        from datetime import datetime
        overdue = []

        # Only checked-out items with due dates can be overdue.
        for item in self.repo.get_all():
            if item.status == "checked_out" and item.due_date:
                if item.due_date < datetime.now().date():
                    overdue.append(item)

        return overdue

    # CHANGE SORT STRATEGY
    def set_sort_strategy(self, strategy):
        self.sorter = strategy
        self.logger.info("Changed sorting strategy to %s", type(strategy).__name__)
