import tkinter as tk
from tkinter import messagebox

def show_admin_panel():
    admin_window = tk.Toplevel()
    admin_window.title("Admin Panel")
    admin_window.geometry("500x400")
    admin_window.configure(bg="#20242b")

    tk.Label(
        admin_window,
        text="ADMIN PANEL",
        font=("Arial", 20, "bold"),
        bg="#20242b",
        fg="#00e676"
    ).pack(pady=20)