# Rubric Evidence

Student: Evan Kutera  
Course: CISY 6503 - Object-Oriented Programming  
Project: Alfred State Equipment Tracking System

## Project Overview

This project is an equipment and inventory tracking system built as a business/scientific-style application. It includes:
- object-oriented architecture
- database persistence
- command-line interaction
- web API support
- automated testing
- logging

## Rubric Evidence

### Programming Language: Does it have OOP support?
- Language used: Python
- Python supports classes, inheritance, abstraction, composition, and polymorphism.

### Architecture: Does it make sense for the project?
- Architecture is layered:
  - CLI/API
  - Service layer
  - Repository layer
  - Domain models
- Evidence:
  - `inventory_system/ui/cli.py`
  - `inventory_system/api/app.py`
  - `inventory_system/core/services/inventory_service.py`
  - `inventory_system/persistence/sqlite_repository.py`
  - `docs/ARCHITECTURE.md`

### Unit testing
- Automated tests are included for:
  - domain models
  - service layer
  - repository layer
  - API layer
- Evidence:
  - `inventory_system/tests/test_item.py`
  - `inventory_system/tests/test_perishable_item.py`
  - `inventory_system/tests/test_inventory_service.py`
  - `inventory_system/tests/test_sqlite_repository.py`
  - `inventory_system/tests/test_api.py`

### Strategic integration and unit tests
- Unit tests cover model behavior and service logic.
- Integration-style tests cover API routes, checkout/checkin flows, error responses, and edge cases.
- Examples:
  - multi-checkout and multi-checkin
  - invalid dates
  - item not found
  - blocked status changes
  - blocked checkout on lost/in-repair items

### OOP concepts
- Encapsulation:
  - item state and behavior live in model classes
- Abstraction:
  - repository interface abstracts persistence behavior
- Inheritance:
  - `PerishableItem` extends `Item`
- Composition:
  - `InventoryService` uses repository and sorting strategy objects
- Decoupling:
  - API and CLI call service layer rather than directly managing SQL

### Do you have two OOP patterns?
- Yes
- Factory Pattern:
  - `inventory_system/core/patterns/item_factory.py`
- Strategy Pattern:
  - `inventory_system/core/patterns/sorting_strategy.py`

### Are they properly implemented?
- Factory creates the correct item type based on category.
- Strategy allows sorting behavior to be swapped without changing service logic.

### Do your features make sense?
- Features are aligned with an inventory/equipment tracking application:
  - add items
  - search/filter items
  - checkout/checkin flow
  - overdue checks
  - status management (`available`, `checked_out`, `in_repair`, `lost`)
  - logging
  - API access

### Is your project feature complete?
- For the inventory system topic, the project is close to feature complete for semester-project scope.
- Core business flow is implemented and tested.

### Does your database technology make sense?
- Yes
- SQLite is appropriate for a small-to-medium semester project.
- It is lightweight, local, simple to deploy, and easy to test.

### Does your database organization make sense?
- Yes
- `items` table stores item identity and current state.
- `checkouts` table stores checkout history and active checkout records.
- This supports multi-copy checkout and checkin tracking.

### Do you have an error management system?
- Yes
- API returns structured error responses:
  - `error`
  - `code`
- Service layer raises meaningful errors for invalid business operations.

### Do you have proper logging?
- Yes
- Logging is centralized and records important actions and failures.
- Evidence:
  - `inventory_system/logs/init.py`
  - `inventory_system/logs/inventory.log`

### Are your comments guiding other developers in refactoring the code base?
- Yes, comments and documentation were added to explain purpose and architecture without over-commenting.
- Evidence:
  - inline comments in service/repository/model code
  - `docs/ARCHITECTURE.md`
  - `docs/API.md`

### If you need threads did you use them properly?
- Not a major project requirement in the current design.
- The project does not rely on custom threading logic.

### If you need concurrency did you implement it properly?
- Concurrency is limited.
- Checkout logic was hardened with atomic repository checkout behavior to reduce race-condition risk.
- API repository handling was updated to avoid a single shared SQLite connection per request lifecycle.

## Supporting Documents

- `Readme.md`
- `docs/ARCHITECTURE.md`
- `docs/API.md`
- `CHECKIN_SUMMARY.md`
- `scripts/demo_rehearsal.ps1`

## Final Note

If the official assignment wording still requires a different topic, the only remaining clarification needed is whether this inventory-system project is approved as an acceptable semester-project topic.
