import os
import hashlib
import json
import secrets
import subprocess
import shutil
import stat
import time

EXECUTABLE = "build/encryptor.exe"
VAULT = "vault"


def ensure_vault():
    os.makedirs(VAULT, exist_ok=True)


def get_folders():
    ensure_vault()
    return [f for f in os.listdir(VAULT) if os.path.isdir(os.path.join(VAULT, f))]


def create_folder(name):
    os.makedirs(os.path.join(VAULT, name), exist_ok=True)


def get_files(folder):
    path = os.path.join(VAULT, folder)
    if not os.path.exists(path):
        return []
    return os.listdir(path)


def encrypt_files(files, folder, password):
    folder_path = os.path.join(VAULT, folder)
    os.makedirs(folder_path, exist_ok=True)

    for f in files:
        out = os.path.join(folder_path, os.path.basename(f) + ".enc")
        subprocess.run([EXECUTABLE, "encrypt", f, out, password])


def delete_file(folder, file):
    path = os.path.join(VAULT, folder, file)
    if os.path.exists(path):
        os.remove(path)

def delete_folder(folder):
    path = os.path.join(VAULT, folder)

    if not os.path.exists(path):
        return False

    def handle_remove_readonly(func, path, exc):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except:
            pass

    try:
        shutil.rmtree(path, onerror=handle_remove_readonly)
        return True
    except Exception as e:
        print("Delete error:", e)
        return False
    
    

META_FILE = ".meta"


def get_meta_path(folder):
    return os.path.join("vault", folder, META_FILE)


def set_folder_password(folder, password):
    salt = secrets.token_hex(16)

    hashed = hashlib.sha256((password + salt).encode()).hexdigest()

    data = {
        "salt": salt,
        "hash": hashed
    }

    with open(get_meta_path(folder), "w") as f:
        json.dump(data, f)


def verify_folder_password(folder, password):
    meta_path = get_meta_path(folder)

    if not os.path.exists(meta_path):
        return None  # no password set

    with open(meta_path, "r") as f:
        data = json.load(f)

    salt = data["salt"]
    expected = data["hash"]

    check = hashlib.sha256((password + salt).encode()).hexdigest()

    return check == expected