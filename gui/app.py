import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import os
from datetime import datetime

from tkinterdnd2 import TkinterDnD, DND_FILES

from theme import *
from vault_manager import *

ensure_vault()

selected_files = []
current_folder = None
EXECUTABLE = "build/encryptor.exe"


# ================= LOGGING =================
def log_action(action, target):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs/history.log", "a") as f:
        f.write(f"[{timestamp}] {action} {target}\n")


# ================= PASSWORD =================
def ask_password():
    return simpledialog.askstring("Password", "Enter password:", show="*")


# ================= FILE SELECTION =================
def select_files():
    global selected_files
    files = filedialog.askopenfilenames()
    if files:
        selected_files = list(files)
        status_label.config(text=f"{len(files)} files selected")


# ================= DRAG DROP =================
def handle_drop(event):
    global selected_files
    files = root.tk.splitlist(event.data)
    selected_files = list(files)
    status_label.config(text=f"{len(files)} files dropped")


# ================= FOLDER =================
def create_new_folder():
    name = simpledialog.askstring("Folder", "Folder name:")
    if not name:
        return

    create_folder(name)

    pwd = simpledialog.askstring(
        "Set Password",
        f"Set password for '{name}':",
        show="*"
    )

    if pwd:
        set_folder_password(name, pwd)
        log_action("CREATE_SECURE_FOLDER", name)

    refresh_folders()


def open_folder(folder):
    global current_folder

    result = verify_folder_password(folder, "")

    if result is None:
        pwd = simpledialog.askstring(
            "Set Password",
            f"Set password for folder '{folder}':",
            show="*"
        )
        if not pwd:
            return

        set_folder_password(folder, pwd)
        log_action("SET_PASSWORD", folder)

    else:
        pwd = simpledialog.askstring(
            "Unlock Folder",
            f"Enter password for '{folder}':",
            show="*"
        )
        if not pwd:
            return

        if not verify_folder_password(folder, pwd):
            messagebox.showerror("Access Denied", "Incorrect password")
            return

    current_folder = folder
    status_label.config(text=f"Opened: {folder}")
    refresh_files()


# ================= ENCRYPT =================
def encrypt_files_to_folder():
    if not selected_files:
        messagebox.showerror("Error", "No files selected")
        return

    if not current_folder:
        messagebox.showerror("Error", "Select a folder")
        return

    password = ask_password()
    if not password:
        return

    encrypt_files(selected_files, current_folder, password)

    log_action("ENCRYPT_BATCH", f"{len(selected_files)} files -> {current_folder}")

    refresh_files()


# ================= DECRYPT =================
def decrypt_file(file):
    password = ask_password()
    if not password:
        return

    input_path = os.path.join("vault", current_folder, file)

    output = filedialog.asksaveasfilename(
        initialfile=file.replace(".enc", "_decrypted")
    )

    if not output:
        return

    subprocess.run([EXECUTABLE, "decrypt", input_path, output, password])

    if os.path.exists(output):
        log_action("DECRYPT", file)
        os.startfile(output)
    else:
        messagebox.showerror("Error", "Decryption failed")


# ================= PREVIEW =================
def preview_file(file):
    path = os.path.join("vault", current_folder, file)

    result = subprocess.run(
        [EXECUTABLE, "preview", path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    win = tk.Toplevel(root)
    win.title("Preview")
    win.geometry("600x400")
    win.configure(bg=APP_BG)

    text = tk.Text(win, bg=CARD_BG, fg=TEXT_PRIMARY)
    text.pack(fill="both", expand=True)

    text.insert("1.0", result.stdout if result.stdout else "No preview")


# ================= LOG VIEW =================
def view_logs():
    log_path = "logs/history.log"
    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(log_path):
        open(log_path, "w").close()

    win = tk.Toplevel(root)
    win.title("Logs")
    win.geometry("650x450")
    win.configure(bg=APP_BG)

    top_frame = tk.Frame(win, bg=APP_BG)
    top_frame.pack(fill="x", pady=5)

    text = tk.Text(win, bg=CARD_BG, fg="#00ff99", insertbackground="white")
    text.pack(fill="both", expand=True, padx=10, pady=5)

    def load_logs():
        text.delete("1.0", tk.END)
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        text.insert("1.0", content if content else "Logs empty")

    def clear_logs():
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            open(log_path, "w").close()
            load_logs()
            messagebox.showinfo("Done", "Logs cleared")

    tk.Button(top_frame, text="Refresh",
              bg=ACCENT, fg=ACCENT_TEXT,
              command=load_logs).pack(side="left", padx=10)

    tk.Button(top_frame, text="Clear Logs",
              bg="#d9534f", fg="white",
              command=clear_logs).pack(side="left", padx=10)

    load_logs()


# ================= DELETE =================
def delete_selected_file(file):
    delete_file(current_folder, file)
    log_action("DELETE", f"{current_folder}/{file}")
    refresh_files()


def delete_selected_folder(folder):
    confirm = messagebox.askyesno("Delete", f"Delete folder {folder}?")
    if not confirm:
        return

    success = delete_folder(folder)

    if not success:
        messagebox.showerror("Error", "Could not delete folder")
        return

    log_action("DELETE_FOLDER", folder)

    global current_folder
    if current_folder == folder:
        current_folder = None

    refresh_folders()
    refresh_files()


# ================= REFRESH =================
def refresh_folders():
    for w in folder_list.winfo_children():
        w.destroy()

    for f in get_folders():
        frame = tk.Frame(folder_list, bg=SIDEBAR_BG)
        frame.pack(fill="x", pady=3)

        tk.Button(frame, text=f, bg=ACCENT, fg=ACCENT_TEXT,
                  command=lambda folder=f: open_folder(folder)).pack(side="left", fill="x", expand=True)

        tk.Button(frame, text="X", bg="#d9534f", fg="white",
                  command=lambda folder=f: delete_selected_folder(folder)).pack(side="right")


def refresh_files():
    for w in file_list_frame.winfo_children():
        w.destroy()

    if not current_folder:
        return

    for f in get_files(current_folder):
        if f == ".meta":
            continue

        frame = tk.Frame(file_list_frame, bg=CARD_BG, pady=6, padx=6)
        frame.pack(fill="x", padx=10, pady=4)

        tk.Label(frame, text=f, bg=CARD_BG, fg=TEXT_PRIMARY).pack(side="left")

        btn_frame = tk.Frame(frame, bg=CARD_BG)
        btn_frame.pack(side="right")

        tk.Button(btn_frame, text="Decrypt", bg=ACCENT, fg=ACCENT_TEXT,
                  command=lambda file=f: decrypt_file(file)).pack(side="left", padx=3)

        tk.Button(btn_frame, text="Preview", bg=ACCENT, fg=ACCENT_TEXT,
                  command=lambda file=f: preview_file(file)).pack(side="left", padx=3)

        tk.Button(btn_frame, text="Delete", bg="#d9534f", fg="white",
                  command=lambda file=f: delete_selected_file(file)).pack(side="left", padx=3)


# ================= GUI =================
root = TkinterDnD.Tk()
root.title("SECURE VAULT")
root.geometry("1150x720")
root.configure(bg=APP_BG)

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)


# SIDEBAR
sidebar = tk.Frame(root, bg=SIDEBAR_BG, width=260)
sidebar.grid(row=0, column=0, sticky="ns")
sidebar.grid_propagate(False)

tk.Label(sidebar, text="SECURE VAULT",
         bg=SIDEBAR_BG,
         fg=TEXT_PRIMARY,
         font=("Segoe UI", 16, "bold")).pack(pady=15)

tk.Button(sidebar, text="Logs", bg=ACCENT, fg=ACCENT_TEXT,
          command=view_logs).pack(fill="x", padx=10, pady=5)

tk.Frame(sidebar, height=2, bg="#3a3a3a").pack(fill="x", padx=10, pady=8)

tk.Button(sidebar, text="Select Files", bg=ACCENT, fg=ACCENT_TEXT,
          command=select_files).pack(fill="x", padx=10, pady=5)

tk.Button(sidebar, text="New Folder", bg=ACCENT, fg=ACCENT_TEXT,
          command=create_new_folder).pack(fill="x", padx=10, pady=5)

tk.Frame(sidebar, height=2, bg="#3a3a3a").pack(fill="x", padx=10, pady=8)

folder_list = tk.Frame(sidebar, bg=SIDEBAR_BG)
folder_list.pack(fill="both", expand=True)


# MAIN
main = tk.Frame(root, bg=APP_BG)
main.grid(row=0, column=1, sticky="nsew")

main.grid_rowconfigure(2, weight=1)
main.grid_columnconfigure(0, weight=1)


# DROP ZONE
drop = tk.Frame(main, bg=CARD_BG, height=260, bd=2, relief="ridge")
drop.grid(row=0, column=0, sticky="ew", padx=20, pady=15)

tk.Label(drop, text="Drag & Drop Files Here",
         bg=CARD_BG,
         fg=TEXT_PRIMARY,
         font=("Segoe UI", 16)).pack(expand=True)

drop.drop_target_register(DND_FILES)
drop.dnd_bind("<<Drop>>", handle_drop)


tk.Button(main, text="Encrypt Files",
          bg=ACCENT, fg=ACCENT_TEXT,
          command=encrypt_files_to_folder).grid(row=1, column=0, pady=5)


file_list_frame = tk.Frame(main, bg=APP_BG)
file_list_frame.grid(row=2, column=0, sticky="nsew")


status_label = tk.Label(main, text="Ready", bg=APP_BG, fg=TEXT_SECONDARY)
status_label.grid(row=3, column=0, pady=5)


refresh_folders()

root.mainloop()