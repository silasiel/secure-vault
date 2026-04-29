import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.ttk import Progressbar
import subprocess
import os

EXECUTABLE = os.path.abspath("../build/encryptor.exe")

selected_file = None
result_file = None

# -------------------------
# Run backend command
# -------------------------
def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            messagebox.showerror("Error", result.stderr or result.stdout)
            return False
        return True
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return False

# -------------------------
# Password strength check
# -------------------------
def is_weak_password(password):
    score = 0
    if len(password) >= 8: score += 1
    if len(password) >= 12: score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(not c.isalnum() for c in password): score += 1
    return score <= 2

# -------------------------
# Browse File
# -------------------------
def browse_file():
    global selected_file
    file_path = filedialog.askopenfilename()
    if file_path:
        selected_file = file_path
        file_label.config(text=f"Selected: {os.path.basename(selected_file)}")

# -------------------------
# Open result file
# -------------------------
def open_file():
    if result_file and os.path.exists(result_file):
        os.startfile(result_file)

def open_folder():
    if result_file and os.path.exists(result_file):
        os.startfile(os.path.dirname(result_file))

# -------------------------
# Encrypt
# -------------------------
def encrypt():
    global result_file

    if not selected_file:
        messagebox.showwarning("No File", "Please select a file first")
        return

    password = simpledialog.askstring("Password", "Enter password:", show="*")
    if not password:
        return

    if is_weak_password(password):
        if not messagebox.askyesno("Weak Password", "Weak password! Continue?"):
            return

    output = selected_file + ".enc"
    result_file = output

    status_label.config(text="Encrypting...")
    progress.start()

    success = run_command([EXECUTABLE, "encrypt", selected_file, output, password])

    progress.stop()

    if success:
        status_label.config(text="Encryption complete ✅")
        result_label.config(text=result_file)

# -------------------------
# Decrypt
# -------------------------
def decrypt():
    global result_file

    if not selected_file:
        messagebox.showwarning("No File", "Please select a file first")
        return

    password = simpledialog.askstring("Password", "Enter password:", show="*")
    if not password:
        return

    output = selected_file + ".dec"
    result_file = output

    status_label.config(text="Decrypting...")
    progress.start()

    success = run_command([EXECUTABLE, "decrypt", selected_file, output, password])

    progress.stop()

    if success:
        status_label.config(text="Decryption complete ✅")
        result_label.config(text=result_file)

# -------------------------
# Preview
# -------------------------
def preview():
    if not selected_file:
        messagebox.showwarning("No File", "Please select a file first")
        return

    password = simpledialog.askstring("Password", "Enter password:", show="*")
    if not password:
        return

    result = subprocess.run(
        [EXECUTABLE, "preview", selected_file, password],
        capture_output=True, text=True
    )

    preview_window = tk.Toplevel(root)
    preview_window.title("Preview")

    text = tk.Text(preview_window, wrap="word")
    text.insert("1.0", result.stdout)
    text.pack(expand=True, fill="both")

# -------------------------
# GUI
# -------------------------
root = tk.Tk()
root.title("Secure File Encryptor 🔐")
root.geometry("550x450")
root.configure(bg="#1e1e1e")

tk.Label(root, text="Secure File Encryptor",
         bg="#1e1e1e", fg="white", font=("Arial", 16)).pack(pady=15)

tk.Button(root, text="Upload File", command=browse_file, width=20).pack(pady=10)

file_label = tk.Label(root, text="No file selected",
                      bg="#1e1e1e", fg="lightgray")
file_label.pack(pady=5)

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=15)

tk.Button(btn_frame, text="Encrypt", command=encrypt, width=10).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Decrypt", command=decrypt, width=10).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Preview", command=preview, width=10).grid(row=0, column=2, padx=5)

progress = Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
progress.pack(pady=15)

status_label = tk.Label(root, text="Ready",
                        bg="#1e1e1e", fg="lightgreen")
status_label.pack()

# -------------------------
# Result File Section (NEW)
# -------------------------
tk.Label(root, text="Result File:",
         bg="#1e1e1e", fg="white").pack(pady=(15, 5))

result_label = tk.Label(root, text="None",
                        bg="#2d2d2d", fg="white", width=50, anchor="w")
result_label.pack(pady=5)

result_btn_frame = tk.Frame(root, bg="#1e1e1e")
result_btn_frame.pack()

tk.Button(result_btn_frame, text="Open", command=open_file).grid(row=0, column=0, padx=5)
tk.Button(result_btn_frame, text="Open Folder", command=open_folder).grid(row=0, column=1, padx=5)

root.mainloop()