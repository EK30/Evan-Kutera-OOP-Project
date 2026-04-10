from datetime import datetime
from pathlib import Path

from inventory_system.persistence.sqlite_repository import SQLiteRepository
from inventory_system.persistence.init import initialize_database
from inventory_system.core.services.inventory_service import InventoryService
from inventory_system.core.patterns.sorting_strategy import (
    SortByName, SortByQuantity, SortByExpiration
)
from inventory_system.logs.init import setup_logging


def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def print_menu():
    print("\n===== Alfred State Equipment Tracking =====")
    print("1. Add Equipment")
    print("2. List All Equipment")
    print("3. Search Equipment")
    print("4. Check Out Equipment")
    print("5. Check In Equipment")
    print("6. Mark as In Repair")
    print("7. Mark as Lost")
    print("8. Filter by Department")
    print("9. Filter by Location")
    print("10. View Overdue Equipment")
    print("11. Change Sorting Method")
    print("12. Exit")
    print("==========================================")


def sorting_menu(service):
    # Lets the user switch sorting behavior at runtime.
    print("\nSorting Options:")
    print("1. By Name")
    print("2. By Quantity")
    print("3. By Expiration")
    choice = input("Select: ").strip()

    if choice == "1":
        service.sorter = SortByName()
    elif choice == "2":
        service.sorter = SortByQuantity()
    elif choice == "3":
        service.sorter = SortByExpiration()
    else:
        print("Invalid choice.")


def main():
    # Create the database connection and service once when the program starts.
    logger = setup_logging()
    db_path = Path(__file__).resolve().parents[2] / "inventory.db"
    initialize_database(str(db_path))
    repo = SQLiteRepository(str(db_path))
    service = InventoryService(repo)
    logger.info("Inventory system started")

    print("Welcome to Alfred State's Equipment Tracking System!")

    try:
        while True:
            print_menu()
            choice = input("Enter choice: ").strip()
            valid_choices = {str(i) for i in range(1, 13)}
            if choice not in valid_choices:
                logger.warning("User entered invalid menu option: %s", choice)
                print("Invalid option. Please choose 1-12.")
                continue

            # Each menu option maps to one inventory action.
            if choice == "1":
                category = input("Category (general/perishable): ").strip().lower()
                if category not in {"general", "perishable"}:
                    print("Category must be 'general' or 'perishable'.")
                    continue

                name = input("Item name: ").strip()
                if not name:
                    print("Item name cannot be empty.")
                    continue

                try:
                    qty = int(input("Quantity: ").strip())
                except ValueError:
                    print("Quantity must be a whole number.")
                    continue
                if qty < 0:
                    print("Quantity cannot be negative.")
                    continue

                dept = input("Department: ").strip() or "General"
                loc = input("Location (e.g., SET 445): ").strip() or "Unknown"

                if category == "perishable":
                    exp = input("Expiration date (YYYY-MM-DD): ").strip()
                    if not is_valid_date(exp):
                        print("Expiration date must be in YYYY-MM-DD format.")
                        continue
                    try:
                        service.add_item(category, name, qty, department=dept, location=loc, expiration_date=exp)
                    except Exception as e:
                        logger.exception("Error while adding perishable item '%s'", name)
                        print(e)
                        continue
                else:
                    try:
                        service.add_item(category, name, qty, department=dept, location=loc)
                    except Exception as e:
                        logger.exception("Error while adding item '%s'", name)
                        print(e)
                        continue

                print("Equipment added!")

            elif choice == "2":
                for item in service.list_items():
                    print(item)

            elif choice == "3":
                term = input("Search: ").strip()
                if not term:
                    print("Search term cannot be empty.")
                    continue
                for item in service.search_items(term):
                    print(item)

            elif choice == "4":
                name = input("Item name: ").strip()
                user = input("Checked out by: ").strip()
                due = input("Due date (YYYY-MM-DD): ").strip()

                if not name:
                    print("Item name cannot be empty.")
                    continue
                if not user:
                    print("Checked out by cannot be empty.")
                    continue
                if not is_valid_date(due):
                    print("Due date must be in YYYY-MM-DD format.")
                    continue

                try:
                    item = service.check_out_item(name, user, due)
                    print(f"Checked out: {item}")
                except Exception as e:
                    logger.exception("Error while checking out item '%s'", name)
                    print(e)

            elif choice == "5":
                name = input("Item name: ").strip()
                if not name:
                    print("Item name cannot be empty.")
                    continue
                try:
                    item = service.check_in_item(name)
                    print(f"Returned: {item}")
                except Exception as e:
                    logger.exception("Error while checking in item '%s'", name)
                    print(e)

            elif choice == "6":
                name = input("Item name: ").strip()
                if not name:
                    print("Item name cannot be empty.")
                    continue
                try:
                    service.mark_in_repair(name)
                    print("Marked in repair.")
                except Exception as e:
                    logger.exception("Error while marking item '%s' in repair", name)
                    print(e)

            elif choice == "7":
                name = input("Item name: ").strip()
                if not name:
                    print("Item name cannot be empty.")
                    continue
                try:
                    service.mark_lost(name)
                    print("Marked lost.")
                except Exception as e:
                    logger.exception("Error while marking item '%s' as lost", name)
                    print(e)

            elif choice == "8":
                dept = input("Department: ").strip()
                if not dept:
                    print("Department cannot be empty.")
                    continue
                for item in service.filter_by_department(dept):
                    print(item)

            elif choice == "9":
                loc = input("Location: ").strip()
                if not loc:
                    print("Location cannot be empty.")
                    continue
                for item in service.filter_by_location(loc):
                    print(item)

            elif choice == "10":
                overdue = service.get_overdue_items()
                for item in overdue:
                    print(item)

            elif choice == "11":
                sorting_menu(service)

            elif choice == "12":
                logger.info("Inventory system closed by user")
                print("Goodbye!")
                break
    finally:
        repo.close()


if __name__ == "__main__":
    main()
