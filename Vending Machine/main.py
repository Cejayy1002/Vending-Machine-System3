
import tkinter as tk
import admin
from tkinter import messagebox
from PIL import Image, ImageTk
import admin
from datetime import datetime

transaction_history = []


products = {
    "Onion Rings": {
        "price": 11, "stock": 50,
        "image": "images/oni.jpg"
    },
    "Potato Chips": {
        "price": 15, "stock": 50,
        "image": "images/potato.jpg"
    },
    "Criss-Cross": {
        "price": 12, "stock": 50,
        "image": "images/criss.jpg"
    },
    "Inihaw na Bangus": {
        "price": 13, "stock": 50,
        "image": "images/bangus.jpg"
    },
    "Martys": {
        "price": 10, "stock": 50,
        "image": "images/martys.jpg"
    },
    "Mang Juan": {
        "price": 10, "stock": 50,
        "image": "images/mang_juan.jpg"
    }
}

MAX_PAYMENT = 500
total = 0
selected_product = None

# Color palette
BG_COLOR = "#E8EDF4"
CARD_COLOR = "#F1F4F8"
PRIMARY_COLOR = "#426A9E"
HIGHLIGHT_COLOR = "#83A9D1"
TEXT_COLOR = "#34445A"
WHITE = "#FFFFFF"

# Main window
root = tk.Tk()
root.title("Python Vending Machine")
root.geometry("800x720")
root.configure(bg=BG_COLOR)
root.resizable(True, True)



title = tk.Label(
    root,
    text="VENDING MACHINE",
    font=("Arial", 20, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
title.pack(pady=15)


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

    if payment < 0:
        messagebox.showerror(
            "Invalid Payment",
            "Payment cannot be negative."
        )
        return

    if payment > MAX_PAYMENT:
        messagebox.showerror(
            "Exceeded Payment Limit",
            f"Machine doesnt have enough balance for change."
        )
        return

    if payment < item["price"]:
        messagebox.showwarning(
            "Insufficient Payment",
            f"You need ₱{item['price'] - payment:.2f} more."
        )
        return

    change = payment - item["price"]
    item["stock"] -= 1
    total += item["price"]
    transaction_history.append({
        "id": len(transaction_history) + 1,
        "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "products": selected_product,
        "quantity": 1,
        "total": item["price"],
        "amount_paid": payment,
        "change": change
    })



    messagebox.showinfo(
        "Purchase Successful",
        f"Product: {selected_product}\n"
        f"Price: ₱{item['price']:.2f}\n"
        f"Payment: ₱{payment:.2f}\n"
        f"Change: ₱{change:.2f}"
    )


    payment_entry.delete(0, tk.END)
    selected_product = None
    refresh_products()
    status_label.config(text="Select another product")


def refresh_products():
    for widget in product_frame.winfo_children():
        widget.destroy()

    for index, (name, item) in enumerate(products.items()):
        stock_text = (
            f"Stock: {item['stock']}"
            if item["stock"] > 0
            else "OUT OF STOCK"
        )

        try:
            image = Image.open(item["image"])
            image = image.resize((100, 100))
            photo = ImageTk.PhotoImage(image)
        except (FileNotFoundError, OSError):
            photo = None

        button = tk.Button(
            product_frame,
            text=f"{name}\n₱{item['price']}\n{stock_text}",
            image=photo,
            compound="top",
            width=140,
            height=160,
            font=("Arial", 10, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            activebackground=HIGHLIGHT_COLOR,
            activeforeground=WHITE,
            relief="flat",
            command=lambda n=name: select_product(n),
            state="normal" if item["stock"] > 0 else "disabled"
        )

        # Keep the image reference
        button.image = photo

        button.grid(
            row=index // 3,
            column=index % 3,
            padx=5,
            pady=5
        )


# Admin panel window

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
        fg=TEXT_COLOR
    ).pack()

    username_entry = tk.Entry(
        login_window,
        bg=CARD_COLOR,
        fg=TEXT_COLOR
    )
    username_entry.pack(pady=5)

    tk.Label(
        login_window,
        text="Password:",
        bg=BG_COLOR,
        fg=TEXT_COLOR
    ).pack()

    password_entry = tk.Entry(
        login_window,
        show="*",
        bg=CARD_COLOR,
        fg=TEXT_COLOR
    )
    password_entry.pack(pady=5)

    def login():
        username = username_entry.get()
        password = password_entry.get()

        if username == "admin123" and password == "102007":
            login_window.destroy()
            admin.show_admin_panel(root, transaction_history)
            

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
        activebackground=HIGHLIGHT_COLOR,
        activeforeground=WHITE,
        width=15,
        relief="flat"
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
    fg=TEXT_COLOR
)
payment_entry.pack(pady=5)

buy_button = tk.Button(
    root,
    text="BUY NOW",
    font=("Arial", 13, "bold"),
    bg=PRIMARY_COLOR,
    fg=WHITE,
    activebackground=HIGHLIGHT_COLOR,
    activeforeground=WHITE,
    width=20,
    relief="flat",
    command=buy_product
)
buy_button.pack(pady=10)

# Admin button
admin_button = tk.Button(
    root,
    text="ADMIN CONTROLS",
    font=("Arial", 11, "bold"),
    bg=TEXT_COLOR,
    fg=WHITE,
    activebackground=PRIMARY_COLOR,
    activeforeground=WHITE,
    width=20,
    relief="flat",
    command=show_admin_panel
)
admin_button.pack(pady=5)

refresh_products()

# Start the application
root.mainloop()
