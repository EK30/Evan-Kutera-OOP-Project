from datetime import datetime

class Item:
    """
    Base class representing general Alfred State equipment.
    Tracks location, department, checkout info, and status.
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
        
        # Alfred State–specific fields
        self.department = department          # e.g., "IT", "Engineering", "Athletics"
        self.location = location              # e.g., "SET 445"
        self.status = status                  # available / checked_out / in_repair / lost
        self.checked_out_by = checked_out_by  # Alfred State student or staff name
        self.due_date = (
            datetime.strptime(due_date, "%Y-%m-%d").date()
            if due_date else None
        )

    def update_quantity(self, amount: int):
        if self.quantity + amount < 0:
            raise ValueError("Resulting quantity cannot be negative.")
        self.quantity += amount

    def check_out(self, user: str, due_date: str):
        if self.status != "available":
            raise ValueError("Item is not available for checkout.")

        self.status = "checked_out"
        self.checked_out_by = user
        self.due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

    def check_in(self):
        self.status = "available"
        self.checked_out_by = None
        self.due_date = None

    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity,
            "category": self.category,
            "department": self.department,
            "location": self.location,
            "status": self.status,
            "checked_out_by": self.checked_out_by,
            "due_date": str(self.due_date) if self.due_date else None
        }

    def __str__(self):
        return (
            f"{self.name} (Qty: {self.quantity}, Status: {self.status}, "
            f"Location: {self.location}, Department: {self.department})"
        )

    def __repr__(self):
        return (
            f"Item(name={self.name!r}, quantity={self.quantity!r}, category={self.category!r}, "
            f"department={self.department!r}, location={self.location!r}, status={self.status!r})"
        )
