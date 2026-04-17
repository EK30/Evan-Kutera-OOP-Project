Alfred State Equipment Tracking System
=====================================

CISY 6503 - Object-Oriented Programming Semester Project

This project is a Python-based inventory management system built to help Alfred State College track equipment across departments, classrooms, labs, and student borrow/return operations. It was developed as a semester project using object-oriented programming, design patterns, SQLite persistence, a command-line interface, logging, automated tests, and a Flask API.

Features
--------

Equipment management
- Add new equipment
- Track both general and perishable equipment
- Store quantity, location, department, and status

Checkout system
- Check out equipment to students or staff
- Support multi-copy checkout until stock reaches zero
- Assign due dates
- Check equipment back in
- View overdue items

Status tracking
- Available
- Checked out
- In repair
- Lost

Search and filtering
- Search by name
- Filter by department
- Filter by location

Persistence
- Save data using SQLite
- Automatically create the database tables if they do not exist
- Track active and returned checkouts with a separate `checkouts` table

Logging
- Record key inventory actions in a log file
- Track add, checkout, check-in, lost, repair, and error events

Flask API
- Expose inventory actions through REST-style endpoints
- Support listing items, adding items, checking items out and in, and updating status
- Return structured error responses with both `error` and `code`

Project Highlights
------------------

- Layered architecture: CLI/API -> Service -> Repository -> Models
- Two design patterns: Factory and Strategy
- SQLite database with separate `items` and `checkouts` tables
- Multi-copy checkout support with due-date tracking
- Unit tests plus integration-style API tests
- Deployment-ready dependency setup with `gunicorn`

Project Structure
-----------------

inventory_system/
- core/
  - models/              Item and PerishableItem classes
  - patterns/            ItemFactory and sorting strategies
  - services/            InventoryService business logic
- persistence/
  - init.py              Database initialization
  - repository.py        Abstract repository interface
  - sqlite_repository.py SQLite implementation
- api/
  - app.py               Flask API
- ui/
  - cli.py               Command-line interface
- tests/
  - test_item.py
  - test_perishable_item.py
  - test_inventory_service.py
  - test_sqlite_repository.py
  - test_api.py
- logs/
  - inventory.log        Application log file

Object-Oriented Concepts Used
-----------------------------

- Encapsulation: item data is stored and managed inside classes
- Inheritance: `PerishableItem` extends `Item`
- Abstraction: `Repository` defines the storage interface
- Polymorphism: sorting strategies can be swapped at runtime
- Composition: `InventoryService` uses a repository and sorting strategy

Design Patterns Used
--------------------

Factory Pattern
- `ItemFactory` creates the correct item type based on category

Strategy Pattern
- `SortByName`
- `SortByQuantity`
- `SortByExpiration`

Database Schema
---------------

The `items` table includes:
- `name`
- `quantity`
- `category`
- `department`
- `location`
- `status`
- `checked_out_by`
- `due_date`
- `expiration_date`

The `checkouts` table includes:
- `id`
- `item_name`
- `borrower`
- `due_date`
- `returned_at`

Running the Project
-------------------

1. Install dependencies

```powershell
py -m pip install -r requirements.txt
```

2. Run the CLI

```powershell
py -m inventory_system.ui.cli
```

3. Run the Flask API

```powershell
py -m inventory_system.api.app
```

4. Run the full test suite

```powershell
py -m unittest discover inventory_system/tests
```

5. Run the app with Gunicorn for deployment testing

```powershell
gunicorn "inventory_system.api.app:create_app()" --bind 127.0.0.1:8000
```

Latest Verification
-------------------

Last successful verification date: 2026-04-17

Verification commands:

```powershell
py -m unittest inventory_system.tests.test_api
py -m unittest discover inventory_system/tests
```

Result:
- Both commands passed.

Recommended Stable Setup (Semester Safe)
----------------------------------------

Use a project-local virtual environment so VS Code, Pylance, and your terminal always use the same Python and dependencies.

1. Build the local environment (one command)

```powershell
.\scripts\setup_env.ps1
```

2. Activate it when you work on the project

```powershell
.\.venv\Scripts\Activate.ps1
```

3. If PowerShell blocks activation, run this once

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Flask API Endpoints
-------------------

- `GET /`
- `GET /health`
- `GET /stats`
- `GET /items`
- `GET /items?status=available`
- `GET /items?status=checked_out`
- `GET /items?status=in_repair`
- `GET /items?status=lost`
- `GET /items?department=IT`
- `GET /items?location=SET 445`
- `GET /items?search=laptop`
- `GET /items?overdue=true`
- `GET /items/<name>`
- `POST /items`
- `POST /items/<name>/checkout`
- `POST /items/<name>/checkin`
- `PATCH /items/<name>`
- `PATCH /items/<name>/status`
- `DELETE /items/<name>`

API response notes
------------------

- Successful requests return JSON resource data.
- Error responses use this format:

```json
{
  "error": "Human-readable message",
  "code": "machine_readable_code"
}
```

Demo and API Collection
-----------------------

- 5-minute demo checklist: `docs/DEMO_CHECKLIST.md`
- Postman collection: `docs/postman/Inventory_API.postman_collection.json`
- Architecture overview: `docs/ARCHITECTURE.md`
- API documentation: `docs/API.md`
- Project check-in summary: `CHECKIN_SUMMARY.md`

Example JSON
------------

Add an item

```json
{
  "category": "general",
  "name": "Laptop",
  "quantity": 5,
  "department": "IT",
  "location": "SET 101"
}
```

Check out an item

```json
{
  "user": "Evan",
  "due_date": "2026-04-30"
}
```

Update item status

```json
{
  "status": "lost"
}
```

Unit Tests
----------

The project includes unit tests for:
- `Item`
- `PerishableItem`
- `InventoryService`
- `SQLiteRepository`
- Flask API routes
- Multi-checkout and multi-checkin flows
- Error-contract consistency
- Edge cases around lost/in-repair status handling

Log File
--------

Application events are written to:

`inventory_system/logs/inventory.log`

Project Status
--------------

The completed project currently includes:
- Core inventory models
- SQLite persistence
- CLI interface
- Logging
- Unit tests
- Flask API
- Deployment-ready dependency setup with `gunicorn`

Deployment Notes
----------------

For Linux server deployment, the project is designed to run behind `gunicorn` and `nginx`.

Typical production start command:

```bash
gunicorn "inventory_system.api.app:create_app()" --bind 127.0.0.1:8000
```
