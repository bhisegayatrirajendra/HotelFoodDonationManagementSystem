import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess  # To open homepage.py

class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Panel - Hotel Food Donation System")
        self.root.geometry("1100x550")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Header
        self.header_label = tk.Label(
            self.root,
            text="Admin - Hotel Food Donation Management System",
            font=("Arial", 16, "bold"),
            fg="black",
            bg="#ADD8E6",
            pady=5,
        )
        self.header_label.pack(fill=tk.X)

        # Database connections
        self.conn_users = sqlite3.connect("users.db")
        self.cursor_users = self.conn_users.cursor()

        self.conn_food = sqlite3.connect("hotel_food_donation.db")
        self.cursor_food = self.conn_food.cursor()

        # Tabs
        self.tab_control = ttk.Notebook(self.root)

        # -------------------- Manage Users Tab -------------------- #
        self.user_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.user_tab, text="Manage Users")

        self.user_search_frame = tk.Frame(self.user_tab)
        self.user_search_frame.pack(fill=tk.X, padx=10, pady=5)

        self.user_search_entry = tk.Entry(self.user_search_frame, width=40)
        self.user_search_entry.pack(side=tk.LEFT, padx=5)

        self.user_search_btn = tk.Button(self.user_search_frame, text="Search", command=self.search_user)
        self.user_search_btn.pack(side=tk.LEFT, padx=5)

        self.user_show_all_btn = tk.Button(self.user_search_frame, text="Show All", command=self.load_users)
        self.user_show_all_btn.pack(side=tk.LEFT, padx=5)

        self.user_tree = ttk.Treeview(self.user_tab, columns=("ID", "Name", "Email", "Phone", "Role", "Address", "Organization"), show="headings")
        for col in ("ID", "Name", "Email", "Phone", "Role", "Address", "Organization"):
            self.user_tree.heading(col, text=col)
        self.user_tree.pack(fill=tk.BOTH, expand=True)

        self.delete_user_button = tk.Button(self.user_tab, text="Delete User", command=self.delete_user, bg="red", fg="white")
        self.delete_user_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.update_user_button = tk.Button(self.user_tab, text="Update User", command=self.update_user, bg="green", fg="white")
        self.update_user_button.pack(side=tk.LEFT, padx=10, pady=5)

        # -------------------- Manage Food Donations Tab -------------------- #
        self.food_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.food_tab, text="Manage Food Donations")

        self.food_search_frame = tk.Frame(self.food_tab)
        self.food_search_frame.pack(fill=tk.X, padx=10, pady=5)

        self.food_search_entry = tk.Entry(self.food_search_frame, width=40)
        self.food_search_entry.pack(side=tk.LEFT, padx=5)

        self.food_search_btn = tk.Button(self.food_search_frame, text="Search", command=self.search_food)
        self.food_search_btn.pack(side=tk.LEFT, padx=5)

        self.food_show_all_btn = tk.Button(self.food_search_frame, text="Show All", command=self.load_food_donations)
        self.food_show_all_btn.pack(side=tk.LEFT, padx=5)

        self.food_tree = ttk.Treeview(
            self.food_tab,
            columns=("ID", "Food Name", "Quantity", "Document Path", "Document ID", 
                     "Orphanage Phone", "Hotel Address", "Donation Date", "Status"),
            show="headings"
        )
        for col in self.food_tree["columns"]:
            self.food_tree.heading(col, text=col)
            self.food_tree.column(col, anchor="center", width=120)

        self.food_tree.pack(fill=tk.BOTH, expand=True)

        self.style = ttk.Style()
        self.style.configure("Treeview", foreground="black")

        self.delete_food_button = tk.Button(self.food_tab, text="Delete Food", command=self.delete_food, bg="red", fg="white")
        self.delete_food_button.pack(pady=5)

        self.tab_control.pack(expand=1, fill="both")

        # Initial Data Load
        self.load_users()
        self.load_food_donations()

    def execute_query_users(self, query, params=()):
        try:
            self.cursor_users.execute(query, params)
            self.conn_users.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def execute_query_food(self, query, params=()):
        try:
            self.cursor_food.execute(query, params)
            self.conn_food.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def load_users(self):
        for row in self.user_tree.get_children():
            self.user_tree.delete(row)
        self.cursor_users.execute("SELECT id, name, email, phone, role, address, organization_name FROM users")
        for user in self.cursor_users.fetchall():
            self.user_tree.insert("", tk.END, values=user)

    def search_user(self):
        keyword = self.user_search_entry.get().strip()
        query = """
            SELECT id, name, email, phone, role, address, organization_name FROM users 
            WHERE name LIKE ? OR email LIKE ? OR phone LIKE ? OR role LIKE ? OR address LIKE ? OR organization_name LIKE ?
        """
        params = tuple([f"%{keyword}%"] * 6)
        self.cursor_users.execute(query, params)
        results = self.cursor_users.fetchall()
        self.user_tree.delete(*self.user_tree.get_children())
        for user in results:
            self.user_tree.insert("", tk.END, values=user)

    def delete_user(self):
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a user to delete.")
            return
        user_id = self.user_tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete User ID {user_id}?")
        if confirm:
            self.execute_query_users("DELETE FROM users WHERE id=?", (user_id,))
            self.load_users()

    def update_user(self):
        selected_item = self.user_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a user to update.")
            return
        item_values = self.user_tree.item(selected_item, "values")
        user_id, user_name, user_email, user_phone, user_role, user_address, user_org = item_values
        update_window = tk.Toplevel(self.root)
        update_window.title("Update User")
        update_window.geometry("400x400")
        labels = ["Name:", "Email:", "Phone:", "Role:", "Address:", "Organization Name:"]
        entries = [tk.Entry(update_window) for _ in labels]
        for i, label in enumerate(labels):
            tk.Label(update_window, text=label).pack()
            entries[i].insert(0, item_values[i+1])
            entries[i].pack()
        def save_updated_user():
            new_values = [entry.get() for entry in entries]
            self.execute_query_users("UPDATE users SET name=?, email=?, phone=?, role=?, address=?, organization_name=? WHERE id=?", (*new_values, user_id))
            self.load_users()
            update_window.destroy()
        tk.Button(update_window, text="Save", command=save_updated_user, bg="blue", fg="white").pack(pady=10)

    def load_food_donations(self):
        for row in self.food_tree.get_children():
            self.food_tree.delete(row)
        self.cursor_food.execute("SELECT id, food_name, quantity, document_path, document_id, orphanage_phone, hotel_address, donation_date, status FROM food_donations")
        for food in self.cursor_food.fetchall():
            self.food_tree.insert("", tk.END, values=food)

    def search_food(self):
        keyword = self.food_search_entry.get().strip()
        query = """
            SELECT id, food_name, quantity, document_path, document_id, orphanage_phone, hotel_address, donation_date, status 
            FROM food_donations
            WHERE food_name LIKE ? OR quantity LIKE ? OR document_id LIKE ? OR orphanage_phone LIKE ? OR hotel_address LIKE ? OR status LIKE ?
        """
        params = tuple([f"%{keyword}%"] * 6)
        self.cursor_food.execute(query, params)
        results = self.cursor_food.fetchall()
        self.food_tree.delete(*self.food_tree.get_children())
        for food in results:
            self.food_tree.insert("", tk.END, values=food)

    def delete_food(self):
        selected_item = self.food_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a food donation to delete.")
            return
        food_id = self.food_tree.item(selected_item, "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Food ID {food_id}?")
        if confirm:
            self.execute_query_food("DELETE FROM food_donations WHERE id=?", (food_id,))
            self.load_food_donations()

    def on_closing(self):
        self.conn_users.close()
        self.conn_food.close()
        self.root.destroy()
        subprocess.Popen(["python", "homepage.py"])

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminPanel(root)
    root.mainloop()
