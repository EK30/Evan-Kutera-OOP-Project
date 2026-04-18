# Database and repository access layer.
import sqlite3

def initialize_database(db_path="inventory.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            name TEXT PRIMARY KEY,
            quantity INTEGER NOT NULL,
            category TEXT NOT NULL,
            department TEXT,
            location TEXT,
            status TEXT,
            checked_out_by TEXT,
            due_date TEXT,
            expiration_date TEXT
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS checkouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            borrower TEXT NOT NULL,
            due_date TEXT NOT NULL,
            returned_at TEXT,
            FOREIGN KEY (item_name) REFERENCES items(name)
        );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")

