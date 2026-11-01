
import tkinter as tk
from tkinter import messagebox

products = {
    "Onion Rings": {
        "price": 11, "stock": 10,
        "image": "images/oni.jpg",
        "category": "Snacks"
    },
    "Potato Chips": {
        "price": 15, "stock": 10,
        "image": "images/potato.jpg",
        "category": "Snacks"
    },
    "Criss-Cross": {
        "price": 12, "stock": 10,
        "image": "images/criss.jpg",
        "category": "Snacks"
    },
    "Inihaw na Bangus": {
        "price": 13, "stock": 10,
        "image": "images/bangus.jpg",
        "category": "Snacks"
    },
    "Martys": {
        "price": 10, "stock": 10,
        "image": "images/martys.jpg",
        "category": "Snacks"
    },
    "Mang Juan": {
        "price": 10, "stock": 10,
        "image": "images/mang_juan.jpg",
        "category": "Snacks"
    },
    "Coca-Cola": {
        "price": 20, "stock": 10,
        "image": "images/coke.jpg",
        "category": "Drinks"
    },
    "Water": {
        "price": 15, "stock": 10,
        "image": "images/water.jpg",
        "category": "Drinks"
    },
    "C2": {
        "price": 18, "stock": 10,
        "image": "images/c2.jpg",
        "category": "Drinks"
    },
}

current_category = "All Products"
transactions = []
MAX_PAYMENT = 500
selected_product = []


def select_product(name, status_label):
    global selected_product

    item = products[name]

    if item["stock"] <= 0:
        status_label.config(text=f"{name} is out of stock!")
        return

    selected_product = name
    status_label.config(
        text=f"{name} - ₱{item['price']:.2f} | Stock: {item['stock']}"
    )


def buy_product(payment_entry, status_label, refresh_products):
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
            f"Maximum payment allowed is ₱{MAX_PAYMENT}."
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

    transactions.append({
        "product": selected_product,
        "price": item["price"],
        "payment": payment,
        "change": change,
        "quantity": 1,
        "time": __import__("datetime").datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
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
