from abc import ABC, abstractmethod

class SortStrategy(ABC):
    """
    Abstract base class for sorting strategies.
    All sorting strategies must implement the sort() method.
    """

    @abstractmethod
    def sort(self, items):
        pass


class SortByName(SortStrategy):
    """
    Sort items alphabetically by name.
    """

    def sort(self, items):
        return sorted(items, key=lambda item: item.name.lower())


class SortByQuantity(SortStrategy):
    """
    Sort items by quantity ascending.
    """

    def sort(self, items):
        return sorted(items, key=lambda item: item.quantity)


class SortByExpiration(SortStrategy):
    """
    Sort perishable items by expiration date (oldest → newest).
    Works only if items have expiration_date attribute.
    """

    def sort(self, items):
        # Filter items that have expiration dates
        perishable_items = [i for i in items if hasattr(i, "expiration_date")]

        # Non-perishable items go last
        non_perishables = [i for i in items if not hasattr(i, "expiration_date")]

        # Sort perishables by soonest expiration date
        perishable_items_sorted = sorted(
            perishable_items,
            key=lambda item: item.expiration_date
        )

        return perishable_items_sorted + non_perishables