# Inventory API Documentation

Base URL (local): `http://127.0.0.1:5000`

## Response Format

Success responses return JSON data for the resource.

Error responses return:

```json
{
  "error": "Human-readable message"
}
```

Common status codes:
- `200` OK
- `201` Created
- `400` Bad Request
- `404` Not Found

## Endpoints

### `GET /`
Returns a basic API message and endpoint list.

Success example:

```json
{
  "message": "Inventory API is running.",
  "endpoints": ["GET /health", "GET /items"]
}
```

---

### `GET /health`
Health check endpoint.

Success example:

```json
{
  "status": "ok"
}
```

---

### `GET /stats`
Returns inventory summary counts.

Success example:

```json
{
  "total_items": 2,
  "total_quantity": 3,
  "available": 1,
  "checked_out": 1,
  "in_repair": 0,
  "lost": 0,
  "perishable_count": 1,
  "overdue_count": 0
}
```

---

### `GET /items`
Returns all items, with optional filters.

Query parameters:
- `status` = `available | checked_out | in_repair | lost`
- `department` = department name (exact match)
- `location` = location name (exact match)
- `search` = partial name match (case-insensitive)
- `overdue` = `true | false`

Example:
`GET /items?status=checked_out&department=IT&search=laptop`

Validation errors:
- invalid `status` -> `400`
- invalid `overdue` -> `400`

---

### `GET /items/<name>`
Returns one item by name.

Success example:

```json
{
  "name": "Laptop",
  "quantity": 2,
  "category": "general",
  "department": "IT",
  "location": "SET 101",
  "status": "available",
  "checked_out_by": null,
  "due_date": null
}
```

Not found:

```json
{
  "error": "Item not found."
}
```

---

### `POST /items`
Creates a new item.

Required fields:
- `category` (`general` or `perishable`)
- `name`
- `quantity` (integer, `>= 0`)

Optional fields:
- `department` (default: `General`)
- `location` (default: `Unknown`)
- `expiration_date` (required if `category = perishable`, format `YYYY-MM-DD`)

Request example:

```json
{
  "category": "general",
  "name": "Projector",
  "quantity": 2,
  "department": "IT",
  "location": "SET 204"
}
```

Success: `201 Created`

Common validation errors (`400`):
- missing required fields
- empty name
- invalid quantity
- missing/invalid perishable expiration date

---

### `POST /items/<name>/checkout`
Checks out one unit of an item to a user.

Required fields:
- `user`
- `due_date` (format `YYYY-MM-DD`)

Request example:

```json
{
  "user": "Evan",
  "due_date": "2026-05-01"
}
```

Behavior:
- supports multi-copy checkout
- fails when stock is out

Possible responses:
- `200` checkout successful
- `400` invalid input or out of stock
- `404` item not found

---

### `POST /items/<name>/checkin`
Checks in one active checkout for the item.

Behavior:
- increases quantity by 1
- item stays `checked_out` if more active checkouts remain
- item returns to `available` when no active checkouts remain

Possible responses:
- `200` checkin successful
- `400` item is not currently checked out
- `404` item not found

---

### `PATCH /items/<name>`
Updates editable fields on an item.

Allowed fields:
- `quantity` (integer, `>= 0`)
- `department`
- `location`

Request example:

```json
{
  "quantity": 4,
  "location": "SET 210"
}
```

Possible responses:
- `200` update successful
- `400` invalid fields/values
- `404` item not found

---

### `PATCH /items/<name>/status`
Updates item status for maintenance/loss.

Allowed values:
- `lost`
- `in_repair`

Request example:

```json
{
  "status": "in_repair"
}
```

Possible responses:
- `200` status updated
- `400` invalid status value
- `404` item not found

---

### `DELETE /items/<name>`
Deletes an item by name.

Success example:

```json
{
  "message": "Item 'Projector' deleted successfully."
}
```

Possible responses:
- `200` delete successful
- `404` item not found

## Quick Test Commands (PowerShell)

Run API:

```powershell
py -m inventory_system.api.app
```

Run API tests:

```powershell
py -m unittest inventory_system.tests.test_api
```
