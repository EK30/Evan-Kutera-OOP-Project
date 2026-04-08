# Project Check-In Summary

Student: Evan Kutera  
Course: CISY 6503 - Object-Oriented Programming  
Project: Alfred State Equipment Tracking System  
Date: April 8, 2026

## What I Improved

1. Fixed architecture and layer responsibilities
- Added a dedicated architecture document (`docs/ARCHITECTURE.md`).
- Clarified the flow: API/CLI -> Service -> Repository -> Models.
- Kept business rules in `InventoryService` instead of route/menu logic.

2. Fixed checkout/checkin behavior bugs
- Implemented multi-copy checkout support.
- Quantity now decreases correctly when items are checked out.
- Quantity increases correctly when items are checked back in.
- Added logic to prevent checkout when stock is out.
- Added checkout ledger tracking in SQLite using a `checkouts` table.

3. Improved API reliability
- Added stronger API tests for multi-checkout and multi-checkin behavior.
- Verified third checkout fails when quantity reaches zero.
- Verified checkin restores stock and allows checkout again.

4. Added demo rehearsal tooling
- Added `scripts/demo_rehearsal.ps1` to run tests and rehearse API flow.
- Script now uses unique demo item names per run.
- Script includes clearer error output for faster debugging.

## Current Project Status

- CLI: working
- Flask API: working
- SQLite database: working
- Logging: working
- Unit tests: passing locally (`py -m unittest discover inventory_system/tests`)

## Key Evidence

- Architecture doc: `docs/ARCHITECTURE.md`
- API tests: `inventory_system/tests/test_api.py`
- Rehearsal script: `scripts/demo_rehearsal.ps1`
- Recent commits include:
  - multi-checkout implementation
  - architecture documentation
  - integration-style API test additions
  - demo rehearsal automation

## Next Steps

1. Add more integration tests for edge cases (lost/in_repair with checkouts).
2. Improve API error responses with consistent structured error codes.
3. Add lightweight API documentation for each endpoint request/response.
4. Continue small refactors to keep service logic simple and testable.
