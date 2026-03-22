Alfred State Equipment Tracking System
CISY 6503 – Object‑Oriented Programming Semester Project
The Alfred State Equipment Tracking System is a Python‑based inventory management application designed to help Alfred State College track equipment across departments, labs, classrooms, and student borrow/return operations.
It uses Object‑Oriented Programming, Design Patterns, SQLite persistence, and a CLI user interface, all structured with clean architecture principles required for the semester project.

🚀 Features
🔷 Equipment Management

Add new equipment
Track general and perishable equipment
Manage quantity, location, department, and status

🔷 Checkout System

Check out equipment to students/staff
Set due dates
Track overdue items
Check items back in

🔷 Status Tracking

Mark equipment as:

Available
Checked Out
In Repair
Lost



🔷 Filtering & Search

Search by name
Filter by department
Filter by location
View overdue items

🔷 Persistence

Data saved permanently using SQLite
db_init.py automatically creates all tables


🏛 Project Architecture (Clean Architecture)
inventory_system/
│
├── core/
│   ├── models/            # Item & PerishableItem classes
│   ├── patterns/          # ItemFactory & Sorting Strategy
│   └── services/          # InventoryService business logic
│
├── persistence/
│   ├── repository.py      # Abstract repository interface
│   ├── sqlite_repository.py# SQLite implementation
│   └── db_init.py         # Creates database tables
│
├── ui/
│   └── cli.py             # CLI user interface
│
├── tests/                 # Unit tests (TBD)
└── logs/                  # Logging directory

This structure cleanly separates logic, storage, and presentation.

🧱 Object‑Oriented Concepts Used
✔ Encapsulation
All item data (name, quantity, status, location, etc.) is stored in dedicated classes.
✔ Inheritance
PerishableItem inherits from Item and adds expiration tracking.
✔ Abstraction
Repository defines the interface for all persistence implementations.
✔ Polymorphism
SortingStrategy allows multiple interchangeable sorting behaviors.
✔ Composition
InventoryService uses a repository and sorting strategy to manage items.

🧩 Design Patterns Used
🏭 Factory Pattern — ItemFactory

Creates the correct item type (Item or PerishableItem)
Simplifies object creation
Decouples UI from model logic
Makes adding new item types easy

🔀 Strategy Pattern — Sorting
Includes strategies:

Sort By Name
Sort By Quantity
Sort By Expiration

The user can switch sorting behavior at runtime.

🗄 Database (SQLite)
The items table includes:













































ColumnPurposenameUnique equipment namequantityHow many availablecategoryGeneral or perishabledepartmentWhich Alfred State departmentlocationWhere the item is storedstatusavailable, checked_out, in_repair, lostchecked_out_byStudent or staff namedue_dateReturn dateexpiration_dateFor perishable items
Database initialization file:
inventory_system/persistence/db_init.py

Run once to create tables:
Shellpython inventory_system/persistence/db_init.pyShow more lines

🖥 Running the Program (CLI)
From the project root:
Shellpython -m inventory_system.ui.cliShow more lines
The CLI supports:

Add equipment
List all equipment
Search
Check out
Check in
Mark as lost
Mark as in repair
Filter
View overdue items
Change sorting strategy
Exit


👨‍🎓 Alfred State Use‑Cases
IT Department

Loan out laptops
Track overdue checkouts
Track equipment in repair

Engineering Labs

Track tools and specialized equipment
Identify where equipment is stored (SET building, labs)

Athletics

Manage sports gear
Monitor lost/damaged equipment

Facilities / Maintenance

Manage tools and perishable supplies
Track expiration for PPE or chemicals


🧪 Unit Tests (Coming Next)
Planned tests:

Item model tests
Perishable item tests
Checkout logic
Repository CRUD operations
InventoryService integration tests


🛠 Planned Enhancements

Flask REST API
Barcode scanning
Web dashboard
Equipment reservation system
Logging to file (activity log)


📜 How This Meets the Project Rubric
✔ Clean architecture
✔ Multiple OOP patterns
✔ Persistence with SQLite
✔ CLI user interface
✔ Real‑world application
✔ Proper use of abstraction/inheritance/encapsulation
✔ Version control (GitHub)
✔ Ready for deployment (API optional next step)

🎉 Project Status: Actively In Development
This project is actively being built and improved.
Next priority: unit tests, logging, and Flask API.