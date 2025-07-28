import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
import subprocess
import sys

# Get orphanage phone number
if len(sys.argv) >= 2:
    orphanage_phone = sys.argv[1]
else:
    # Prompt user for orphanage phone
    root_prompt = tk.Tk()
    root_prompt.withdraw()  # Hide the root window
    orphanage_phone = simpledialog.askstring("Orphanage Login", "Enter your phone number:")
    if not orphanage_phone:
        messagebox.showerror("Error", "Phone number is required!")
        sys.exit(1)

# DB Connection
conn = sqlite3.connect("hotel_food_donation.db")
cursor = conn.cursor()

# GUI setup
root = tk.Tk()
root.title(f"Orphanage Panel - {orphanage_phone}")
root.geometry("900x400")

tk.Label(root, text="Available Food Donations Requests", font=("Arial", 14, "bold")).pack(pady=10)
frame = tk.Frame(root, bd=2, relief="solid")
frame.pack(pady=10, padx=10, fill="both", expand=True)

tree = ttk.Treeview(frame, columns=("ID", "Food", "Quantity", "Document ID", "Document Path", "Hotel", "Status", "Date"), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)

scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tree.pack(pady=2, padx=2, fill="both", expand=True)

# Load pending donations
def load_donations():
    tree.delete(*tree.get_children())
    cursor.execute("""
        SELECT id, food_name, quantity, document_id, document_path, hotel_address, status, donation_date
        FROM food_donations
        WHERE status='Pending' AND orphanage_phone=?
    """, (orphanage_phone,))
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

# Update donation status
def update_status(accepted=True):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Select a donation to update!")
        return
    donation_id = tree.item(selected_item[0], "values")[0]
    new_status = "Accepted" if accepted else "Rejected"
    cursor.execute("UPDATE food_donations SET status=? WHERE id=?", (new_status, donation_id))
    conn.commit()
    messagebox.showinfo("Success", f"Donation {new_status} successfully!")
    load_donations()

# Open document
def open_document():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Select a donation to open the document!")
        return
    document_path = tree.item(selected_item[0], "values")[4]
    if not os.path.exists(document_path):
        messagebox.showerror("Error", "Document file not found!")
        return
    try:
        if os.name == 'nt':
            os.startfile(document_path)
        else:
            subprocess.run(["xdg-open", document_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open document: {e}")

# View past donation history
def view_past_requests():
    past_window = tk.Toplevel(root)
    past_window.title("Past Donation Requests")
    past_window.geometry("900x400")
    tk.Label(past_window, text="Past Donation Requests", font=("Arial", 14, "bold")).pack(pady=10)
    frame_past = tk.Frame(past_window, bd=2, relief="solid")
    frame_past.pack(pady=10, padx=10, fill="both", expand=True)

    tree_past = ttk.Treeview(frame_past, columns=tree["columns"], show="headings")
    for col in tree["columns"]:
        tree_past.heading(col, text=col)

    scrollbar_past = ttk.Scrollbar(frame_past, orient="vertical", command=tree_past.yview)
    tree_past.configure(yscrollcommand=scrollbar_past.set)
    scrollbar_past.pack(side="right", fill="y")
    tree_past.pack(pady=2, padx=2, fill="both", expand=True)

    cursor.execute("""
        SELECT id, food_name, quantity, document_id, document_path, hotel_address, status, donation_date
        FROM food_donations
        WHERE status IN ('Accepted', 'Rejected') AND orphanage_phone=?
    """, (orphanage_phone,))
    for row in cursor.fetchall():
        tree_past.insert("", "end", values=row)

    def open_past_document():
        selected_item = tree_past.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a donation to open the document!")
            return
        document_path = tree_past.item(selected_item[0], "values")[4]
        if not os.path.exists(document_path):
            messagebox.showerror("Error", "Document file not found!")
            return
        try:
            if os.name == 'nt':
                os.startfile(document_path)
            else:
                subprocess.run(["xdg-open", document_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {e}")

    tk.Button(past_window, text="View Document", command=open_past_document, font=("Arial", 12), bg="blue", fg="white").pack(pady=5)

# Buttons
tk.Button(root, text="Accept", command=lambda: update_status(True), font=("Arial", 12), bg="green", fg="white").pack(pady=5, side="left", padx=20)
tk.Button(root, text="Reject", command=lambda: update_status(False), font=("Arial", 12), bg="red", fg="white").pack(pady=5, side="left", padx=20)
tk.Button(root, text="View Document", command=open_document, font=("Arial", 12), bg="blue", fg="white").pack(pady=5, side="left", padx=20)
tk.Button(root, text="View All Requests", command=view_past_requests, font=("Arial", 12), bg="#17a2b8", fg="white").pack(pady=5, side="right", padx=20)

# Handle close event and navigate to homepage.py
def on_closing():
    root.destroy()
    try:
        subprocess.Popen(["python", "homepage.py"])
    except Exception as e:
        print(f"Error launching homepage.py: {e}")

root.protocol("WM_DELETE_WINDOW", on_closing)

# Load data
load_donations()
root.mainloop()
