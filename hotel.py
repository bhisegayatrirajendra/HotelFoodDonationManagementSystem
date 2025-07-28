import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import subprocess

from datetime import datetime

# --- Database connections ---
donation_conn = sqlite3.connect("hotel_food_donation.db")
donation_cursor = donation_conn.cursor()

users_conn = sqlite3.connect("users.db")
users_cursor = users_conn.cursor()

# Create necessary tables if they don't exist
donation_cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        food_name TEXT,
        quantity TEXT,
        document_path TEXT,
        document_id TEXT UNIQUE,
        orphanage_phone TEXT,
        hotel_address TEXT,
        donation_date TEXT,
        status TEXT DEFAULT 'Pending'
    )
""")
donation_conn.commit()

# --- GUI setup ---
root = tk.Tk()
root.title("Hotel - Food Donation Panel")
root.geometry("650x600")
root.configure(bg="#f8f9fa")

frame = tk.Frame(root, padx=20, pady=20, bg="white", relief="ridge", bd=2)
frame.pack(pady=20)

tk.Label(frame, text="Food Donation Form", font=("Arial", 16, "bold"), fg="#333", bg="white").grid(row=0, column=0, columnspan=3, pady=10)

# --- Input Fields ---
labels = [
    "Name of Food:",
    "Quantity:",
    "Food Testing Document:",
    "Document ID (Unique):",
    "Orphanage Phone No:",
    "Hotel Address:",
    "Date of Donation (YYYY-MM-DD):"
]

entries = []

for i, label_text in enumerate(labels):
    tk.Label(frame, text=label_text, font=("Arial", 12), bg="white").grid(row=i+1, column=0, sticky="w", padx=10, pady=5)
    if label_text == "Food Testing Document:":
        entry_document_path = tk.Entry(frame, width=30, font=("Arial", 10))
        entry_document_path.grid(row=i+1, column=1, pady=5, padx=5)
        tk.Button(frame, text="Browse", command=lambda: select_file(entry_document_path), font=("Arial", 10), bg="#007bff", fg="white").grid(row=i+1, column=2, padx=5)
    else:
        entry = tk.Entry(frame, width=35, font=("Arial", 10))
        entry.grid(row=i+1, column=1, pady=5, padx=5)
        entries.append(entry)

# Unpack entries for use
entry_food_name, entry_quantity, entry_document_id, entry_orphanage_phone, entry_hotel_address, entry_date = entries

# --- Functions ---

def select_file(entry_field):
    file_path = filedialog.askopenfilename(title="Select Food Testing Document", filetypes=[("PDF Files", ".pdf"), ("All Files", ".*")])
    entry_field.delete(0, tk.END)
    entry_field.insert(0, file_path)

def clear_fields():
    entry_food_name.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    entry_document_path.delete(0, tk.END)
    entry_document_id.delete(0, tk.END)
    entry_orphanage_phone.delete(0, tk.END)
    entry_hotel_address.delete(0, tk.END)
    entry_date.delete(0, tk.END)

def submit_donation():
    food_name = entry_food_name.get()
    quantity = entry_quantity.get()
    document_path = entry_document_path.get()
    document_id = entry_document_id.get()
    orphanage_phone = entry_orphanage_phone.get()
    hotel_address = entry_hotel_address.get()
    donation_date = entry_date.get()

    # Validation
    if not all([food_name, quantity, document_path, document_id, orphanage_phone, hotel_address, donation_date]):
        messagebox.showerror("Error", "All fields are required!")
        return

    # Check orphanage existence
    users_cursor.execute("""
        SELECT name, address, organization_name FROM users
        WHERE phone = ? AND role = 'Orphanage'
    """, (orphanage_phone,))
    orphanage_data = users_cursor.fetchone()

    if not orphanage_data:
        messagebox.showerror("Error", "No orphanage found with that phone number!")
        return

    orphanage_name, orphanage_address, orphanage_org = orphanage_data

    try:
        donation_cursor.execute('''
            INSERT INTO food_donations (
                food_name, quantity, document_path, document_id,
                orphanage_phone, hotel_address, donation_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (food_name, quantity, document_path, document_id,
              orphanage_phone, hotel_address, donation_date))
        donation_conn.commit()

        messagebox.showinfo("Success", f"Donation submitted to {orphanage_org or orphanage_name} successfully!")
        clear_fields()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Document ID already exists. Use a unique one.")

def open_status_checker():
    win = tk.Toplevel(root)
    win.title("Check Donation Status")
    win.geometry("400x250")
    win.configure(bg="#f8f9fa")

    tk.Label(win, text="Enter Document ID", font=("Arial", 12), bg="#f8f9fa").pack(pady=15)
    doc_entry = tk.Entry(win, font=("Arial", 12), width=30)
    doc_entry.pack(pady=5)

    status_label = tk.Label(win, text="", font=("Arial", 12, "bold"), bg="#f8f9fa", fg="blue")
    status_label.pack(pady=10)

    def check_status():
        doc_id = doc_entry.get().strip()
        if not doc_id:
            messagebox.showerror("Error", "Please enter a Document ID.")
            return

        donation_cursor.execute("SELECT status FROM food_donations WHERE document_id=?", (doc_id,))
        result = donation_cursor.fetchone()

        if result:
            status_label.config(text=f"Status: {result[0]}")
        else:
            messagebox.showerror("Not Found", "No record found for the given Document ID.")

    tk.Button(win, text="Check", font=("Arial", 12), bg="#007bff", fg="white", command=check_status).pack(pady=10)

# --- Buttons ---
tk.Button(frame, text="Submit Donation", command=submit_donation, font=("Arial", 12, "bold"), bg="#28a745", fg="white", width=18).grid(row=9, column=0, pady=20)
tk.Button(frame, text="Check Status", command=open_status_checker, font=("Arial", 12, "bold"), bg="#ffc107", fg="black", width=18).grid(row=9, column=1, pady=20)
def on_closing():
    root.destroy()
    try:
        subprocess.Popen(["python", "homepage.py"])
    except Exception as e:
        print(f"Error launching homepage.py: {e}")

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()