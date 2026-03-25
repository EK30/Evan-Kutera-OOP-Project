from flask import Flask, jsonify, request

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

    def serialize_items(items):
        return [item.to_dict() for item in items]

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok"})

    @app.get("/items")
    def get_items():
        department = request.args.get("department")
        location = request.args.get("location")
        search = request.args.get("search")
        overdue = request.args.get("overdue")

        if overdue and overdue.lower() == "true":
            return jsonify(serialize_items(service.get_overdue_items()))
        if department:
            return jsonify(serialize_items(service.filter_by_department(department)))
        if location:
            return jsonify(serialize_items(service.filter_by_location(location)))
        if search:
            return jsonify(serialize_items(service.search_items(search)))

        return jsonify(serialize_items(service.list_items()))

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

        try:
            item = service.add_item(
                data["category"],
                data["name"],
                int(data["quantity"]),
                department=data.get("department", "General"),
                location=data.get("location", "Unknown"),
                expiration_date=data.get("expiration_date"),
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

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
