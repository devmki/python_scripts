"""
Module for managing a SQLite database of birthdays.
This module provides functions to initialize the database, add, 
edit, delete, and fetch birthday records.
"""
import sqlite3
from datetime import datetime
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "birthdays.db")

def initialize_database():
    """Initialize the SQLite database and create the birthdays table if it doesn't exist."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS birthdays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            age INTEGER NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()

def add_birthday(name, date, age):
    """Add a new birthday record to the database."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO birthdays (name, date, age) VALUES (?, ?, ?)",
            (name, date, age)
        )
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error adding birthday: {e}")
    finally:
        connection.close()

def edit_birthday(record_id, name, date, age):
    """Edit an existing birthday record in the database."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE birthdays SET name = ?, date = ?, age = ? WHERE id = ?",
            (name, date, age, record_id)
        )
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error editing birthday: {e}")
    finally:
        connection.close()

def delete_birthday(record_id):
    """Delete a birthday record from the database."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM birthdays WHERE id = ?", (record_id,))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error deleting birthday: {e}")
    finally:
        connection.close()

def delete_birthday_v2(name, date):
    """Delete a birthday record from the database by name and date."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM birthdays WHERE name = ? AND date = ?", (name, date))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error deleting birthday: {e}")
    finally:
        connection.close()

def get_birthdays():
    """Fetch all birthday records from the database."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM birthdays")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching birthdays: {e}")
        return []
    finally:
        connection.close()

def import_birthdays_from_csv(file_path):
    """Read birthdays from a CSV file and add them to the database."""
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                day = row['Day'].zfill(2)
                month = row['Month'].zfill(2)
                year = row['Year'] if row['Year'] else '0999'
                name = row['Name']
                date = f"{day}.{month}.{year}"
                age = -1 if year == '0999' else datetime.now().year - int(year)
                add_birthday(name, date, age)
    except (FileNotFoundError, KeyError) as e:
        print(f"Error reading CSV file: {e}")

def update_age_if_birthday():
    """Update the age of persons in the database if today is their birthday."""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        today = datetime.now().strftime("%d.%m")
        cursor.execute("SELECT id, date FROM birthdays")
        records = cursor.fetchall()
        for record_id, date in records:
            day_month, year = date[:5], date[6:]
            if day_month == today:
                new_age = -1 if year == '0999' else datetime.now().year - int(year)
                cursor.execute("UPDATE birthdays SET age = ? WHERE id = ?", (new_age, record_id))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error updating ages: {e}")
    finally:
        connection.close()
