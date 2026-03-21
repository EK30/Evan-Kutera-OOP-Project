from inventory_system.core.patterns.item_factory import ItemFactory
from inventory_system.core.patterns.sorting_strategy import SortByName

class InventoryService:
    """
    Core business logic for managing inventory items.
    Handles item creation, updates, sorting, searching, and passing data to/from the repository.
    """

    def __init__(self, repository, sorting_strategy=None):
        """
        repository: an object that implements insert(), get_all(), update(), delete()
        sorting_strategy: any class that inherits from SortStrategy
        """
        self.repository = repository
        self.sorting_strategy = sorting_strategy or SortByName()

    # ----------------------------------------------------------------------
    # CREATE
    # ----------------------------------------------------------------------
    def add_item(self, category: str, name: str, quantity: int, **extra):
        """
        Create an item (general or perishable) using the Factory Pattern,
        then insert into the repository.
        """
        item = ItemFactory.create_item(
            category=category,
            name=name,
            quantity=quantity,
            **extra
        )
        
        self.repository.insert(item)
        return item

    # ----------------------------------------------------------------------
    # READ
    # ----------------------------------------------------------------------
    def list_items(self):
        """
        Fetch all items from the repository and sort them.
        """
        items = self.repository.get_all()
        return self.sorting_strategy.sort(items)

    def search_items(self, keyword: str):
        """
        Simple search by matching text in item names (case insensitive).
        """
        items = self.repository.get_all()
        keyword_lower = keyword.lower()

        return [item for item in items if keyword_lower in item.name.lower()]

    # ----------------------------------------------------------------------
    # UPDATE
    # ----------------------------------------------------------------------
    def update_quantity(self, item_name: str, amount: int):
        """
        Increase or decrease quantity for a given item.
        """
        item = self.repository.get_by_name(item_name)
        if not item:
            raise ValueError(f"Item '{item_name}' not found.")

        item.update_quantity(amount)
        self.repository.update(item)

        return item

    # ----------------------------------------------------------------------
    # DELETE
    # ----------------------------------------------------------------------
    def delete_item(self, item_name: str):
        """
        Remove an item entirely from inventory.
        """
        item = self.repository.get_by_name(item_name)
        if not item:
            raise ValueError(f"Item '{item_name}' not found.")

        self.repository.delete(item_name)
        return True

    # ----------------------------------------------------------------------
    # STRATEGY SWAP
    # ----------------------------------------------------------------------
    def set_sort_strategy(self, strategy):
        """
        Change sorting strategy at runtime.
        """
        self.sorting_strategy = strategy