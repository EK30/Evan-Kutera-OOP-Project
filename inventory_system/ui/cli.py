from inventory_system.persistence.sqlite_repository import SQLiteRepository
from inventory_system.core.services.inventory_service import InventoryService
from inventory_system.core.patterns.sorting_strategy import (
    SortByName, SortByQuantity, SortByExpiration
)


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
    print("\nSorting Options:")
    print("1. By Name")
    print("2. By Quantity")
    print("3. By Expiration")
    choice = input("Select: ")

    if choice == "1":
        service.sorter = SortByName()
    elif choice == "2":
        service.sorter = SortByQuantity()
    elif choice == "3":
        service.sorter = SortByExpiration()
    else:
        print("Invalid choice.")


def main():
    repo = SQLiteRepository("inventory.db")
    service = InventoryService(repo)

    print("Welcome to Alfred State's Equipment Tracking System!")

    while True:
        print_menu()
        choice = input("Enter choice: ")

        if choice == "1":
            category = input("Category (general/perishable): ")
            name = input("Item name: ")
            qty = int(input("Quantity: "))
            dept = input("Department: ")
            loc = input("Location (e.g., SET 445): ")

            if category == "perishable":
                exp = input("Expiration date (YYYY-MM-DD): ")
                service.add_item(category, name, qty, department=dept, location=loc, expiration_date=exp)
            else:
                service.add_item(category, name, qty, department=dept, location=loc)

            print("Equipment added!")

        elif choice == "2":
            for item in service.list_items():
                print(item)

        elif choice == "3":
            term = input("Search: ")
            for item in service.search_items(term):
                print(item)

        elif choice == "4":
            name = input("Item name: ")
            user = input("Checked out by: ")
            due = input("Due date (YYYY-MM-DD): ")
            try:
                item = service.check_out_item(name, user, due)
                print(f"Checked out: {item}")
            except Exception as e:
                print(e)

        elif choice == "5":
            name = input("Item name: ")
            try:
                item = service.check_in_item(name)
                print(f"Returned: {item}")
            except Exception as e:
                print(e)

        elif choice == "6":
            name = input("Item name: ")
            service.mark_in_repair(name)
            print("Marked in repair.")

        elif choice == "7":
            name = input("Item name: ")
            service.mark_lost(name)
            print("Marked lost.")

        elif choice == "8":
            dept = input("Department: ")
            for item in service.filter_by_department(dept):
                print(item)

        elif choice == "9":
            loc = input("Location: ")
            for item in service.filter_by_location(loc):
                print(item)

        elif choice == "10":
            overdue = service.get_overdue_items()
            for item in overdue:
                print(item)

        elif choice == "11":
            sorting_menu(service)

        elif choice == "12":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()