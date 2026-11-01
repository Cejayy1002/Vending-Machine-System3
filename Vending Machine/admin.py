
import tkinter as tk


def show_admin_panel(root):
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Panel")
    admin_window.geometry("500x400")
    admin_window.configure(bg="#E8EDF4")
    admin_window.resizable(False, False)

    tk.Label(
        admin_window,
        text="ADMIN PANEL",
        font=("Arial", 20, "bold"),
        bg="#E8EDF4",
        fg="#34445A"
    ).pack(pady=30)
