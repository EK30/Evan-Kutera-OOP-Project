import sqlite3
from datetime import datetime

from inventory_system.persistence.repository import Repository
from inventory_system.core.models.item import Item
from inventory_system.core.models.perishable_item import PerishableItem

class SQLiteRepository(Repository):
    def __init__(self, db_path="inventory.db"):
        self.db_path = db_path
        self._connect()

    def _connect(self):
        # row_factory lets us access columns by name instead of index.
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row


    # INSERT -----------------------------------------------------------------
    def insert(self, item):
        query = """
            INSERT INTO items 
            (name, quantity, category, department, location, status, checked_out_by, due_date, expiration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.conn.execute(query, (
            item.name,
            item.quantity,
            item.category,
            item.department,
            item.location,
            item.status,
            item.checked_out_by,
            str(item.due_date) if item.due_date else None,
            str(item.expiration_date) if hasattr(item, "expiration_date") else None
        ))
        self.conn.commit()


    # GET ALL ----------------------------------------------------------------
    def get_all(self):
        cursor = self.conn.execute("SELECT * FROM items")
        items = []

        # Rebuild each database row as the correct Python object type.
        for row in cursor:
            if row["category"] == "perishable":
                items.append(
                    PerishableItem(
                        name=row["name"],
                        quantity=row["quantity"],
                        expiration_date=row["expiration_date"],
                        department=row["department"],
                        location=row["location"],
                        status=row["status"],
                        checked_out_by=row["checked_out_by"],
                        due_date=row["due_date"]
                    )
                )
            else:
                items.append(
                    Item(
                        name=row["name"],
                        quantity=row["quantity"],
                        category=row["category"],
                        department=row["department"],
                        location=row["location"],
                        status=row["status"],
                        checked_out_by=row["checked_out_by"],
                        due_date=row["due_date"]
                    )
                )
        return items


    # GET ONE ---------------------------------------------------------------
    def get_by_name(self, name: str):
        cursor = self.conn.execute("SELECT * FROM items WHERE name = ?", (name,))
        row = cursor.fetchone()

        if not row:
            return None

        # Match the object type to the saved category before returning it.
        if row["category"] == "perishable":
            return PerishableItem(
                name=row["name"],
                quantity=row["quantity"],
                expiration_date=row["expiration_date"],
                department=row["department"],
                location=row["location"],
                status=row["status"],
                checked_out_by=row["checked_out_by"],
                due_date=row["due_date"]
            )
        else:
            return Item(
                name=row["name"],
                quantity=row["quantity"],
                category=row["category"],
                department=row["department"],
                location=row["location"],
                status=row["status"],
                checked_out_by=row["checked_out_by"],
                due_date=row["due_date"]
            )


    # UPDATE -----------------------------------------------------------------
    def update(self, item):
        query = """
            UPDATE items
            SET quantity=?, category=?, department=?, location=?, status=?, 
                checked_out_by=?, due_date=?, expiration_date=?
            WHERE name=?
        """

        # Save the current in-memory state of the item back to the database.
        self.conn.execute(query, (
            item.quantity,
            item.category,
            item.department,
            item.location,
            item.status,
            item.checked_out_by,
            str(item.due_date) if item.due_date else None,
            str(item.expiration_date) if hasattr(item, "expiration_date") else None,
            item.name
        ))
        self.conn.commit()


    # DELETE -----------------------------------------------------------------
    def delete(self, name: str):
        self.conn.execute("DELETE FROM items WHERE name = ?", (name,))
        self.conn.commit()

    def close(self):
        self.conn.close()
