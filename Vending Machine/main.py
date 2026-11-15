import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import math
import sqlite3
from pathlib import Path

import admin
import database

transaction_history = []

products = {
    "Piattos": {
        "price": 20,
        "stock": 50,
        "image": "images/piattos.jpg"
    },
    "Nova": {
        "price": 20,
        "stock": 50,
        "image": "images/nova.jpg"
    },
    "Pillows": {
        "price": 12,
        "stock": 50,
        "image": "images/pillows.jpg"
    },
    "Fita": {
        "price": 10,
        "stock": 50,
        "image": "images/Fita.jpg"
    },
    "Rebisco": {
        "price": 10,
        "stock": 50,
        "image": "images/rebi.jpg"
    },
    "Clover": {
        "price": 12,
        "stock": 50,
        "image": "images/clover.jpg"
    },
    "C2 Apple": {
        "price": 20,
        "stock": 50,
        "image": "images/c2.jpg"
    },
    "Chuckie": {
        "price": 15,
        "stock": 50,
        "image": "images/chuckie.jpg"
    },
    "Water": {
        "price": 15,
        "stock": 50,
        "image": "images/water.jpg"
    }
}

MAX_CHANGE = 500
total = 0
selected_product = None

# Color palette
BG_COLOR = "#000000"
CARD_COLOR = "#1A1A1A"
PRIMARY_COLOR = "#E50920"
SECONDARY_COLOR = "#8B0015"
HIGHLIGHT_COLOR = "#8B0015"
TEXT_COLOR = "#FFFFFF"
SECONDARY_TEXT_COLOR = "#B3B3B3"
BORDER_COLOR = "#333333"
WHITE = "#FFFFFF"

# Main window
root = tk.Tk()
root.title("Python Vending Machine")
root.geometry("800x720")
root.configure(bg=BG_COLOR)
root.resizable(True, True)

root.total_sales = 0
root.starting_current_money = 500
root.available_change = MAX_CHANGE

try:
    database.initialize_database(products)
    products.clear()
    products.update(database.get_products())
    transaction_history.extend(database.get_transaction_history())
    machine_state = database.get_machine_state()
    root.total_sales = machine_state["total_sales"]
    root.starting_current_money = machine_state["cash_balance"]
    root.available_change = machine_state["available_change"]
except sqlite3.Error as error:
    messagebox.showerror(
        "Database Error",
        f"The vending machine database could not be opened:\n{error}",
        parent=root
    )
    root.destroy()
    raise

header_frame = tk.Frame(root, bg=BG_COLOR)
header_frame.pack(pady=10)

logo_image = Image.open(
    Path(__file__).resolve().parent.parent / "images" / "logo.jpg"
)
logo_image = logo_image.resize((120, 90))
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(header_frame, image=logo_photo, bg=BG_COLOR)
logo_label.image = logo_photo
logo_label.pack(side="left", padx=(0, 12))

title = tk.Label(
    header_frame,
    text="VENDING MACHINE",
    font=("Arial", 20, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
title.pack(side="left")

# Product display
product_frame = tk.Frame(root, bg=BG_COLOR)
product_frame.pack(pady=10)

status_label = tk.Label(
    root,
    text="Select a product",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
status_label.pack(pady=5)


def select_product(name):
    global selected_product

    item = products[name]

    if item.get("archived", False):
        status_label.config(text=f"{name} is unavailable.")
        return

    if item["stock"] <= 0:
        status_label.config(text=f"{name} is out of stock!")
        return

    selected_product = name
    status_label.config(
        text=f"{name} - ₱{item['price']} | Stock: {item['stock']}"
    )


def buy_product():
    global total, selected_product

    if selected_product is None:
        messagebox.showwarning(
            "No Product",
            "Please select a product first."
        )
        return

    item = products[selected_product]

    if item.get("archived", False):
        messagebox.showerror(
            "Unavailable Product",
            "This product is unavailable."
        )
        selected_product = None
        refresh_products()
        return

    if item["stock"] <= 0:
        messagebox.showerror(
            "Out of Stock",
            "This product is unavailable."
        )
        return

    try:
        payment = float(payment_entry.get())
    except ValueError:
        messagebox.showerror(
            "Invalid Payment",
            "Please enter a valid amount."
        )
        return

    if not math.isfinite(payment):
        messagebox.showerror(
            "Invalid Payment",
            "Please enter a valid amount."
        )
        return

    if payment < 0:
        messagebox.showerror(
            "Invalid Payment",
            "Payment cannot be negative."
        )
        return

    if payment < item["price"]:
        messagebox.showwarning(
            "Insufficient Payment",
            f"You need ₱{item['price'] - payment:.2f} more."
        )
        return

    change = payment - item["price"]
    if change > root.available_change:
        messagebox.showwarning(
            "Insufficient Change",
            f"The machine can only provide ₱{root.available_change:.2f} in change."
        )
        return

    try:
        purchase = database.complete_sale(selected_product, payment)
    except ValueError as error:
        messagebox.showwarning("Purchase Unavailable", str(error))
        try:
            stored_products = database.get_products()
        except sqlite3.Error as database_error:
            messagebox.showerror(
                "Database Error",
                f"Could not refresh product stock:\n{database_error}"
            )
            return
        products.clear()
        products.update(stored_products)
        refresh_products()
        return
    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"The purchase could not be saved:\n{error}"
        )
        return

    try:
        stored_products = database.get_products()
        stored_transactions = database.get_transaction_history()
        machine_state = database.get_machine_state()
    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            "The purchase was saved, but the latest machine data could not "
            f"be loaded:\n{error}\nPlease restart the application before "
            "making another purchase."
        )
        payment_entry.delete(0, tk.END)
        selected_product = None
        return

    products.clear()
    products.update(stored_products)
    transaction_history[:] = stored_transactions
    root.total_sales = machine_state["total_sales"]
    root.starting_current_money = machine_state["cash_balance"]
    root.available_change = machine_state["available_change"]
    total += purchase["total"]

    messagebox.showinfo(
        "Purchase Successful",
        f"Product: {purchase['product']}\n"
        f"Price: ₱{purchase['total']:.2f}\n"
        f"Payment: ₱{purchase['payment']:.2f}\n"
        f"Change: ₱{purchase['change']:.2f}"
    )

    payment_entry.delete(0, tk.END)
    selected_product = None
    refresh_products()
    status_label.config(text="Select another product")


def refresh_products():
    for widget in product_frame.winfo_children():
        widget.destroy()

    visible_index = 0
    for name, item in products.items():
        if item.get("archived", False):
            continue

        stock_text = (
            f"Stock: {item['stock']}"
            if item["stock"] > 0
            else "OUT OF STOCK"
        )

        try:
            image = Image.open(item["image"])
            image = image.resize((70, 70))
            photo = ImageTk.PhotoImage(image)
        except (FileNotFoundError, OSError):
            photo = None

        button = tk.Button(
            product_frame,
            text=f"{name}\n₱{item['price']}\n{stock_text}",
            image=photo,
            compound="top",
            width=120,
            height=130,
            font=("Arial", 10, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            activebackground=PRIMARY_COLOR,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=PRIMARY_COLOR,
            command=lambda n=name: select_product(n),
            state="normal" if item["stock"] > 0 else "disabled"
        )

        button.image = photo
        button.grid(
            row=visible_index // 4,
            column=visible_index % 4,
            padx=5,
            pady=5
        )
        visible_index += 1


def show_admin_panel():
    login_window = tk.Toplevel(root)
    login_window.title("Admin Login")
    login_window.geometry("300x250")
    login_window.configure(bg=BG_COLOR)
    login_window.resizable(False, False)

    tk.Label(
        login_window,
        text="ADMIN LOGIN",
        font=("Arial", 18, "bold"),
        bg=BG_COLOR,
        fg=PRIMARY_COLOR
    ).pack(pady=15)

    tk.Label(
        login_window,
        text="Username:",
        bg=BG_COLOR,
        fg=SECONDARY_TEXT_COLOR
    ).pack()

    username_entry = tk.Entry(
        login_window,
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        highlightcolor=PRIMARY_COLOR
    )
    username_entry.pack(pady=5)

    tk.Label(
        login_window,
        text="Password:",
        bg=BG_COLOR,
        fg=SECONDARY_TEXT_COLOR
    ).pack()

    password_entry = tk.Entry(
        login_window,
        show="*",
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        highlightcolor=PRIMARY_COLOR
    )
    password_entry.pack(pady=5)

    def login():
        username = username_entry.get()
        password = password_entry.get()

        if username == "admin123" and password == "102007":
            login_window.destroy()
            admin.show_admin_panel(
                root,
                transaction_history,
                products,
                refresh_products
            )
        else:
            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password."
            )

    tk.Button(
        login_window,
        text="LOGIN",
        command=login,
        bg=PRIMARY_COLOR,
        fg=WHITE,
        activebackground=SECONDARY_COLOR,
        activeforeground=WHITE,
        width=15,
        relief="flat",
        bd=0
    ).pack(pady=15)


# Payment section
payment_label = tk.Label(
    root,
    text="Enter Payment (₱):",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
payment_label.pack(pady=(10, 5))

payment_entry = tk.Entry(
    root,
    font=("Arial", 14),
    justify="center",
    bg=CARD_COLOR,
    fg=TEXT_COLOR,
    insertbackground=TEXT_COLOR,
    highlightthickness=1,
    highlightbackground=BORDER_COLOR,
    highlightcolor=PRIMARY_COLOR
)
payment_entry.pack(pady=5)

buy_button = tk.Button(
    root,
    text="BUY NOW",
    font=("Arial", 13, "bold"),
    bg=PRIMARY_COLOR,
    fg=WHITE,
    activebackground=SECONDARY_COLOR,
    activeforeground=WHITE,
    width=20,
    relief="flat",
    bd=0,
    command=buy_product
)
buy_button.pack(pady=10)

# Admin button
admin_button = tk.Button(
    root,
    text="ADMIN CONTROLS",
    font=("Arial", 11, "bold"),
    bg=PRIMARY_COLOR,
    fg=WHITE,
    activebackground=SECONDARY_COLOR,
    activeforeground=WHITE,
    width=20,
    relief="flat",
    bd=0,
    command=show_admin_panel
)
admin_button.pack(pady=5)

refresh_products()

# Start the application
root.mainloop()