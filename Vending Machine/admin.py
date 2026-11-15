import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from pathlib import Path
import math
import sqlite3
from PIL import Image

import database


def show_admin_panel(parent, transaction_history, products=None, refresh_products=None):

    if products is None:
        products = {}

    admin = tk.Toplevel(parent)
    admin.title("Vending Machine - Admin Panel")
    admin.geometry("950x600")
    # Colors
    BG_COLOR = "#000000"
    CARD_COLOR = "#1A1A1A"
    PRIMARY_COLOR = "#E50920"
    SECONDARY_COLOR = "#8B0015"
    TEXT_COLOR = "#FFFFFF"
    SECONDARY_TEXT_COLOR = "#B3B3B3"
    BORDER_COLOR = "#333333"
    admin.configure(bg=BG_COLOR)

    def reload_database_state():
        try:
            stored_products = database.get_products()
            machine_state = database.get_machine_state()
            stored_transactions = database.get_transaction_history()
        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Could not load vending machine data:\n{error}",
                parent=admin
            )
            return False

        products.clear()
        products.update(stored_products)
        transaction_history[:] = stored_transactions
        parent.total_sales = machine_state["total_sales"]
        parent.starting_current_money = machine_state["cash_balance"]
        parent.available_change = machine_state["available_change"]
        return True

    style = ttk.Style(admin)
    style.theme_use("clam")
    style.configure(
        "RedRoses.TNotebook",
        background=BG_COLOR,
        borderwidth=0
    )
    style.configure(
        "RedRoses.TNotebook.Tab",
        background=CARD_COLOR,
        foreground=SECONDARY_TEXT_COLOR,
        padding=(12, 6),
        borderwidth=1
    )
    style.map(
        "RedRoses.TNotebook.Tab",
        background=[("selected", PRIMARY_COLOR), ("active", SECONDARY_COLOR)],
        foreground=[("selected", TEXT_COLOR), ("active", TEXT_COLOR)]
    )
    style.configure(
        "RedRoses.Treeview",
        background=CARD_COLOR,
        foreground=TEXT_COLOR,
        fieldbackground=CARD_COLOR,
        bordercolor=BORDER_COLOR,
        rowheight=26
    )
    style.map(
        "RedRoses.Treeview",
        background=[("selected", PRIMARY_COLOR)],
        foreground=[("selected", TEXT_COLOR)]
    )
    style.configure(
        "RedRoses.Treeview.Heading",
        background=SECONDARY_COLOR,
        foreground=TEXT_COLOR,
        bordercolor=BORDER_COLOR,
        relief="flat"
    )
    style.map(
        "RedRoses.Treeview.Heading",
        background=[("active", PRIMARY_COLOR)]
    )
    style.configure(
        "RedRoses.Vertical.TScrollbar",
        background=CARD_COLOR,
        troughcolor=BG_COLOR,
        bordercolor=BORDER_COLOR,
        arrowcolor=TEXT_COLOR
    )

    # Main title
    tk.Label(
        admin,
        text="ADMIN PANEL",
        font=("Arial", 22, "bold"),
        bg=BG_COLOR,
        fg=PRIMARY_COLOR
    ).pack(pady=15)

    # Tabs
    notebook = ttk.Notebook(admin, style="RedRoses.TNotebook")
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    history_tab = tk.Frame(notebook, bg=BG_COLOR)

    notebook.add(history_tab, text="Transaction History")

    product_tab = tk.Frame(notebook, bg=BG_COLOR)
    notebook.add(product_tab, text="Product Management")

    product_filter = tk.StringVar(value="Active Products")
    filter_frame = tk.Frame(product_tab, bg=BG_COLOR)
    filter_frame.pack(fill="x", padx=15, pady=(15, 0))

    tk.Label(
        filter_frame,
        text="View:",
        bg=BG_COLOR,
        fg=SECONDARY_TEXT_COLOR
    ).pack(side="left", padx=(0, 8))

    product_filter_menu = ttk.Combobox(
        filter_frame,
        textvariable=product_filter,
        values=("Active Products", "Archived Products", "All Products"),
        state="readonly",
        width=18
    )
    product_filter_menu.pack(side="left")

    product_table = ttk.Treeview(
        product_tab,
        columns=("Product Name", "Price", "Stock", "Status"),
        show="headings",
        style="RedRoses.Treeview"
    )
    product_table.heading("Product Name", text="Product Name")
    product_table.heading("Price", text="Price")
    product_table.heading("Stock", text="Stock")
    product_table.heading("Status", text="Status")
    product_table.column("Product Name", width=220, anchor="center")
    product_table.column("Price", width=140, anchor="center")
    product_table.column("Stock", width=120, anchor="center")
    product_table.column("Status", width=140, anchor="center")
    product_table.pack(fill="both", expand=True, padx=15, pady=(10, 10))

    def refresh_product_table():
        for row in product_table.get_children():
            product_table.delete(row)

        for name, item in products.items():
            archived = item.get("archived", False)
            if product_filter.get() == "Active Products" and archived:
                continue
            if product_filter.get() == "Archived Products" and not archived:
                continue

            product_table.insert("", "end", values=(
                name,
                f"₱{item['price']:.2f}",
                item["stock"],
                "Archived" if archived else "Active"
            ))

    product_filter_menu.bind(
        "<<ComboboxSelected>>",
        lambda event: refresh_product_table()
    )

    def selected_product_name():
        selected = product_table.selection()
        if not selected:
            messagebox.showwarning(
                "No Product Selected",
                "Please select a product first.",
                parent=admin
            )
            return None
        return product_table.item(selected[0], "values")[0]

    def add_stock():
        name = selected_product_name()
        if name is None:
            return

        quantity = simpledialog.askinteger(
            "Add Stock",
            f"How many units of {name} do you want to add?",
            parent=admin,
            minvalue=1
        )

        if quantity is None:
            return

        if quantity <= 0:
            messagebox.showerror(
                "Invalid Quantity",
                "Stock quantity must be greater than zero.",
                parent=admin
            )
            return

        try:
            database.update_product_stock(name, quantity)
        except ValueError as error:
            messagebox.showerror("Stock Update Failed", str(error), parent=admin)
            return
        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Could not update stock:\n{error}",
                parent=admin
            )
            return

        if not reload_database_state():
            return
        refresh_product_table()

        if refresh_products is not None:
            refresh_products()

        messagebox.showinfo(
            "Stock Updated",
            f"{quantity} item(s) were added to {name}.",
            parent=admin
        )

    def edit_price():
        name = selected_product_name()
        if name is None:
            return

        new_price = simpledialog.askfloat(
            "Edit Price",
            f"Enter a new price for {name}:",
            parent=admin,
            minvalue=0.01
        )

        if new_price is None:
            return

        if not math.isfinite(new_price):
            messagebox.showerror(
                "Invalid Price",
                "Please enter a valid price.",
                parent=admin
            )
            return

        if new_price <= 0:
            messagebox.showerror(
                "Invalid Price",
                "Price must be greater than zero.",
                parent=admin
            )
            return

        try:
            database.update_product_price(name, new_price)
        except ValueError as error:
            messagebox.showerror("Price Update Failed", str(error), parent=admin)
            return
        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Could not update the price:\n{error}",
                parent=admin
            )
            return

        if not reload_database_state():
            return
        refresh_product_table()

        if refresh_products is not None:
            refresh_products()

        messagebox.showinfo(
            "Price Updated",
            f"The price of {name} was changed to ₱{new_price:.2f}.",
            parent=admin
        )

    def add_product():
        add_window = tk.Toplevel(admin)
        add_window.title("Add Product")
        add_window.geometry("430x300")
        add_window.configure(bg=BG_COLOR)
        add_window.resizable(False, False)
        add_window.transient(admin)
        add_window.grab_set()

        fields = {}
        for row, label_text in enumerate(
            ("Product Name:", "Product Price:", "Initial Stock:", "Image Path:")
        ):
            tk.Label(
                add_window,
                text=label_text,
                bg=BG_COLOR,
                fg=SECONDARY_TEXT_COLOR
            ).grid(row=row, column=0, sticky="w", padx=15, pady=10)

            entry = tk.Entry(
                add_window,
                bg=CARD_COLOR,
                fg=TEXT_COLOR,
                insertbackground=TEXT_COLOR,
                highlightthickness=1,
                highlightbackground=BORDER_COLOR,
                highlightcolor=PRIMARY_COLOR,
                width=30
            )
            entry.grid(row=row, column=1, padx=10, pady=10)
            fields[label_text] = entry

        def browse_image():
            image_path = filedialog.askopenfilename(
                parent=add_window,
                title="Select Product Image",
                filetypes=(("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),)
            )
            if image_path:
                fields["Image Path:"].delete(0, tk.END)
                fields["Image Path:"].insert(0, image_path)

        tk.Button(
            add_window,
            text="Browse",
            command=browse_image,
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            activebackground=SECONDARY_COLOR,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=0
        ).grid(row=3, column=2, padx=(0, 10))

        def save_product():
            name = fields["Product Name:"].get().strip()
            if not name:
                messagebox.showerror(
                    "Invalid Product",
                    "Product name cannot be empty.",
                    parent=add_window
                )
                return

            if any(existing_name.casefold() == name.casefold()
                   for existing_name in products):
                messagebox.showerror(
                    "Duplicate Product",
                    "A product with this name already exists.",
                    parent=add_window
                )
                return

            try:
                price = float(fields["Product Price:"].get().strip())
            except ValueError:
                messagebox.showerror(
                    "Invalid Price",
                    "Enter a valid product price.",
                    parent=add_window
                )
                return

            if not math.isfinite(price) or price <= 0:
                messagebox.showerror(
                    "Invalid Price",
                    "Product price must be greater than zero.",
                    parent=add_window
                )
                return

            try:
                stock = int(fields["Initial Stock:"].get().strip())
            except ValueError:
                messagebox.showerror(
                    "Invalid Stock",
                    "Initial stock must be a whole number of zero or more.",
                    parent=add_window
                )
                return

            if stock < 0:
                messagebox.showerror(
                    "Invalid Stock",
                    "Initial stock cannot be negative.",
                    parent=add_window
                )
                return

            image_value = fields["Image Path:"].get().strip()
            if not image_value:
                messagebox.showerror(
                    "Invalid Image",
                    "Please enter or select a product image path.",
                    parent=add_window
                )
                return

            image_path = Path(image_value).expanduser()
            if not image_path.is_absolute():
                image_path = Path(__file__).resolve().parent.parent / image_path
            if not image_path.is_file():
                messagebox.showerror(
                    "Invalid Image",
                    "The selected image file does not exist.",
                    parent=add_window
                )
                return

            try:
                with Image.open(image_path) as product_image:
                    product_image.verify()
            except (OSError, SyntaxError, ValueError):
                messagebox.showerror(
                    "Invalid Image",
                    "The selected file is not a valid image.",
                    parent=add_window
                )
                return

            try:
                database.add_product(
                    name,
                    price,
                    stock,
                    str(image_path.resolve())
                )
            except sqlite3.IntegrityError:
                messagebox.showerror(
                    "Duplicate Product",
                    "A product with this name already exists.",
                    parent=add_window
                )
                return
            except (ValueError, sqlite3.Error) as error:
                messagebox.showerror(
                    "Database Error",
                    f"Could not add the product:\n{error}",
                    parent=add_window
                )
                return

            if not reload_database_state():
                return
            product_filter.set("Active Products")
            refresh_product_table()
            if refresh_products is not None:
                refresh_products()
            add_window.destroy()
            messagebox.showinfo(
                "Product Added",
                f"{name} was added successfully.",
                parent=admin
            )

        tk.Button(
            add_window,
            text="Add Product",
            command=save_product,
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            activebackground=SECONDARY_COLOR,
            activeforeground=TEXT_COLOR,
            relief="flat",
            bd=0,
            width=15
        ).grid(row=4, column=0, columnspan=3, pady=12)

    def archive_product():
        name = selected_product_name()
        if name is None:
            return

        if products[name].get("archived", False):
            messagebox.showwarning(
                "Product Archived",
                f"{name} is already archived.",
                parent=admin
            )
            return

        if not messagebox.askyesno(
            "Archive Product",
            f"Archive {name}? It will no longer be available to customers.",
            parent=admin
        ):
            return

        try:
            database.set_product_archived(name, True)
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror(
                "Database Error",
                f"Could not archive the product:\n{error}",
                parent=admin
            )
            return

        if not reload_database_state():
            return
        refresh_product_table()
        if refresh_products is not None:
            refresh_products()

    def restore_product():
        name = selected_product_name()
        if name is None:
            return

        if not products[name].get("archived", False):
            messagebox.showwarning(
                "Active Product",
                f"{name} is already active.",
                parent=admin
            )
            return

        try:
            database.set_product_archived(name, False)
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror(
                "Database Error",
                f"Could not restore the product:\n{error}",
                parent=admin
            )
            return

        if not reload_database_state():
            return
        refresh_product_table()
        if refresh_products is not None:
            refresh_products()

    button_frame = tk.Frame(product_tab, bg=BG_COLOR)
    button_frame.pack(pady=(0, 15))

    tk.Button(
        button_frame,
        text="Add Product",
        command=add_product,
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        activebackground=SECONDARY_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        bd=0,
        width=15
    ).pack(side="left", padx=(0, 10))

    tk.Button(
        button_frame,
        text="Add Stock",
        command=add_stock,
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        activebackground=SECONDARY_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        bd=0,
        width=15
    ).pack(side="left", padx=(0, 10))

    tk.Button(
        button_frame,
        text="Edit Price",
        command=edit_price,
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        activebackground=SECONDARY_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        bd=0,
        width=15
    ).pack(side="left", padx=(0, 10))

    tk.Button(
        button_frame,
        text="Archive Product",
        command=archive_product,
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        activebackground=SECONDARY_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        bd=0,
        width=15
    ).pack(side="left", padx=(0, 10))

    tk.Button(
        button_frame,
        text="Restore Product",
        command=restore_product,
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        activebackground=SECONDARY_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        bd=0,
        width=15
    ).pack(side="left")

    refresh_product_table()

    # =================================
    # TRANSACTION HISTORY
    # =================================

    summary_frame = tk.Frame(history_tab, bg=BG_COLOR)
    summary_frame.pack(fill="x", padx=15, pady=(10, 0))

    total_sales_label = tk.Label(
        summary_frame,
        font=("Arial", 13, "bold"),
        bg=BG_COLOR,
        fg=SECONDARY_TEXT_COLOR
    )
    total_sales_label.pack(side="left", padx=(0, 30))

    current_money_label = tk.Label(
        summary_frame,
        font=("Arial", 13, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )
    current_money_label.pack(side="left", padx=(0, 20))

    available_change_label = tk.Label(
        summary_frame,
        font=("Arial", 13, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )
    available_change_label.pack(side="left")

    history_columns = (
        "Transaction ID",
        "Date and Time",
        "Transaction Type",
        "Amount",
        "Purchased Products",
        "Quantity",
        "Amount Paid",
        "Change Received"
    )

    table_frame = tk.Frame(history_tab, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, padx=15, pady=10)

    table = ttk.Treeview(
        table_frame,
        columns=history_columns,
        show="headings",
        style="RedRoses.Treeview"
    )
    for column in history_columns:
        table.heading(column, text=column)

    table.column("Transaction ID", width=90, anchor="center")
    table.column("Date and Time", width=150, anchor="center")
    table.column("Transaction Type", width=110, anchor="center")
    table.column("Amount", width=100, anchor="e")
    table.column("Purchased Products", width=190)
    table.column("Quantity", width=70, anchor="center")
    table.column("Amount Paid", width=110, anchor="e")
    table.column("Change Received", width=110, anchor="e")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview,
        style="RedRoses.Vertical.TScrollbar"
    )
    horizontal_scrollbar = ttk.Scrollbar(
        table_frame,
        orient="horizontal",
        command=table.xview
    )
    table.configure(
        yscrollcommand=scrollbar.set,
        xscrollcommand=horizontal_scrollbar.set
    )
    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    horizontal_scrollbar.pack(side="bottom", fill="x")

    def refresh_transactions():
        if not reload_database_state():
            return

        for row in table.get_children():
            table.delete(row)

        for transaction in transaction_history:
            transaction_type = transaction.get("type", "Sale")
            amount = transaction.get("amount", transaction.get("total", 0))
            if transaction_type in ("Deposit", "Withdrawal"):
                values = (
                    transaction["id"],
                    transaction["date_time"],
                    transaction_type,
                    f"₱{amount:.2f}",
                    "",
                    "",
                    "",
                    ""
                )
            else:
                values = (
                    transaction["id"],
                    transaction["date_time"],
                    transaction_type,
                    f"₱{amount:.2f}",
                    transaction.get("products", ""),
                    transaction.get("quantity", ""),
                    f"₱{transaction.get('amount_paid', 0):.2f}",
                    f"₱{transaction.get('change', 0):.2f}"
                )
            table.insert("", "end", values=values)

    def update_summary():
        total_sales_label.config(text=f"Total Sales: ₱{parent.total_sales:.2f}")
        current_money_label.config(
            text=f"Current Machine Money: ₱{parent.starting_current_money:.2f}"
        )

        available_change_label.config(
            text=f"Available Change: ₱{parent.available_change:.2f}"
        )

    def refresh_summary():
        update_summary()
        admin.after(1000, refresh_summary)

    tk.Button(
        history_tab,
        text="Refresh",
        command=refresh_transactions,
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        activebackground=SECONDARY_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        bd=0
    ).pack(pady=(0, 10))

    def record_cash_transaction(transaction_type, amount):
        try:
            database.record_cash_transaction(transaction_type, amount)
        except ValueError as error:
            messagebox.showerror(
                f"{transaction_type} Failed",
                str(error),
                parent=admin
            )
            return False
        except sqlite3.Error as error:
            messagebox.showerror(
                "Database Error",
                f"Could not save the transaction:\n{error}",
                parent=admin
            )
            return False

        if not reload_database_state():
            return False
        refresh_transactions()
        update_summary()
        return True

    def deposit_cash():
        amount = simpledialog.askfloat(
            "Deposit",
            "How much would you like to deposit?",
            parent=admin,
            minvalue=0.01
        )

        if amount is None:
            return

        if not math.isfinite(amount) or amount <= 0:
            messagebox.showerror(
                "Invalid Amount",
                "Enter a valid positive deposit amount.",
                parent=admin
            )
            return

        if not messagebox.askyesno(
            "Confirm Deposit",
            f"Deposit ₱{amount:.2f}?",
            parent=admin
        ):
            return

        if not record_cash_transaction("Deposit", amount):
            return
        messagebox.showinfo(
            "Deposit Successful",
            f"₱{amount:.2f} was deposited successfully.",
            parent=admin
        )

    def withdraw_profit(root):
        amount = simpledialog.askfloat(
            "Withdraw",
            "How much would you like to withdraw?",
            parent=admin,
            minvalue=0.01
        )

        if amount is None:
            return

        if not math.isfinite(amount) or amount <= 0:
            messagebox.showerror(
                "Invalid Amount",
                "Enter a valid positive withdrawal amount.",
                parent=admin
            )
            return

        if not messagebox.askyesno(
            "Confirm Withdrawal",
            f"Withdraw ₱{amount:.2f}?",
            parent=admin
        ):
            return

        if not record_cash_transaction("Withdrawal", amount):
            return
        messagebox.showinfo(
            "Withdrawal Successful",
            f"₱{amount:.2f} was withdrawn successfully.",
            parent=admin
        )

    tk.Button(
        history_tab,
        text="Deposit",
        command=deposit_cash,
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        activebackground=SECONDARY_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        bd=0
    ).pack(pady=(0, 10))

    tk.Button(
        history_tab,
        text="Withdraw",
        command=lambda: withdraw_profit(parent),
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        activebackground=SECONDARY_COLOR,
        activeforeground=TEXT_COLOR,
        relief="flat",
        bd=0
    ).pack(pady=(0, 10))

    refresh_transactions()
    refresh_summary()