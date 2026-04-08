# Architecture Overview

This document explains how the Alfred State Equipment Tracking System is structured and why each part exists.

## 1) Layered Design

The project follows a layered architecture:

1. `ui/` and `api/` (Input Layer)
- `ui/cli.py` handles command-line interaction.
- `api/app.py` handles HTTP requests/responses with Flask.
- These layers collect input, validate it, and call the service layer.

2. `core/services/` (Business Logic Layer)
- `InventoryService` contains the project rules:
  - add items
  - checkout/checkin flow
  - status updates (`lost`, `in_repair`)
  - filtering and overdue logic
- This keeps logic out of Flask routes and CLI menus.

3. `persistence/` (Data Access Layer)
- `Repository` is the abstraction (interface).
- `SQLiteRepository` is the concrete implementation.
- It is responsible for SQL operations and database mapping.

4. `core/models/` (Domain Model Layer)
- `Item` and `PerishableItem` represent inventory objects.
- Models hold item state and behavior (quantity, due dates, status fields).

## 2) Main Data Flow

### API request example (`POST /items/<name>/checkout`)

1. Flask route in `api/app.py` validates request JSON.
2. Route calls `InventoryService.check_out_item(...)`.
3. Service fetches item from repository.
4. Service applies checkout business rules.
5. Repository updates the `items` table and writes a checkout record.
6. API returns JSON response.

### CLI command example (check-in)

1. CLI menu calls `InventoryService.check_in_item(...)`.
2. Service verifies item and active checkout state.
3. Repository marks oldest active checkout as returned.
4. Quantity is increased and item status is recalculated.
5. Updated state is persisted and printed to user.

## 3) Database Structure

The project uses SQLite with two main tables:

- `items`
  - stores item identity and current inventory state
  - includes `quantity`, `category`, `department`, `location`, `status`, etc.

- `checkouts`
  - stores checkout history records
  - each row tracks borrower, due date, and `returned_at`
  - supports multi-copy checkout behavior

## 4) Why This Architecture Is Better

- Separation of concerns:
  - API/CLI handle input/output.
  - Service handles rules.
  - Repository handles SQL.
- Easier testing:
  - service and repository logic can be unit-tested independently.
- Easier maintenance:
  - swapping storage backends only affects repository layer.
- Reusability:
  - both CLI and API share the same `InventoryService`.

## 5) Current Known Boundaries

- Flask API and CLI are intentionally thin wrappers over `InventoryService`.
- SQLite is the current persistence backend.
- Logging is centralized through `logs/init.py` and used by service/API operations.

## 6) Future Refactor Opportunities

- Add DTO or schema validation layer for API payloads.
- Introduce transaction helpers in repository for complex operations.
- Add integration test suite focused on end-to-end API + database workflows.
