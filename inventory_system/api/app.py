from flask import Flask, jsonify, request, g
from datetime import datetime

from inventory_system.core.services.inventory_service import InventoryService
from inventory_system.logs.init import setup_logging
from inventory_system.persistence.init import initialize_database
from inventory_system.persistence.sqlite_repository import SQLiteRepository


def create_app(db_path="inventory.db"):
    app = Flask(__name__)
    logger = setup_logging()

    # Make sure the database exists before the API starts serving requests.
    initialize_database(db_path)
    app.config["DB_PATH"] = db_path

    def get_repo():
        if "inventory_repo" not in g:
            g.inventory_repo = SQLiteRepository(app.config["DB_PATH"])
        return g.inventory_repo

    def get_service():
        if "inventory_service" not in g:
            g.inventory_service = InventoryService(get_repo())
        return g.inventory_service

    @app.teardown_appcontext
    def close_repo(_exc):
        repo = g.pop("inventory_repo", None)
        if repo is not None:
            repo.close()

    def serialize_items(items):
        return [item.to_dict() for item in items]

    def error_response(message, code, status):
        return jsonify({"error": message, "code": code}), status

    def is_valid_date(date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except (TypeError, ValueError):
            return False

    @app.get("/")
    def index():
        return jsonify(
            {
                "message": "Inventory API is running.",
                "endpoints": [
                    "GET /health",
                    "GET /stats",
                    "GET /items",
                    "GET /items/<name>",
                    "POST /items",
                    "POST /items/<name>/checkout",
                    "POST /items/<name>/checkin",
                    "PATCH /items/<name>",
                    "PATCH /items/<name>/status",
                    "DELETE /items/<name>",
                ],
            }
        )

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.get("/stats")
    def get_stats():
        service = get_service()
        items = service.list_items()
        counts = {
            "available": 0,
            "checked_out": 0,
            "in_repair": 0,
            "lost": 0,
        }

        for item in items:
            if item.status in counts:
                counts[item.status] += 1

        return jsonify(
            {
                "total_items": len(items),
                "total_quantity": sum(item.quantity for item in items),
                "available": counts["available"],
                "checked_out": counts["checked_out"],
                "in_repair": counts["in_repair"],
                "lost": counts["lost"],
                "perishable_count": sum(1 for item in items if item.category == "perishable"),
                "overdue_count": len(service.get_overdue_items()),
            }
        )

    @app.get("/items")
    def get_items():
        service = get_service()
        department = request.args.get("department")
        location = request.args.get("location")
        search = request.args.get("search")
        overdue = request.args.get("overdue")
        status = request.args.get("status")
        allowed_statuses = {"available", "checked_out", "in_repair", "lost"}
        items = service.list_items()

        if status:
            status = status.strip().lower()
            if status not in allowed_statuses:
                return error_response(
                    "status must be one of: available, checked_out, in_repair, lost.",
                    "invalid_status_filter",
                    400,
                )
            items = [item for item in items if item.status == status]

        if department:
            items = [item for item in items if item.department == department]

        if location:
            items = [item for item in items if item.location == location]

        if search:
            term = search.lower()
            items = [item for item in items if term in item.name.lower()]

        if overdue is not None:
            overdue_value = overdue.strip().lower()
            if overdue_value not in {"true", "false"}:
                return error_response("overdue must be 'true' or 'false'.", "invalid_overdue_filter", 400)

            today = datetime.now().date()
            if overdue_value == "true":
                items = [
                    item for item in items
                    if item.status == "checked_out" and item.due_date and item.due_date < today
                ]
            else:
                items = [
                    item for item in items
                    if not (item.status == "checked_out" and item.due_date and item.due_date < today)
                ]

        return jsonify(serialize_items(items))

    @app.get("/items/<path:name>")
    def get_item(name):
        repo = get_repo()
        item = repo.get_by_name(name)
        if not item:
            return error_response("Item not found.", "item_not_found", 404)
        return jsonify(item.to_dict())

    @app.post("/items")
    def add_item():
        service = get_service()
        data = request.get_json(silent=True) or {}

        required_fields = ["category", "name", "quantity"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return error_response(
                f"Missing required fields: {', '.join(missing_fields)}",
                "missing_required_fields",
                400,
            )
        if not str(data["name"]).strip():
            return error_response("Item name cannot be empty.", "invalid_name", 400)

        try:
            quantity = int(data["quantity"])
            if quantity < 0:
                return error_response("Quantity must be 0 or greater.", "invalid_quantity", 400)

            category = str(data["category"]).strip().lower()
            expiration_date = data.get("expiration_date")
            if category == "perishable" and not expiration_date:
                return error_response(
                    "Perishable items require expiration_date.",
                    "missing_expiration_date",
                    400,
                )
            if expiration_date and not is_valid_date(expiration_date):
                return error_response("expiration_date must be YYYY-MM-DD.", "invalid_expiration_date", 400)

            item = service.add_item(
                category,
                data["name"],
                quantity,
                department=data.get("department", "General"),
                location=data.get("location", "Unknown"),
                expiration_date=expiration_date,
            )
        except Exception as exc:
            logger.exception("API failed to add item '%s'", data.get("name"))
            return error_response(str(exc), "add_item_failed", 400)

        return jsonify(item.to_dict()), 201

    @app.post("/items/<path:name>/checkout")
    def check_out_item(name):
        service = get_service()
        data = request.get_json(silent=True) or {}
        if "user" not in data or "due_date" not in data:
            return error_response("Both 'user' and 'due_date' are required.", "missing_checkout_fields", 400)
        if not str(data["user"]).strip():
            return error_response("User cannot be empty.", "invalid_user", 400)
        if not is_valid_date(data["due_date"]):
            return error_response("due_date must be YYYY-MM-DD.", "invalid_due_date", 400)

        try:
            item = service.check_out_item(name, data["user"], data["due_date"])
        except ValueError as exc:
            logger.exception("API failed to check out item '%s'", name)
            if "not found" in str(exc).lower():
                return error_response(str(exc), "item_not_found", 404)
            return error_response(str(exc), "checkout_failed", 400)
        except Exception as exc:
            logger.exception("API failed to check out item '%s'", name)
            return error_response(str(exc), "checkout_failed", 400)

        return jsonify(item.to_dict())

    @app.post("/items/<path:name>/checkin")
    def check_in_item(name):
        service = get_service()
        try:
            item = service.check_in_item(name)
        except ValueError as exc:
            logger.exception("API failed to check in item '%s'", name)
            if "not found" in str(exc).lower():
                return error_response(str(exc), "item_not_found", 404)
            return error_response(str(exc), "checkin_failed", 400)

        return jsonify(item.to_dict())

    @app.patch("/items/<path:name>")
    def update_item(name):
        repo = get_repo()
        data = request.get_json(silent=True) or {}
        allowed_fields = {"quantity", "department", "location"}
        invalid_fields = [field for field in data if field not in allowed_fields]

        if not data:
            return error_response("No update fields provided.", "missing_update_fields", 400)
        if invalid_fields:
            return error_response(f"Invalid fields: {', '.join(invalid_fields)}", "invalid_update_fields", 400)

        item = repo.get_by_name(name)
        if not item:
            return error_response("Item not found.", "item_not_found", 404)

        if "quantity" in data:
            try:
                quantity = int(data["quantity"])
            except (TypeError, ValueError):
                return error_response("quantity must be an integer.", "invalid_quantity_type", 400)
            if quantity < 0:
                return error_response("quantity must be 0 or greater.", "invalid_quantity", 400)
            item.quantity = quantity

        if "department" in data:
            if not str(data["department"]).strip():
                return error_response("department cannot be empty.", "invalid_department", 400)
            item.department = data["department"]

        if "location" in data:
            if not str(data["location"]).strip():
                return error_response("location cannot be empty.", "invalid_location", 400)
            item.location = data["location"]

        repo.update(item)
        logger.info("Updated item '%s' via PATCH /items/%s", item.name, name)
        return jsonify(item.to_dict())

    @app.patch("/items/<path:name>/status")
    def update_item_status(name):
        service = get_service()
        data = request.get_json(silent=True) or {}
        status = data.get("status")

        if status not in {"lost", "in_repair"}:
            return error_response("Status must be 'lost' or 'in_repair'.", "invalid_status_value", 400)

        try:
            if status == "lost":
                item = service.mark_lost(name)
            else:
                item = service.mark_in_repair(name)
        except ValueError as exc:
            logger.exception("API failed to update status for item '%s'", name)
            if "not found" in str(exc).lower():
                return error_response(str(exc), "item_not_found", 404)
            return error_response(str(exc), "status_update_failed", 400)

        return jsonify(item.to_dict())

    @app.delete("/items/<path:name>")
    def delete_item(name):
        repo = get_repo()
        item = repo.get_by_name(name)
        if not item:
            return error_response("Item not found.", "item_not_found", 404)

        repo.delete(name)
        logger.info("Deleted item '%s'", name)
        return jsonify({"message": f"Item '{name}' deleted successfully."})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
