Inventory System Demo Checklist (5 Minutes)
==========================================

Pre-demo setup
--------------

1. Open terminal in project root.
2. Activate environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Start API:

```powershell
python -m inventory_system.api.app
```

4. Keep API terminal open.
5. Open Postman or browser for endpoints.

Live demo flow
--------------

1. Health check
- Request: `GET http://127.0.0.1:5000/health`
- Expected: `{"status":"ok"}`

2. Add item
- Request: `POST http://127.0.0.1:5000/items`
- Body:

```json
{
  "category": "general",
  "name": "Demo Laptop",
  "quantity": 3,
  "department": "IT",
  "location": "SET 101"
}
```

3. List items
- Request: `GET http://127.0.0.1:5000/items`
- Confirm `Demo Laptop` appears.

4. Checkout item
- Request: `POST http://127.0.0.1:5000/items/Demo Laptop/checkout`
- Body:

```json
{
  "user": "Student Demo",
  "due_date": "2026-05-01"
}
```

5. Patch item details
- Request: `PATCH http://127.0.0.1:5000/items/Demo Laptop`
- Body:

```json
{
  "quantity": 5,
  "location": "SET 210"
}
```

6. Mark item in repair
- Request: `PATCH http://127.0.0.1:5000/items/Demo Laptop/status`
- Body:

```json
{
  "status": "in_repair"
}
```

7. Delete item
- Request: `DELETE http://127.0.0.1:5000/items/Demo Laptop`

8. Confirm deletion
- Request: `GET http://127.0.0.1:5000/items/Demo Laptop`
- Expected: `404 Item not found`

Test proof (final step)
-----------------------

In a new terminal:

```powershell
python -m unittest inventory_system.tests.test_api
python -m unittest discover inventory_system/tests
```

Both commands should pass for final submission proof.
