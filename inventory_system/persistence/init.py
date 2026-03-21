# Database and repository access layer.
import sqlite3

def initialize_database(db_path="inventory.db"):
    conn = sqlite3.connect(db_path)

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

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()

