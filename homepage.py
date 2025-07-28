import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import hashlib
import subprocess  # To run external Python files
from twilio.rest import Client  # Twilio client for sending SMS
from PIL import Image, ImageTk

# Colors and Fonts
BG_COLOR = "#e3f2fd"
NAV_BG = "#1565c0"
BTN_COLOR = "#0288d1"
TEXT_COLOR = "#333"
ENTRY_BG = "#ffffff"
BTN_TEXT_COLOR = "#ffffff"
HEADER_FONT = ("Arial", 18, "bold")
TEXT_FONT = ("Arial", 12)

# Global variable for logged-in user
logged_in_user = None

# Twilio Credentials (Use your own credentials here)
TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'  # This is the phone number you use to send SMS

# Database Connection Function
def connect_db():
    return sqlite3.connect("users.db")

# Hash function for secure passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize database
try:
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                address TEXT,
                organization_name TEXT
            )
        """)
        conn.commit()
except sqlite3.Error as e:
    print(f"Database Error: {e}")

# Twilio function to send SMS
def send_sms(to_phone_number, message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        messagebox.showinfo("Success", "Message sent successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send message: {e}")

# Main Window
root = tk.Tk()
root.title("Hotel Food Donation Management System")
root.geometry("800x600")
root.configure(bg=BG_COLOR)
root.state("zoomed")  # Maximized window

# Title
tk.Label(root, text="Hotel Food Donation Management System", font=HEADER_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=10)

# Navigation Bar
nav_frame = tk.Frame(root, bg=NAV_BG)
nav_frame.pack(fill=tk.X, pady=5)

# Centered Navigation Buttons
btn_frame = tk.Frame(nav_frame, bg=NAV_BG)
btn_frame.pack(expand=True)

# Content Frame
content_frame = tk.Frame(root, bg=BG_COLOR)
content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

# Function to Switch Pages
def show_page(page):
    for widget in content_frame.winfo_children():
        widget.destroy()

    if page == "Home":
        tk.Label(content_frame, text="Welcome to the Hotel Food Donation Management System!", 
                 font=HEADER_FONT, fg=TEXT_COLOR, bg=BG_COLOR, anchor="center").pack(pady=10)
        
        home_text = """
  The Hotel Food Donation Management System is a user-friendly application developed using  
    Python and Tkinter that aims to bridge the gap between hotels with surplus food and orphanages
or NGOs in need of food donations. The system provides an efficient platform where hotels 
can list available food donations, and orphanages or NGOs can access the details and make 
requests to collect the food.                                                                                                 """
        tk.Label(content_frame, text=home_text, font=TEXT_FONT, fg=TEXT_COLOR, bg=BG_COLOR, 
                 wraplength=700, justify="center", anchor="center").pack(pady=5)
        try:
            food_image = Image.open("fooddonation.webp")  # Replace with your image file name
            food_image = food_image.resize((400, 300))  # Resize the image
            food_image = ImageTk.PhotoImage(food_image)

        # Display image in the Home tab
            image_label = tk.Label(content_frame, image=food_image, bg=BG_COLOR)
            image_label.image = food_image  # Keep reference to avoid garbage collection
            image_label.pack(pady=10)
        except Exception as e:
            tk.Label(content_frame, text="Error loading image!", font=TEXT_FONT, fg="red", bg=BG_COLOR).pack(pady=5)

        system_text = """
This project automates and streamlines the donation process by ensuring that leftover food 
from hotels is effectively utilized, minimizing food wastage and contributing to social welfare. 
Through an intuitive GUI interface, the system simplifies the process of food submission, 
user registration, login, and request tracking.
        """
        tk.Label(content_frame, text=system_text, font=TEXT_FONT, fg=TEXT_COLOR, bg=BG_COLOR, 
                 wraplength=700, justify="center", anchor="center").pack(pady=5)
    elif page == "About Us":
        tk.Label(content_frame, text="About Us", font=HEADER_FONT, fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=10)
        tk.Label(content_frame, text="We help distribute leftover food to orphanages.", fg=TEXT_COLOR, bg=BG_COLOR, font=TEXT_FONT, wraplength=500, justify="center").pack(pady=5)
    elif page == "Contact Us":
        tk.Label(content_frame, text="Contact Us", font=HEADER_FONT, fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=10)
        tk.Label(content_frame, text="Email:abc123@gmail.com", fg=TEXT_COLOR, bg=BG_COLOR, font=TEXT_FONT).pack(pady=5)
        tk.Label(content_frame, text="Phone: +91 1111111111", fg=TEXT_COLOR, bg=BG_COLOR, font=TEXT_FONT).pack(pady=5)

# Logout Function
def logout():
    global logged_in_user
    logged_in_user = None
    update_nav_buttons()
    show_page("Home")

# Update Navigation Buttons Based on Login Status
def update_nav_buttons():
    for widget in btn_frame.winfo_children():
        widget.destroy()

    nav_buttons = [
        ("Home", lambda: show_page("Home")),
        ("About Us", lambda: show_page("About Us")),
        ("Contact Us", lambda: show_page("Contact Us"))
    ]

    if logged_in_user:
        nav_buttons.append(("Logout", logout))
    else:
        nav_buttons.append(("Register", open_register))
        nav_buttons.append(("Login", open_login))

    for text, command in nav_buttons:
        tk.Button(btn_frame, text=text, command=command, bg=BTN_COLOR, fg=BTN_TEXT_COLOR, width=12, font=TEXT_FONT).pack(side=tk.LEFT, padx=10, pady=10)

# Registration Window
def open_register():
    register_window = tk.Toplevel(root)
    register_window.title("Register")
    register_window.geometry("400x450")
    register_window.configure(bg=BG_COLOR)

    tk.Label(register_window, text="Register", fg=TEXT_COLOR, bg=BG_COLOR, font=HEADER_FONT).pack(pady=10)

    fields = [("Name", ""), ("Email", ""), ("Phone", ""), ("Password", "*"), ("Address", ""), ("Organization Name", "")]
    entries = {}

    for label_text, show_char in fields:
        tk.Label(register_window, text=label_text, fg=TEXT_COLOR, bg=BG_COLOR, font=TEXT_FONT).pack(pady=5)
        entry = tk.Entry(register_window, bg=ENTRY_BG, show=show_char)
        entry.pack(pady=5)
        entries[label_text] = entry

    tk.Label(register_window, text="Role:", fg=TEXT_COLOR, bg=BG_COLOR, font=TEXT_FONT).pack(pady=5)
    role_var = tk.StringVar(value="Hotel")  # Default role
    role_dropdown = ttk.Combobox(register_window, textvariable=role_var, values=["Hotel","Orphanage"])
    role_dropdown.pack(pady=5)

    def submit_form():
        name, email, phone, password, address, organization_name, role = (
            entries["Name"].get(), entries["Email"].get(), entries["Phone"].get(), entries["Password"].get(),
            entries["Address"].get(), entries["Organization Name"].get(), role_var.get()
        )

        if not all([name, email, phone, password, role, address, organization_name]):
            messagebox.showerror("Error", "All fields are required!")
            return

        hashed_password = hash_password(password)

        try:
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name, email, phone, password, role, address, organization_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (name, email, phone, hashed_password, role, address, organization_name))
                conn.commit()
            messagebox.showinfo("Success", "Registration Successful!")
            register_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already exists!")

    tk.Button(register_window, text="Submit", command=submit_form, bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 12, "bold"), width=15).pack(pady=15)

# Login Window
def open_login():
    login_window = tk.Toplevel(root)
    login_window.title("Login")
    login_window.geometry("400x300")
    login_window.configure(bg=BG_COLOR)

    tk.Label(login_window, text="Login", fg=TEXT_COLOR, bg=BG_COLOR, font=HEADER_FONT).pack(pady=10)

    tk.Label(login_window, text="Email:", fg=TEXT_COLOR, bg=BG_COLOR, font=TEXT_FONT).pack()
    email_entry = tk.Entry(login_window, bg=ENTRY_BG)
    email_entry.pack()

    tk.Label(login_window, text="Password:", fg=TEXT_COLOR, bg=BG_COLOR, font=TEXT_FONT).pack()
    password_entry = tk.Entry(login_window, show="*", bg=ENTRY_BG)
    password_entry.pack()
    def check_login():
        global logged_in_user
        email, password = email_entry.get(), password_entry.get()
        hashed_password = hash_password(password)

        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, role FROM users WHERE email=? AND password=?", (email, hashed_password))
            user = cursor.fetchone()

        if user:
            logged_in_user = {"id": user[0], "name": user[1], "role": user[2]}
            root.destroy()
            subprocess.run(["python", f"{logged_in_user['role'].lower()}.py"])
        else:
            messagebox.showerror("Error", "Invalid email or password!")

    tk.Button(login_window, text="Login", command=check_login, bg=BTN_COLOR, fg=BTN_TEXT_COLOR, font=("Arial", 12, "bold"), width=15).pack(pady=15)

update_nav_buttons()
show_page("Home")
root.mainloop()