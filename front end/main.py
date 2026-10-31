import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from admin import show_admin_panel

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

# Main window
root = tk.Tk()
root.title("Python Vending Machine")
root.geometry("800x750")
root.configure(bg="#3B3838")
root.resizable(True,True)


title = tk.Label(
    root,
    text="VENDING MACHINE",
    font=("Arial", 20, "bold"),
    bg="#3B3838",
    fg="#00e676"

)
def show_category(category):
    global current_category
    current_category = category
    refresh_products()
#nav bar
nav_frame = tk.Frame(root, bg="#20242b")
nav_frame.pack(fill="x", padx=10, pady=5)

tk.Button(
    nav_frame,
    text="All Products",
    command=lambda: show_category("All Products")
).pack(side="left", padx=5)

tk.Button(
    nav_frame,
    text="Snacks",
    command=lambda: show_category("Snacks")
).pack(side="left", padx=5)

tk.Button(
    nav_frame,
    text="Beverages",
    command=lambda: show_category("Beverages")
).pack(side="left", padx=5)

# Product display
product_frame = tk.Frame(root, bg="#20242b")
product_frame.pack(pady=10)

status_label = tk.Label(
    root,
    text="Select a product",
    font=("Arial", 11),
    bg="#20242b",
    fg="white"
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
        text=f"{name} - ₱{item['price']:.2f} | Stock: {item['stock']}"
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
            width=125,
            height=150,
            font=("Arial", 10, "bold"),
            bg="#303640",
            fg="white",
            activebackground="#00c853",
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

def show_admin_login():
    login_window = tk.Toplevel(root)
    login_window.title("Admin Login")
    login_window.geometry("300x250")
    login_window.configure(bg="#20242b")
    login_window.resizable(False, False)

    tk.Label(
        login_window,
        text="ADMIN LOGIN",
        font=("Arial", 18, "bold"),
        bg="#20242b",
        fg="#00e676"
    ).pack(pady=15)

    tk.Label(
        login_window,
        text="Username:",
        bg="#20242b",
        fg="white"
    ).pack()

    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)

    tk.Label(
        login_window,
        text="Password:",
        bg="#20242b",
        fg="white"
    ).pack()

    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    def login():
        username = username_entry.get()
        password = password_entry.get()

        if username == "admin123" and password == "102007":
            # Hide the login window first so the admin panel appears cleanly,
            # then close it after the panel is created.
            login_window.withdraw()
            show_admin_panel(
                root,
                products,
                transactions,
                refresh_products,
                lambda: total,
                lambda: balance_label.config(
                    text=f"Total Sales: ₱{total:.2f}"
                )
            )
            login_window.destroy()
        else:
            messagebox.showerror(
                "Login Failed",
                "Incorrect username or password."
            )

    tk.Button(
        login_window,
        text="LOGIN",
        command=login,
        bg="#00c853",
        fg="white",
        width=15
    ).pack(pady=15)


# Payment section
payment_label = tk.Label(
    root,
    text="Enter Payment (₱):",
    font=("Arial", 11),
    bg="#3B3838",
    fg="white"
)
payment_label.pack(pady=(10, 5))

payment_entry = tk.Entry(
    root,
    font=("Arial", 14),
    justify="center"
)
payment_entry.pack(pady=5)

buy_button = tk.Button(
    root,
    text="BUY NOW",
    font=("Arial", 13, "bold"),
    bg="#00c853",
    fg="white",
    width=20,
    command=buy_product
)
buy_button.pack(pady=10)

# Admin button
admin_button = tk.Button(
    root,
    text="ADMINISTRATOR PANEL",
    font=("Arial", 11, "bold"),
    bg="#303640",
    fg="white",
    width=20,
    command=show_admin_login
)
admin_button.pack(pady=5)

refresh_products()

# Start the application
root.mainloop()
