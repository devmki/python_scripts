"""
Main entry point for the Birthday Push Message application.
This script initializes the database, handles command-line arguments for various tasks
such as updating ages, sending notifications, adding or deleting birthdays, and starting the GUI.
"""
import argparse
from .database import (initialize_database, update_age_if_birthday,
                      add_birthday, delete_birthday_v2)
from .gui import create_gui
from.scheduler import check_and_send_birthdays
from .config import API_KEY

def main():
    """Main entry point for the application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Birthday Manager")
    parser.add_argument("--update", action="store_true", help="Update ages for today's birthdays")
    parser.add_argument("--notify", action="store_true", help="Send birthday notifications")
    parser.add_argument("--add", nargs=3, type=str, help="add new birthday to the database "\
                                                         "(name,date,age)")
    parser.add_argument("--delete", nargs=2, type=str, help="Delete a birthday from the database "\
                                                            "(name,date)")
    parser.add_argument("--gui", action="store_true", help="Start the GUI application")
    args = parser.parse_args()

    # Initialize the database
    initialize_database()

    # Handle tasks based on arguments
    if args.update:
        update_age_if_birthday()

    elif args.notify:
        check_and_send_birthdays(API_KEY)

    elif args.add:
        name = args.add[0]
        date = args.add[1]
        age  = args.add[2]
        add_birthday(name,date,age)

    elif args.delete:
        name = args.delete[0]
        date = args.delete[1]
        delete_birthday_v2(name, date)

    else:
        create_gui()

if __name__ == "__main__":
    main()
