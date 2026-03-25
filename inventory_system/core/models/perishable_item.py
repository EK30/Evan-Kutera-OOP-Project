from datetime import datetime
from .item import Item

class PerishableItem(Item):
    """
    A subclass of Item that includes expiration logic (for lab chemicals, PPE, batteries, etc.).
    """

    def __init__(
        self,
        name: str,
        quantity: int,
        expiration_date: str,
        department: str = "General",
        location: str = "Unknown",
        status: str = "available",
        checked_out_by: str = None,
        due_date: str = None
    ):
        super().__init__(
            name=name,
            quantity=quantity,
            category="perishable",
            department=department,
            location=location,
            status=status,
            checked_out_by=checked_out_by,
            due_date=due_date
        )

        try:
            # Perishable items must have a valid expiration date for tracking.
            self.expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Expiration date must be YYYY-MM-DD.")

    def is_expired(self) -> bool:
        # Returns True when today's date is past the expiration date.
        today = datetime.now().date()
        return today > self.expiration_date

    def to_dict(self):
        base = super().to_dict()
        base["expiration_date"] = str(self.expiration_date)
        return base

    def __str__(self):
        return (
            f"{self.name} (Qty: {self.quantity}, Status: {self.status}, "
            f"Expires: {self.expiration_date}, Location: {self.location})"
        )
