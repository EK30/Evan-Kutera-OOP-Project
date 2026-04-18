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
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS checkouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                borrower TEXT NOT NULL,
                due_date TEXT NOT NULL,
                returned_at TEXT,
                FOREIGN KEY (item_name) REFERENCES items(name)
            );
        """)
        self.conn.commit()

    def _ensure_connection(self):
        # Reconnect if the connection was explicitly closed.
        if not hasattr(self, "conn") or self.conn is None:
            self._connect()
            return

        try:
            self.conn.execute("SELECT 1")
        except sqlite3.ProgrammingError:
            self._connect()


    # INSERT -----------------------------------------------------------------
    def insert(self, item):
        self._ensure_connection()
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
        self._ensure_connection()
        cursor = self.conn.execute("SELECT * FROM items")
        items = []

        # Rebuild each database row as the correct Python object type.
        for row in cursor:
            checkout_summary = self._get_checkout_summary(row["name"])
            status = row["status"]
            checked_out_by = None
            due_date = None

            if status not in {"in_repair", "lost"}:
                if checkout_summary["active_count"] > 0:
                    status = "checked_out"
                    checked_out_by = checkout_summary["borrower"]
                    due_date = checkout_summary["due_date"]
                else:
                    status = "available"

            if row["category"] == "perishable":
                items.append(
                    PerishableItem(
                        name=row["name"],
                        quantity=row["quantity"],
                        expiration_date=row["expiration_date"],
                        department=row["department"],
                        location=row["location"],
                        status=status,
                        checked_out_by=checked_out_by,
                        due_date=due_date
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
                        status=status,
                        checked_out_by=checked_out_by,
                        due_date=due_date
                    )
                )
        return items


    # GET ONE ---------------------------------------------------------------
    def get_by_name(self, name: str):
        self._ensure_connection()
        cursor = self.conn.execute("SELECT * FROM items WHERE name = ?", (name,))
        row = cursor.fetchone()

        if not row:
            return None

        checkout_summary = self._get_checkout_summary(name)
        status = row["status"]
        checked_out_by = None
        due_date = None

        if status not in {"in_repair", "lost"}:
            if checkout_summary["active_count"] > 0:
                status = "checked_out"
                checked_out_by = checkout_summary["borrower"]
                due_date = checkout_summary["due_date"]
            else:
                status = "available"

        # Match the object type to the saved category before returning it.
        if row["category"] == "perishable":
            return PerishableItem(
                name=row["name"],
                quantity=row["quantity"],
                expiration_date=row["expiration_date"],
                department=row["department"],
                location=row["location"],
                status=status,
                checked_out_by=checked_out_by,
                due_date=due_date
            )
        else:
            return Item(
                name=row["name"],
                quantity=row["quantity"],
                category=row["category"],
                department=row["department"],
                location=row["location"],
                status=status,
                checked_out_by=checked_out_by,
                due_date=due_date
            )


    # UPDATE -----------------------------------------------------------------
    def update(self, item):
        self._ensure_connection()
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
        self._ensure_connection()
        # Remove checkout history first so re-adding an item with the same
        # name does not inherit stale active checkouts.
        self.conn.execute("DELETE FROM checkouts WHERE item_name = ?", (name,))
        self.conn.execute("DELETE FROM items WHERE name = ?", (name,))
        self.conn.commit()

    def close(self):
        if hasattr(self, "conn") and self.conn is not None:
            try:
                self.conn.close()
            except sqlite3.ProgrammingError:
                # In debug/threaded runs, teardown can occur from a different thread.
                pass
            self.conn = None

    # CHECKOUTS --------------------------------------------------------------
    def checkout_item_atomic(self, item_name: str, borrower: str, due_date: str):
        self._ensure_connection()
        try:
            # Lock writes so checkout validation and stock decrement happen as one unit.
            self.conn.execute("BEGIN IMMEDIATE")
            row = self.conn.execute(
                "SELECT quantity, status FROM items WHERE name = ?",
                (item_name,),
            ).fetchone()

            if not row:
                self.conn.rollback()
                raise ValueError("Item not found.")

            if row["status"] in {"lost", "in_repair"}:
                self.conn.rollback()
                raise ValueError("Item is not available for checkout.")

            if row["quantity"] <= 0:
                self.conn.rollback()
                raise ValueError("Item is out of stock.")

            self.conn.execute(
                """
                UPDATE items
                SET quantity = quantity - 1,
                    status = 'checked_out',
                    checked_out_by = ?,
                    due_date = ?
                WHERE name = ?
                """,
                (borrower, due_date, item_name),
            )
            self.conn.execute(
                """
                INSERT INTO checkouts (item_name, borrower, due_date, returned_at)
                VALUES (?, ?, ?, NULL)
                """,
                (item_name, borrower, due_date),
            )
            self.conn.commit()
        except:
            try:
                self.conn.rollback()
            except sqlite3.Error:
                pass
            raise

        return self.get_by_name(item_name)

    def insert_checkout(self, item_name: str, borrower: str, due_date: str):
        self._ensure_connection()
        self.conn.execute(
            """
            INSERT INTO checkouts (item_name, borrower, due_date, returned_at)
            VALUES (?, ?, ?, NULL)
            """,
            (item_name, borrower, due_date),
        )
        self.conn.commit()

    def return_oldest_checkout(self, item_name: str) -> bool:
        self._ensure_connection()
        row = self.conn.execute(
            """
            SELECT id
            FROM checkouts
            WHERE item_name = ? AND returned_at IS NULL
            ORDER BY id ASC
            LIMIT 1
            """,
            (item_name,),
        ).fetchone()

        if not row:
            return False

        self.conn.execute(
            "UPDATE checkouts SET returned_at = ? WHERE id = ?",
            (datetime.now().isoformat(timespec="seconds"), row["id"]),
        )
        self.conn.commit()
        return True

    def count_active_checkouts(self, item_name: str) -> int:
        self._ensure_connection()
        row = self.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM checkouts
            WHERE item_name = ? AND returned_at IS NULL
            """,
            (item_name,),
        ).fetchone()
        return int(row["count"])

    def _get_checkout_summary(self, item_name: str):
        self._ensure_connection()
        active_count_row = self.conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM checkouts
            WHERE item_name = ? AND returned_at IS NULL
            """,
            (item_name,),
        ).fetchone()
        oldest_active_row = self.conn.execute(
            """
            SELECT borrower, due_date
            FROM checkouts
            WHERE item_name = ? AND returned_at IS NULL
            ORDER BY id ASC
            LIMIT 1
            """,
            (item_name,),
        ).fetchone()

        return {
            "active_count": int(active_count_row["count"]),
            "borrower": oldest_active_row["borrower"] if oldest_active_row else None,
            "due_date": oldest_active_row["due_date"] if oldest_active_row else None,
        }
