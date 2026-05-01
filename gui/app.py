import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.ttk import Progressbar
import subprocess
import os

APP_BG = "#1e1e1e"
CARD_BG = "#2a2a2a"
TEXT_COLOR = "#ffffff"
BTN_COLOR = "#3a3a3a"
ACCENT = "#4CAF50"

selected_file = None
output_file = None


# BACKEND
def run_command(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")


# PASSWORD
def ask_password():
    password = simpledialog.askstring("Password", "Enter password:", show="*")
    if not password:
        return None

    if len(password) < 6:
        proceed = messagebox.askyesno(
            "Weak Password",
            "Weak password detected. Proceed anyway?"
        )
        if not proceed:
            return None

    return password


# FILE SELECTION
def choose_file():
    global selected_file
    file_path = filedialog.askopenfilename()

    if file_path:
        selected_file = file_path
        file_label.config(text=os.path.basename(file_path))
        status_label.config(text="File selected")


# OUTPUT
def show_output_buttons():
    open_btn.grid()
    folder_btn.grid()


def open_file():
    if not output_file:
        messagebox.showerror("Error", "No output file available")
        return

    if not os.path.exists(output_file):
        messagebox.showerror("Error", "Output file not found (operation may have failed)")
        return

    os.startfile(output_file)


def open_folder():
    if output_file and os.path.exists(output_file):
        os.startfile(os.path.dirname(output_file))


# ENCRYPT
def encrypt_file():
    global output_file

    if not selected_file:
        messagebox.showerror("Error", "No file selected")
        return

    password = ask_password()
    if not password:
        return

    output = selected_file + ".enc"

    progress.start()

    result = run_command([
        "../build/encryptor.exe",
        "encrypt",
        selected_file,
        output,
        password
    ])

    progress.stop()

    if result.returncode == 0:
        output_file = output
        status_label.config(text=f"Encrypted → {os.path.basename(output)}")
        show_output_buttons()
    else:
        status_label.config(text="Encryption failed")
        messagebox.showerror("Error", result.stderr)


# DECRYPT
def decrypt_file():
    global output_file

    if not selected_file:
        messagebox.showerror("Error", "No file selected")
        return

    password = ask_password()
    if not password:
        return

    output = selected_file.replace(".enc", "") + "_decrypted"

    progress.start()

    result = run_command([
        "../build/encryptor.exe",
        "decrypt",
        selected_file,
        output,
        password
    ])

    progress.stop()

    if result.returncode != 0:
        status_label.config(text="Integrity check failed")
        messagebox.showerror(
            "Decryption Error",
            "File is tampered or password is incorrect."
        )
        return

    output_file = output
    status_label.config(text=f"Decrypted → {os.path.basename(output)}")
    show_output_buttons()


# PREVIEW
def preview_file():
    if not selected_file:
        messagebox.showerror("Error", "No file selected")
        return

    result = run_command([
        "../build/encryptor.exe",
        "preview",
        selected_file
    ])

    win = tk.Toplevel(root)
    win.title("Preview")
    win.geometry("500x400")

    text = tk.Text(win, wrap="word")
    text.insert("1.0", result.stdout if result.stdout else "No preview available")
    text.pack(expand=True, fill="both")


# LOG VIEW
def view_logs():
    log_path = "../logs/history.log"

    win = tk.Toplevel(root)
    win.title("Logs")
    win.geometry("500x400")

    top_frame = tk.Frame(win, bg=APP_BG)
    top_frame.pack(fill="x", pady=5)

    text_frame = tk.Frame(win)
    text_frame.pack(fill="both", expand=True)

    text = tk.Text(text_frame, bg="#111", fg="#0f0")
    text.pack(fill="both", expand=True)

    def load_logs():
        text.delete("1.0", tk.END)

        if not os.path.exists(log_path):
            with open(log_path, "w"):
                pass

        with open(log_path, "r") as f:
            content = f.read()

        if content.strip() == "":
            text.insert("1.0", "Logs are empty")
        else:
            text.insert("1.0", content)

    def clear_logs():
        if messagebox.askyesno("Confirm", "Delete all logs?"):
            with open(log_path, "w") as f:
                f.truncate(0)
            load_logs()
            messagebox.showinfo("Success", "Logs cleared")

    refresh_btn = tk.Button(
        top_frame,
        text="Refresh",
        bg="#2e2e2e",
        fg="#ffffff",
        activebackground="#3a3a3a",
        relief="flat",
        borderwidth=0,
        padx=10,
        pady=5,
        command=load_logs
    )
    refresh_btn.pack(side="left", padx=10)

    clear_btn = tk.Button(
        top_frame,
        text="Clear Logs",
        bg="#5a1e1e",
        fg="#ffffff",
        activebackground="#7a2a2a",
        relief="flat",
        borderwidth=0,
        padx=10,
        pady=5,
        command=clear_logs
    )
    clear_btn.pack(side="left", padx=10)

    load_logs()


# GUI
root = tk.Tk()
root.title("ENCRYPTION AND DECRYPTION TOOL")
root.geometry("600x500")
root.configure(bg=APP_BG)

title = tk.Label(
    root,
    text="ENCRYPTION AND DECRYPTION TOOL",
    bg=APP_BG,
    fg=ACCENT,
    font=("Segoe UI", 16, "bold")
)
title.pack(pady=15)

card = tk.Frame(root, bg=CARD_BG, padx=20, pady=20)
card.pack(padx=20, pady=10, fill="both", expand=True)

file_label = tk.Label(
    card,
    text="No file selected",
    bg=CARD_BG,
    fg=TEXT_COLOR
)
file_label.pack(pady=10)

select_btn = tk.Button(
    card,
    text="Choose File",
    bg=BTN_COLOR,
    fg=TEXT_COLOR,
    width=20,
    command=choose_file
)
select_btn.pack(pady=5)

btn_frame = tk.Frame(card, bg=CARD_BG)
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="Encrypt", bg=ACCENT, fg="white", width=10, command=encrypt_file).grid(row=0, column=0, padx=8)
tk.Button(btn_frame, text="Decrypt", bg="#2196F3", fg="white", width=10, command=decrypt_file).grid(row=0, column=1, padx=8)
tk.Button(btn_frame, text="Preview", bg="#FF9800", fg="white", width=10, command=preview_file).grid(row=0, column=2, padx=8)
tk.Button(btn_frame, text="Logs", bg="#9C27B0", fg="white", width=10, command=view_logs).grid(row=0, column=3, padx=8)

progress = Progressbar(card, orient="horizontal", length=300, mode="indeterminate")
progress.pack(pady=15)

status_label = tk.Label(card, text="Ready", bg=CARD_BG, fg=TEXT_COLOR)
status_label.pack(pady=5)

output_frame = tk.Frame(card, bg=CARD_BG)
output_frame.pack(pady=10)

open_btn = tk.Button(output_frame, text="Open File", command=open_file)
open_btn.grid(row=0, column=0, padx=10)
open_btn.grid_remove()

folder_btn = tk.Button(output_frame, text="Open Folder", command=open_folder)
folder_btn.grid(row=0, column=1, padx=10)
folder_btn.grid_remove()

root.mainloop()