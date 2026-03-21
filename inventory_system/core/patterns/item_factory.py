
from inventory_system.core.models.item import Item
from inventory_system.core.models.perishable_item import PerishableItem

class ItemFactory:
    """
    Factory class used to create Item or PerishableItem objects
    for the Alfred State Equipment Tracking System.
    """

    @staticmethod
    def create_item(category: str, name: str, quantity: int, **extra):
        category = category.lower().strip()

        # Perishable item
        if category == "perishable":
            if "expiration_date" not in extra:
                raise ValueError("Perishable items require an expiration_date.")

            return PerishableItem(
                name=name,
                quantity=quantity,
                expiration_date=extra["expiration_date"],
                department=extra.get("department", "General"),
                location=extra.get("location", "Unknown"),
                status=extra.get("status", "available"),
                checked_out_by=extra.get("checked_out_by"),
                due_date=extra.get("due_date")
            )

        # General item
        return Item(
            name=name,
            quantity=quantity,
            category=category,
            department=extra.get("department", "General"),
            location=extra.get("location", "Unknown"),
            status=extra.get("status", "available"),
            checked_out_by=extra.get("checked_out_by"),
            due_date=extra.get("due_date")
        )
