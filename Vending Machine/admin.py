import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import math

def show_admin_panel(parent, transaction_history):

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
    current_money_label.pack(side="left")

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
        show="headings",
        style="RedRoses.Treeview"
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

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview,
        style="RedRoses.Vertical.TScrollbar"
    )
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

    def refresh_summary():
        total_sales_label.config(text=f"Total Sales: ₱{parent.total_sales:.2f}")
        current_money_label.config(
            text=f"Current Machine Money: ₱{parent.starting_current_money:.2f}"
        )
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

    def withdraw_profit(root):
        amount = simpledialog.askfloat(
            "Withdraw",
            "How much would you like to withdraw?",
            parent=admin,
            minvalue=0.01
        )

        if amount is None:
            return

        if not math.isfinite(amount):
            messagebox.showerror(
                "Invalid Amount",
                "Enter a valid withdrawal amount.",
                parent=admin
            )
            return

        if not messagebox.askyesno(
            "Confirm Withdrawal",
            f"Withdraw ₱{amount:.2f}?",
            parent=admin
        ):
            return

        if amount > root.starting_current_money:
            messagebox.showerror(
                "Insufficient Balance",
                "There is not enough available balance for this withdrawal.",
                parent=admin
            )
            return

        root.starting_current_money -= amount
        messagebox.showinfo(
            "Withdrawal Successful",
            f"₱{amount:.2f} was withdrawn successfully.",
            parent=admin
        )
        refresh_transactions()

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