import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import subprocess
import sys
import os
import threading
import shutil
from datetime import datetime

from tkinterdnd2 import TkinterDnD, DND_FILES

from theme import *
from vault_manager import *


# PATH
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if getattr(sys, 'frozen', False):
    EXECUTABLE = os.path.join(BASE_DIR, "encryptor.exe")
else:
    EXECUTABLE = os.path.join(BASE_DIR, "build", "encryptor.exe")

APPDATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA"), "SecureVault")
BASE_VAULT = os.path.join(APPDATA_DIR, "vault")
LOGS_DIR = os.path.join(APPDATA_DIR, "logs")

ensure_vault()

selected_files = []
current_folder = None

# UTIL
def check_backend():
    try:
        subprocess.run([EXECUTABLE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        messagebox.showerror("Error", "Encryption engine missing or blocked")
        return False


def run_command(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr if result.stderr else "Operation failed")

    return result


# LOGGING
def log_action(action, target):
    os.makedirs(LOGS_DIR, exist_ok=True)

    log_path = os.path.join(LOGS_DIR, "history.log")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action} {target}\n")



def view_logs():
    os.makedirs(LOGS_DIR, exist_ok=True)

    log_path = os.path.join(LOGS_DIR, "history.log")

    if not os.path.exists(log_path):
        open(log_path, "w").close()

    win = tk.Toplevel(root)
    win.title("Logs")
    win.geometry("650x450")
    win.configure(bg=APP_BG)

    text = tk.Text(
        win,
        bg=CARD_BG,
        fg="#00ff99",
        insertbackground="white"
    )

    text.pack(fill="both", expand=True, padx=10, pady=10)

    def load_logs():
        text.delete("1.0", tk.END)

        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        text.insert("1.0", content if content else "Logs empty")

    def clear_logs():
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            open(log_path, "w").close()
            load_logs()

    btn_frame = tk.Frame(win, bg=APP_BG)
    btn_frame.pack(fill="x")

    tk.Button(
        btn_frame,
        text="Refresh",
        bg=ACCENT,
        fg=ACCENT_TEXT,
        command=load_logs
    ).pack(side="left", padx=10, pady=5)

    tk.Button(
        btn_frame,
        text="Clear Logs",
        bg="#d9534f",
        fg="white",
        command=clear_logs
    ).pack(side="left", padx=10, pady=5)

    load_logs()


# PASSWORD
def check_password_strength(password):
    score = 0

    if len(password) >= 8:
        score += 1

    if any(c.isupper() for c in password):
        score += 1

    if any(c.islower() for c in password):
        score += 1

    if any(c.isdigit() for c in password):
        score += 1

    if any(not c.isalnum() for c in password):
        score += 1

    return score



def ask_password():
    win = tk.Toplevel(root)
    win.title("Password")
    win.geometry("350x180")
    win.configure(bg=APP_BG)
    win.grab_set()

    result = {"password": None}

    tk.Label(
        win,
        text="Enter Password",
        bg=APP_BG,
        fg=TEXT_PRIMARY,
        font=("Segoe UI", 11)
    ).pack(pady=10)

    password_var = tk.StringVar()

    entry = tk.Entry(
        win,
        textvariable=password_var,
        show="*",
        width=30
    )

    entry.pack(pady=5)

    strength_label = tk.Label(
        win,
        text="Strength: ",
        bg=APP_BG,
        fg=TEXT_SECONDARY
    )

    strength_label.pack(pady=5)

    def update_strength(*args):
        pwd = password_var.get()
        score = check_password_strength(pwd)

        if score <= 2:
            strength_label.config(text="Strength: Weak", fg="red")
        elif score <= 4:
            strength_label.config(text="Strength: Medium", fg="orange")
        else:
            strength_label.config(text="Strength: Strong", fg="green")

    password_var.trace_add("write", update_strength)

    def submit():
        result["password"] = password_var.get()
        win.destroy()

    tk.Button(
        win,
        text="OK",
        bg=ACCENT,
        fg=ACCENT_TEXT,
        command=submit
    ).pack(pady=10)

    entry.focus()

    root.wait_window(win)

    return result["password"]


# FILE SELECTION
def select_files():
    global selected_files

    files = filedialog.askopenfilenames()

    if files:
        selected_files = list(files)
        status_label.config(text=f"{len(files)} files selected")


# DRAG DROP
def handle_drop(event):
    global selected_files

    files = root.tk.splitlist(event.data)

    selected_files = list(files)

    status_label.config(text=f"{len(files)} files dropped")


# FOLDER
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
            f"Set password for '{folder}':",
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


# ENCRYPT
def encrypt_files_to_folder(password):
    if not selected_files:
        messagebox.showerror("Error", "No files selected")
        return

    if not current_folder:
        messagebox.showerror("Error", "Select a folder")
        return

    if not check_backend():
        return

    total = len(selected_files)

    try:
        for i, file in enumerate(selected_files):
            encrypt_files([file], current_folder, password, EXECUTABLE)

            percent = ((i + 1) / total) * 100

            root.after(
                0,
                lambda p=percent: progress_var.set(p)
            )

        log_action(
            "ENCRYPT_BATCH",
            f"{len(selected_files)} files -> {current_folder}"
        )

        root.after(0, refresh_files)

        root.after(
            0,
            lambda: status_label.config(text="Encryption complete")
        )

    except Exception as e:
        err_msg = str(e)

        root.after(
            0,
            lambda: messagebox.showerror("Encryption Failed", err_msg)
        )



def run_encrypt_thread():
    password = ask_password()

    if not password:
        return

    progress_var.set(0)

    threading.Thread(
        target=encrypt_files_to_folder,
        args=(password,)
    ).start()


# DECRYPT
def decrypt_file(file):
    if not check_backend():
        return

    password = ask_password()

    if not password:
        return

    input_path = os.path.join(BASE_VAULT, current_folder, file)

    filename = file[:-4] if file.endswith(".enc") else file

    output = filedialog.asksaveasfilename(initialfile=filename)

    if not output:
        return

    try:
        result = subprocess.run(
            [EXECUTABLE, "decrypt", input_path, output, password],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(result.stderr or "Decryption failed")

        if os.path.exists(output):
            log_action("DECRYPT", file)
            os.startfile(output)
        else:
            raise Exception("Output file not created")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# PREVIEW
def preview_file(file):
    path = os.path.join(BASE_VAULT, current_folder, file)

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

    text = tk.Text(
        win,
        bg=CARD_BG,
        fg=TEXT_PRIMARY
    )

    text.pack(fill="both", expand=True)

    text.insert("1.0", result.stdout if result.stdout else "No preview")


# DOWNLOAD
def download_file(file):
    src = os.path.join(BASE_VAULT, current_folder, file)

    dest = filedialog.asksaveasfilename(initialfile=file)

    if not dest:
        return

    shutil.copy2(src, dest)

    log_action("DOWNLOAD_ENCRYPTED_FILE", file)

    messagebox.showinfo("Success", "Encrypted file downloaded")



def download_folder(folder):
    src = os.path.join(BASE_VAULT, folder)

    dest = filedialog.askdirectory()

    if not dest:
        return

    target = os.path.join(dest, folder)

    shutil.copytree(src, target, dirs_exist_ok=True)

    log_action("DOWNLOAD_FOLDER", folder)

    messagebox.showinfo("Success", "Encrypted folder downloaded")


# DELETE
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


# SEARCH
def filter_files(*args):
    refresh_files()


def refresh_ui_theme():
    root.configure(bg=APP_BG)

    sidebar.configure(bg=SIDEBAR_BG)

    main.configure(bg=APP_BG)

    drop.configure(bg=CARD_BG)

    status_label.configure(
        bg=APP_BG,
        fg=TEXT_SECONDARY
    )

    refresh_folders()
    refresh_files()


# REFRESH
def refresh_folders():
    for w in folder_list.winfo_children():
        w.destroy()

    for f in get_folders():
        frame = tk.Frame(folder_list, bg=SIDEBAR_BG)
        frame.pack(fill="x", pady=3)

        tk.Button(
            frame,
            text=f,
            bg=ACCENT,
            fg=ACCENT_TEXT,
            command=lambda folder=f: open_folder(folder)
        ).pack(side="left", fill="x", expand=True)

        tk.Button(
            frame,
            text="⬇️",
            bg=HIGHLIGHT,
            fg="black",
            command=lambda folder=f: download_folder(folder)
        ).pack(side="right", padx=2)

        tk.Button(
            frame,
            text="X",
            bg="#d9534f",
            fg="white",
            command=lambda folder=f: delete_selected_folder(folder)
        ).pack(side="right")



def refresh_files():
    for w in file_list_frame.winfo_children():
        w.destroy()

    if not current_folder:
        return

    search_query = search_var.get().lower()

    if search_query == "search files":
        search_query = ""

    for f in get_files(current_folder):
        if f == ".meta":
            continue

        if search_query not in f.lower():
            continue

        frame = tk.Frame(file_list_frame, bg=CARD_BG, pady=6, padx=6)
        frame.pack(fill="x", padx=10, pady=4)

        tk.Label(
            frame,
            text=f,
            bg=CARD_BG,
            fg=TEXT_PRIMARY
        ).pack(side="left")

        btn_frame = tk.Frame(frame, bg=CARD_BG)
        btn_frame.pack(side="right")

        tk.Button(
            btn_frame,
            text="⬇️",
            bg=HIGHLIGHT,
            fg="black",
            command=lambda file=f: download_file(file)
        ).pack(side="left", padx=3)

        tk.Button(
            btn_frame,
            text="Decrypt",
            bg=ACCENT,
            fg=ACCENT_TEXT,
            command=lambda file=f: decrypt_file(file)
        ).pack(side="left", padx=3)

        tk.Button(
            btn_frame,
            text="Preview",
            bg=ACCENT,
            fg=ACCENT_TEXT,
            command=lambda file=f: preview_file(file)
        ).pack(side="left", padx=3)

        tk.Button(
            btn_frame,
            text="Delete",
            bg="#d9534f",
            fg="white",
            command=lambda file=f: delete_selected_file(file)
        ).pack(side="left", padx=3)


# GUI
root = TkinterDnD.Tk()
progress_var = tk.DoubleVar()
search_var = tk.StringVar()
root.title("SECURE VAULT")
root.geometry("1150x720")
root.configure(bg=APP_BG)

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

sidebar = tk.Frame(root, bg=SIDEBAR_BG, width=260)
sidebar.grid(row=0, column=0, sticky="ns")
sidebar.grid_propagate(False)


# SIDEBAR

tk.Label(
    sidebar,
    text="SECURE VAULT",
    bg=SIDEBAR_BG,
    fg=TEXT_PRIMARY,
    font=("Segoe UI", 16, "bold")
).pack(pady=15)


tk.Button(
    sidebar,
    text="Logs",
    bg=ACCENT,
    fg=ACCENT_TEXT,
    command=view_logs
).pack(fill="x", padx=10, pady=5)


tk.Frame(sidebar, height=2, bg="#abadba").pack(fill="x", padx=10, pady=8)


tk.Button(
    sidebar,
    text="Select Files",
    bg=ACCENT,
    fg=ACCENT_TEXT,
    command=select_files
).pack(fill="x", padx=10, pady=5)


tk.Button(
    sidebar,
    text="New Folder",
    bg=ACCENT,
    fg=ACCENT_TEXT,
    command=create_new_folder
).pack(fill="x", padx=10, pady=5)



tk.Frame(sidebar, height=2, bg="#abadb1").pack(fill="x", padx=10, pady=8)


folder_list = tk.Frame(sidebar, bg=SIDEBAR_BG)
folder_list.pack(fill="both", expand=True)


# MAIN
main = tk.Frame(root, bg=APP_BG)
main.grid(row=0, column=1, sticky="nsew")


drop = tk.Frame(main, bg=CARD_BG, height=260, bd=2, relief="ridge")
drop.pack(fill="x", padx=20, pady=15)


tk.Label(
    drop,
    text="Drag & Drop Files Here",
    bg=CARD_BG,
    fg=TEXT_PRIMARY,
    font=("Segoe UI", 16)
).pack(expand=True)


drop.drop_target_register(DND_FILES)
drop.dnd_bind("<<Drop>>", handle_drop)


tk.Button(
    main,
    text="Encrypt Files",
    bg=ACCENT,
    fg=ACCENT_TEXT,
    command=run_encrypt_thread
).pack(pady=5)


search_bar = tk.Entry(
    main,
    textvariable=search_var,
    font=("Segoe UI", 11),
    fg="gray"
)

search_bar.insert(0, "Search files")

search_bar.pack(fill="x", padx=20, pady=5)
def clear_placeholder(event):
    if search_bar.get() == "Search files":
        search_bar.delete(0, tk.END)
        search_bar.config(fg="black")


def restore_placeholder(event):
    if not search_bar.get():
        search_bar.insert(0, "Search files")
        search_bar.config(fg="gray")


search_bar.bind("<FocusIn>", clear_placeholder)
search_bar.bind("<FocusOut>", restore_placeholder)

search_var.trace_add("write", filter_files)

style = ttk.Style()

style.theme_use("default")

style.configure(
    "purple.Horizontal.TProgressbar",
    troughcolor="#382F64",
    background="#A598C0",
    bordercolor="#382F64",
    lightcolor="#B9AACF",
    darkcolor="#BDADD4"
)

progress = ttk.Progressbar(
    main,
    variable=progress_var,
    maximum=100,
    style="purple.Horizontal.TProgressbar"
)

progress.pack(fill="x", padx=20, pady=5)


file_list_frame = tk.Frame(main, bg=APP_BG)
file_list_frame.pack(fill="both", expand=True)


status_label = tk.Label(
    main,
    text="Ready",
    bg=APP_BG,
    fg=TEXT_SECONDARY
)

status_label.pack(pady=5)


refresh_folders()
refresh_ui_theme()

root.mainloop()