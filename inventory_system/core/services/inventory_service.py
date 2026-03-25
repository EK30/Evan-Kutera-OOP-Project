
from inventory_system.core.patterns.item_factory import ItemFactory
from inventory_system.core.patterns.sorting_strategy import SortByName

class InventoryService:
    def __init__(self, repository, sorting_strategy=None):
        # The service coordinates business rules between the UI and storage layer.
        self.repo = repository
        self.sorter = sorting_strategy or SortByName()

    # ADD ITEM
    def add_item(self, category, name, quantity, **extra):
        item = ItemFactory.create_item(
            category=category,
            name=name,
            quantity=quantity,
            **extra
        )
        self.repo.insert(item)
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
        item = self.repo.get_by_name(name)
        if not item:
            raise ValueError("Item not found.")

        item.check_out(user, due_date)
        self.repo.update(item)
        return item

    # CHECK IN
    def check_in_item(self, name):
        item = self.repo.get_by_name(name)
        if not item:
            raise ValueError("Item not found.")

        item.check_in()
        self.repo.update(item)
        return item

    # MARK IN REPAIR
    def mark_in_repair(self, name):
        item = self.repo.get_by_name(name)
        item.status = "in_repair"
        self.repo.update(item)
        return item

    # MARK LOST
    def mark_lost(self, name):
        item = self.repo.get_by_name(name)
        item.status = "lost"
        self.repo.update(item)
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
