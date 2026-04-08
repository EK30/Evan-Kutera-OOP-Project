from datetime import datetime

class Item:
    """
    Base class representing general Alfred State equipment.
    """

    def __init__(
        self,
        name: str,
        quantity: int,
        category: str,
        department: str = "General",
        location: str = "Unknown",
        status: str = "available",
        checked_out_by: str = None,
        due_date: str = None
    ):
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        self.name = name
        self.quantity = quantity
        self.category = category
        self.department = department
        self.location = location
        self.status = status
        self.checked_out_by = checked_out_by

        # Store due dates as date objects so overdue checks are easier later.
        self.due_date = (
            datetime.strptime(due_date, "%Y-%m-%d").date()
            if due_date else None
        )

    def update_quantity(self, amount: int):
        if self.quantity + amount < 0:
            raise ValueError("Resulting quantity cannot be negative.")
        self.quantity += amount

    def check_out(self, user: str, due_date: str):
        # Checking out an item updates both its status and borrower details.
        if self.status in {"in_repair", "lost"}:
            raise ValueError("Item is not available for checkout.")

        if self.quantity <= 0:
            raise ValueError("Item is out of stock.")

        self.quantity -= 1
        self.status = "checked_out"
        self.checked_out_by = user
        self.due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

    def check_in(self):
        # Returning an item clears any active checkout information.
        if self.status != "checked_out":
            raise ValueError("Item is not currently checked out.")

        self.quantity += 1
        self.status = "available"
        self.checked_out_by = None
        self.due_date = None

    def to_dict(self):
        # Convert the item to a dictionary for storage, APIs, or future exports.
        return {
            "name": self.name,
            "quantity": self.quantity,
            "category": self.category,
            "department": self.department,
            "location": self.location,
            "status": self.status,
            "checked_out_by": self.checked_out_by,
            "due_date": str(self.due_date) if self.due_date else None,
        }

    def __str__(self):
        parts = [
            f"{self.name}",
            f"Qty: {self.quantity}",
            f"Status: {self.status}",
            f"Location: {self.location}",
            f"Department: {self.department}"
        ]

        if self.checked_out_by:
            parts.append(f"Checked out by: {self.checked_out_by}")

        if self.due_date:
            parts.append(f"Due: {self.due_date}")

        return ", ".join(parts)

    def __repr__(self):
        return f"Item({self.name}, Qty={self.quantity}, Status={self.status})"
