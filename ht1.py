import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
from datetime import datetime

# Database Connection
conn = sqlite3.connect("hotel_food_donation.db")
cursor = conn.cursor()

# Drop and recreate tables to apply changes (optional if schema changes)
cursor.execute("DROP TABLE IF EXISTS food_requests")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hotel_name TEXT,
        hotel_address TEXT,
        food_name TEXT,
        document TEXT,
        reference_id TEXT UNIQUE,
        donation_date TEXT,
        status TEXT DEFAULT 'Pending'
    )
""")

cursor.execute('''
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
''')
conn.commit()

# Function to select food testing document
def select_file():
    file_path = filedialog.askopenfilename(title="Select Food Testing Document", filetypes=[("PDF Files", ".pdf"), ("All Files", ".*")])
    entry_document_path.delete(0, tk.END)
    entry_document_path.insert(0, file_path)

# Function to submit donation request
def submit_data():
    food_name = entry_food_name.get()
    quantity = entry_quantity.get()
    document_path = entry_document_path.get()
    document_id = entry_document_id.get()
    orphanage_phone = entry_orphanage_phone.get()
    hotel_address = entry_hotel_address.get()
    donation_date = entry_date.get()
    
    if not (food_name and quantity and document_path and document_id and orphanage_phone and hotel_address and donation_date):
        messagebox.showerror("Error", "All fields are required!")
        return
    
    try:
        cursor.execute('''
            INSERT INTO food_donations (food_name, quantity, document_path, document_id, orphanage_phone, hotel_address, donation_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (food_name, quantity, document_path, document_id, orphanage_phone, hotel_address, donation_date))
        conn.commit()

        cursor.execute('''
            INSERT INTO food_requests (hotel_name, hotel_address, food_name, document, reference_id, donation_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("Hotel", hotel_address, food_name, document_path, document_id, donation_date))
        conn.commit()

        messagebox.showinfo("Success", "Food donation details submitted successfully!")
        clear_fields()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Duplicate document ID detected. Please use a unique document ID.")

# Function to check donation status in a new window
def open_status_page():
    status_window = tk.Toplevel(root)
    status_window.title("Check Donation Status")
    status_window.geometry("400x250")

    tk.Label(status_window, text="Enter Document ID:", font=("Arial", 12)).pack(pady=10)
    
    entry_status_id = tk.Entry(status_window, width=30, font=("Arial", 12))
    entry_status_id.pack(pady=5)

    lbl_status = tk.Label(status_window, text="", font=("Arial", 12, "bold"), fg="blue")
    lbl_status.pack(pady=10)

    def check_status():
        document_id = entry_status_id.get()
        if not document_id:
            messagebox.showerror("Error", "Enter the Document ID!")
            return
        
        cursor.execute("SELECT status FROM food_donations WHERE document_id=?", (document_id,))
        result = cursor.fetchone()
        
        if result:
            lbl_status.config(text=f"Status: {result[0]}")
        else:
            messagebox.showerror("Error", "No record found for the provided Document ID.")

    tk.Button(status_window, text="Submit", command=check_status, font=("Arial", 12), bg="#007bff", fg="white").pack(pady=10)

# Function to clear input fields
def clear_fields():
    entry_food_name.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    entry_document_path.delete(0, tk.END)
    entry_document_id.delete(0, tk.END)
    entry_orphanage_phone.delete(0, tk.END)
    entry_hotel_address.delete(0, tk.END)
    entry_date.delete(0, tk.END)

# Function to open homepage.py when window is closed
def on_close():
    root.destroy()
    os.system("python homepage.py")

# GUI Layout for Food Donation
root = tk.Tk()
root.title("Hotel Food Donation System")
root.geometry("600x600")
root.configure(bg="#f8f9fa")
root.protocol("WM_DELETE_WINDOW", on_close)

frame = tk.Frame(root, padx=20, pady=20, bg="white", relief="ridge", bd=2)
frame.pack(pady=20)

tk.Label(frame, text="Food Donation Form", font=("Arial", 16, "bold"), fg="#333", bg="white").grid(row=0, column=0, columnspan=3, pady=10)

labels = ["Name of Food:", "Quantity:", "Food Testing Document:", "ID of Document:", "Orphanage Phone No:", "Hotel Address:", "Date of Donation (YYYY-MM-DD):"]
entries = []

for i, label in enumerate(labels):
    tk.Label(frame, text=label, font=("Arial", 12), bg="white").grid(row=i+1, column=0, sticky="w", padx=10, pady=5)
    if label == "Food Testing Document:":
        entry_document_path = tk.Entry(frame, width=30, font=("Arial", 10))
        entry_document_path.grid(row=i+1, column=1, pady=5, padx=5)
        tk.Button(frame, text="Browse", command=select_file, font=("Arial", 10), bg="#007bff", fg="white").grid(row=i+1, column=2, padx=5)
    else:
        entry = tk.Entry(frame, width=35, font=("Arial", 10))
        entry.grid(row=i+1, column=1, pady=5, padx=5)
        entries.append(entry)

entry_food_name, entry_quantity, entry_document_id, entry_orphanage_phone, entry_hotel_address, entry_date = entries

tk.Button(frame, text="Submit", command=submit_data, font=("Arial", 12, "bold"), bg="#28a745", fg="white", width=15).grid(row=9, column=0, pady=15)
tk.Button(frame, text="Check Status", command=open_status_page, font=("Arial", 12, "bold"), bg="#ffc107", fg="black", width=15).grid(row=9, column=1, pady=15)

root.mainloop()