import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


def show_admin_panel(parent, transaction_history):

    admin = tk.Toplevel(parent)
    admin.title("Vending Machine - Admin Panel")
    admin.geometry("950x600")
    admin.configure(bg="#E8EDF4")
    

    # Colors
    BG_COLOR = "#E8EDF4"
    CARD_COLOR = "#FFFFFF"
    PRIMARY_COLOR = "#0C7A5A"
    TEXT_COLOR = "#222222"

    # Main title
    tk.Label(
        admin,
        text="ADMIN PANEL",
        font=("Arial", 22, "bold"),
        bg=BG_COLOR,
        fg=PRIMARY_COLOR
    ).pack(pady=15)

    # Tabs
    notebook = ttk.Notebook(admin)
    notebook.pack(fill="both", expand=True, padx=20, pady=10)

    history_tab = tk.Frame(notebook, bg=BG_COLOR)

    notebook.add(history_tab, text="Transaction History")
    # =================================
    # TRANSACTION HISTORY
    # =================================

    history_columns = (
        "Transaction ID",
        "Date and Time",
        "Purchased Products",
        "Quantity",
        "Total Amount",
        "Amount Paid",
        "Change Received"
    )

    table_frame = tk.Frame(history_tab, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, padx=15, pady=10)

    table = ttk.Treeview(
        table_frame,
        columns=history_columns,
        show="headings"
    )
    for column in history_columns:
        table.heading(column, text=column)

    table.column("Transaction ID", width=90, anchor="center")
    table.column("Date and Time", width=150, anchor="center")
    table.column("Purchased Products", width=220)
    table.column("Quantity", width=80, anchor="center")
    table.column("Total Amount", width=110, anchor="e")
    table.column("Amount Paid", width=110, anchor="e")
    table.column("Change Received", width=120, anchor="e")

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)
    table.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def refresh_transactions():
        for row in table.get_children():
            table.delete(row)

        for transaction in transaction_history:
            table.insert("", "end", values=(
                transaction["id"],
                transaction["date_time"],
                transaction["products"],
                transaction["quantity"],
                f"₱{transaction['total']:.2f}",
                f"₱{transaction['amount_paid']:.2f}",
                f"₱{transaction['change']:.2f}"
            ))

    tk.Button(
        history_tab,
        text="Refresh",
        command=refresh_transactions
    ).pack(pady=(0, 10))

    refresh_transactions()