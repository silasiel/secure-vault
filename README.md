# SecureVault
SecureVault is a secure desktop file storage application that allows users to encrypt, organize, preview, and manage sensitive files through a simple graphical interface. The project combines the performance of C-based cryptography with the usability of a Python GUI to create a secure and accessible file protection system.  <br>
## Developed by:
This app was made in collaboration with Faizah Hafeez(@faizahhafeez2-code), Sakina Fatima Mirza(@sakinastlw110), and myself(@silasiel) <br>

# Features
* AES-GCM file encryption using OpenSSL
* Password-protected secure folders
* Drag-and-drop file support
* File preview functionality
* Secure file decryption
* Vault-based file organization
* Activity logging system
* Desktop GUI for ease of use
* Windows installer support <br>

# Tech Stack Used:
## Languages
- C
- Python
## Libraries & Tools
- OpenSSL 
- Tkinter
- TkinterDnD2 
- hashlib
- PyInstaller 
- Inno Setup <br>

# Installation
### Method 1 — Installer (Recommended)
* Download SecureVault_Setup.exe from Releases
* Run the installer
* Launch SecureVault from Desktop or Start Menu
* If Windows SmartScreen appears, click: More Info → Run Anyway
### Running From Source
* Requirements
- Python 3.12+
- MinGW GCC
- OpenSSL
#### Steps
- Build C Backend
```bash
mingw32-make
```
- Run GUI
```bash
python gui/app.py
```
<br>

# Screenshots
To be added <br>

# Some Additional Security Notes
- Files are encrypted using AES-GCM authenticated encryption
- Password-protected folders prevent unauthorized access
- Sensitive data is stored locally on the user’s machine
- No cloud storage or external servers are used <br>

# License
This project is licensed under the MIT License.
