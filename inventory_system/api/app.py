from flask import Flask, jsonify, request
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
    repo = SQLiteRepository(db_path)
    service = InventoryService(repo)
    app.config["INVENTORY_REPO"] = repo

    @app.teardown_appcontext
    def close_repo(_exception):
        repo.close()

    def serialize_items(items):
        return [item.to_dict() for item in items]

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
                return jsonify({"error": "status must be one of: available, checked_out, in_repair, lost."}), 400
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
                return jsonify({"error": "overdue must be 'true' or 'false'."}), 400

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
        item = repo.get_by_name(name)
        if not item:
            return jsonify({"error": "Item not found."}), 404
        return jsonify(item.to_dict())

    @app.post("/items")
    def add_item():
        data = request.get_json(silent=True) or {}

        required_fields = ["category", "name", "quantity"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        if not str(data["name"]).strip():
            return jsonify({"error": "Item name cannot be empty."}), 400

        try:
            quantity = int(data["quantity"])
            if quantity < 0:
                return jsonify({"error": "Quantity must be 0 or greater."}), 400

            category = str(data["category"]).strip().lower()
            expiration_date = data.get("expiration_date")
            if category == "perishable" and not expiration_date:
                return jsonify({"error": "Perishable items require expiration_date."}), 400
            if expiration_date and not is_valid_date(expiration_date):
                return jsonify({"error": "expiration_date must be YYYY-MM-DD."}), 400

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
            return jsonify({"error": str(exc)}), 400

        return jsonify(item.to_dict()), 201

    @app.post("/items/<path:name>/checkout")
    def check_out_item(name):
        data = request.get_json(silent=True) or {}
        if "user" not in data or "due_date" not in data:
            return jsonify({"error": "Both 'user' and 'due_date' are required."}), 400
        if not str(data["user"]).strip():
            return jsonify({"error": "User cannot be empty."}), 400
        if not is_valid_date(data["due_date"]):
            return jsonify({"error": "due_date must be YYYY-MM-DD."}), 400

        try:
            item = service.check_out_item(name, data["user"], data["due_date"])
        except ValueError as exc:
            logger.exception("API failed to check out item '%s'", name)
            return jsonify({"error": str(exc)}), 404
        except Exception as exc:
            logger.exception("API failed to check out item '%s'", name)
            return jsonify({"error": str(exc)}), 400

        return jsonify(item.to_dict())

    @app.post("/items/<path:name>/checkin")
    def check_in_item(name):
        try:
            item = service.check_in_item(name)
        except ValueError as exc:
            logger.exception("API failed to check in item '%s'", name)
            return jsonify({"error": str(exc)}), 404

        return jsonify(item.to_dict())

    @app.patch("/items/<path:name>")
    def update_item(name):
        data = request.get_json(silent=True) or {}
        allowed_fields = {"quantity", "department", "location"}
        invalid_fields = [field for field in data if field not in allowed_fields]

        if not data:
            return jsonify({"error": "No update fields provided."}), 400
        if invalid_fields:
            return jsonify({"error": f"Invalid fields: {', '.join(invalid_fields)}"}), 400

        item = repo.get_by_name(name)
        if not item:
            return jsonify({"error": "Item not found."}), 404

        if "quantity" in data:
            try:
                quantity = int(data["quantity"])
            except (TypeError, ValueError):
                return jsonify({"error": "quantity must be an integer."}), 400
            if quantity < 0:
                return jsonify({"error": "quantity must be 0 or greater."}), 400
            item.quantity = quantity

        if "department" in data:
            if not str(data["department"]).strip():
                return jsonify({"error": "department cannot be empty."}), 400
            item.department = data["department"]

        if "location" in data:
            if not str(data["location"]).strip():
                return jsonify({"error": "location cannot be empty."}), 400
            item.location = data["location"]

        repo.update(item)
        logger.info("Updated item '%s' via PATCH /items/%s", item.name, name)
        return jsonify(item.to_dict())

    @app.patch("/items/<path:name>/status")
    def update_item_status(name):
        data = request.get_json(silent=True) or {}
        status = data.get("status")

        if status not in {"lost", "in_repair"}:
            return jsonify({"error": "Status must be 'lost' or 'in_repair'."}), 400

        try:
            if status == "lost":
                item = service.mark_lost(name)
            else:
                item = service.mark_in_repair(name)
        except ValueError as exc:
            logger.exception("API failed to update status for item '%s'", name)
            return jsonify({"error": str(exc)}), 404

        return jsonify(item.to_dict())

    @app.delete("/items/<path:name>")
    def delete_item(name):
        item = repo.get_by_name(name)
        if not item:
            return jsonify({"error": "Item not found."}), 404

        repo.delete(name)
        logger.info("Deleted item '%s'", name)
        return jsonify({"message": f"Item '{name}' deleted successfully."})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
