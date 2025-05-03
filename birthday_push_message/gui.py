import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from .database import add_birthday, edit_birthday, delete_birthday, get_birthdays
from datetime import datetime
from .push_notification import send_push_message
from .config import API_KEY

def refresh_table(tree):
    """Refresh the table with the current database records."""
    for row in tree.get_children():
        tree.delete(row)
    for record in sorted(get_birthdays(), key=lambda x: (int(x[2].split('.')[1]), int(x[2].split('.')[0]))):
        tree.insert("", "end", values=record)
    style_rows(tree)

# Apply alternating row colors
def style_rows(tree):
    for i, row in enumerate(tree.get_children()):
        if i % 2 == 0:
            tree.item(row, tags=("even",))
        else:
            tree.item(row, tags=("odd",))

def validate_date_format(date):
    """Validate the date format (dd.mm.yyyy) and allow placeholder year 999."""
    try:
        if date.endswith(".999"):
            datetime.strptime(date.replace(".999", ".0999"), "%d.%m.%Y")
        else:
            datetime.strptime(date, "%d.%m.%Y")
        return True
    except ValueError:
        return False

def refresh_listbox(listbox):
    """Refresh the listbox with the current database records."""
    listbox.delete(0, tk.END)
    for record in get_birthdays():
        listbox.insert(tk.END, f"{record[0]}: {record[1]} - {record[2]} ({record[3]} years old)")

def add_record(name_entry, date_entry, age_entry, tree):
    """Add a new record to the database."""
    name = name_entry.get()
    date = date_entry.get()
    age = age_entry.get()
    if not validate_date_format(date):
        messagebox.showerror("Error", "Date must be in the format dd.mm.yyyy!")
        return
    if name and date and age:
        add_birthday(name, date, int(age))
        refresh_table(tree)
        messagebox.showinfo("Success", "Record added successfully!")
    else:
        messagebox.showerror("Error", "All fields are required!")

# Global variable to track the previous selection
previous_selection = None

def on_record_select(event, name_entry, date_entry, age_entry, tree):
    global previous_selection

    # Get the current selection
    current_selection = tree.selection()

    # Check if the selection is empty (deselection)
    if not current_selection:
        print("Deselection occurred")
        previous_selection = None
        return

    # Check if the selection has changed
    if current_selection != previous_selection:
        print("Selection occurred")
        previous_selection = current_selection

        # Populate the input fields with the selected record
        selected_item = current_selection[0]
        values = tree.item(selected_item, "values")
        record_id, name, date, age = values

        name_entry.delete(0, tk.END)
        name_entry.insert(0, name)

        date_entry.delete(0, tk.END)
        date_entry.insert(0, date)

        age_entry.delete(0, tk.END)
        age_entry.insert(0, age)

def edit_record(name_entry, date_entry, age_entry, tree):
    """Edit the selected record in the database."""
    try:
        selected_item = tree.selection()
        if not selected_item:
            print("E2")
            raise IndexError("No record selected!")

        selected_item = selected_item[0]  # Get the first selected item
        record_id = tree.item(selected_item, "values")[0]
        name = name_entry.get()
        date = date_entry.get()
        age = age_entry.get()

        if not validate_date_format(date):
            messagebox.showerror("Error", "Date must be in the format dd.mm.yyyy!")
            return

        if name and date and age:
            edit_birthday(record_id, name, date, int(age))
            refresh_table(tree)
            messagebox.showinfo("Success", "Record updated successfully!")
        else:
            messagebox.showerror("Error", "All fields are required!")
    except IndexError:
        print("E3")
        messagebox.showerror("Error", "No record selected!")

def delete_record(tree):
    """Delete the selected record from the database."""
    try:
        selected_item = tree.selection()[0]  # Get selected item
        record_id = tree.item(selected_item, "values")[0]
        delete_birthday(record_id)
        refresh_table(tree)
        messagebox.showinfo("Success", "Record deleted successfully!")
    except IndexError:
        print("E4")
        messagebox.showerror("Error", "No record selected!")

def notify_now(api_key, listbox):
    """Send a push message immediately if there is a birthday today."""
    today = datetime.now().strftime("%d.%m.")  # Only day and month are needed
    birthdays = get_birthdays()
    found = False
    for birthday in birthdays:
        name, date, age = birthday[1], birthday[2], birthday[3]
        # Extract day and month from the stored date
        stored_day_month = ".".join(date.split(".")[:2]) + "."
        if stored_day_month == today:  # Compare only day and month
            send_push_message(api_key, "Birthday Reminder", f"Today is {name}'s {age}th birthday!")
            found = True
    if not found:
        messagebox.showinfo("Notification", "No birthdays today.")

def open_edit_window(tree):
    """Open a new window to edit the selected record."""
    try:
        selected_item = tree.selection()[0]  # Get selected item
        values = tree.item(selected_item, "values")
        record_id, current_name, current_date, current_age = values

        # Create a new window
        edit_window = tk.Toplevel()
        edit_window.title("Edit Record")

        # Name field
        tk.Label(edit_window, text="Name:").grid(row=0, column=0, sticky="w")
        name_entry = tk.Entry(edit_window)
        name_entry.grid(row=0, column=1, sticky="ew")
        name_entry.insert(0, current_name)

        # Date field
        tk.Label(edit_window, text="Date (dd.mm.yyyy):").grid(row=1, column=0, sticky="w")
        date_entry = tk.Entry(edit_window)
        date_entry.grid(row=1, column=1, sticky="ew")
        date_entry.insert(0, current_date)

        # Age field
        tk.Label(edit_window, text="Age:").grid(row=2, column=0, sticky="w")
        age_entry = tk.Entry(edit_window)
        age_entry.grid(row=2, column=1, sticky="ew")
        age_entry.insert(0, current_age)

        def save_changes():
            """Save the updated data to the database."""
            updated_name = name_entry.get()
            updated_date = date_entry.get()
            updated_age = age_entry.get()

            if not validate_date_format(updated_date):
                messagebox.showerror("Error", "Date must be in the format dd.mm.yyyy!")
                return

            if updated_name and updated_date and updated_age:
                edit_birthday(record_id, updated_name, updated_date, int(updated_age))
                refresh_table(tree)
                edit_window.destroy()
                messagebox.showinfo("Success", "Record updated successfully!")
            else:
                messagebox.showerror("Error", "All fields are required!")

        # Save button
        tk.Button(edit_window, text="Save", command=save_changes).grid(row=3, column=0, columnspan=2)

    except IndexError:
        print("E5")
        messagebox.showerror("Error", "No record selected!")

def create_gui():
    """Create the GUI for managing the database."""
    root = tk.Tk()
    root.title("Birthday Manager")

    # Configure grid weights for rescaling
    root.rowconfigure(3, weight=1)
    root.columnconfigure(0, weight=1)

    # Input fields
    tk.Label(root, text="Name:").grid(row=0, column=0, sticky="w")
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1, sticky="ew")

    tk.Label(root, text="Date (dd.mm.yyyy):").grid(row=1, column=0, sticky="w")
    date_entry = tk.Entry(root)
    date_entry.grid(row=1, column=1, sticky="ew")

    tk.Label(root, text="Age:").grid(row=2, column=0, sticky="w")
    age_entry = tk.Entry(root)
    age_entry.grid(row=2, column=1, sticky="ew")

    # Table view
    columns = ("ID", "Name", "Date", "Age")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Name", text="Name")
    tree.heading("Date", text="Date")
    tree.heading("Age", text="Age")
    tree.grid(row=3, column=0, columnspan=3, sticky="nsew")

    # Add scrollbar
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=3, column=3, sticky="ns")

    style_rows(tree)

    tree.tag_configure("even", background="white")
    tree.tag_configure("odd", background="lightgrey")

    # Make column names bold
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

    # Ensure the treeview is populated before editing
    refresh_table(tree)

    # Bind the selection event to update input fields
    tree.bind("<<TreeviewSelect>>", lambda event: on_record_select(event, name_entry, date_entry, age_entry, tree))

    # Buttons
    tk.Button(root, text="Add", command=lambda: add_record(name_entry, date_entry, age_entry, tree)).grid(row=4, column=0)
    tk.Button(root, text="Edit", command=lambda: edit_record(name_entry, date_entry, age_entry, tree)).grid(row=4, column=1)
    tk.Button(root, text="Delete", command=lambda: delete_record(tree)).grid(row=4, column=2)
    tk.Button(root, text="Notify Now", command=lambda: notify_now(API_KEY, tree)).grid(row=5, column=0)
    tk.Button(root, text="Exit", command=root.quit).grid(row=5, column=1)

    root.mainloop()
