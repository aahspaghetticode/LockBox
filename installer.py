import os
import sys
import subprocess

if True:
    print("Downloading...")
    os.makedirs(os.path.expanduser("~/.local/share/LockBox/"), exist_ok=True)
    subprocess.run("rm -r ~/.local/share/LockBox/dist", shell=True)
    subprocess.run("python3 -m ensurepip --upgrade", shell=True)
    subprocess.run("python3 -m pip install pyinstaller --break-system-packages", shell=True)
    subprocess.run("curl -L https://raw.githubusercontent.com/aahspaghetticode/LockBox/refs/heads/main/main.py -o ~/.local/share/LockBox/main.py", shell=True)
    subprocess.run("pyinstaller --onefile --noconsole --distpath ~/.local/share/LockBox/dist/ ~/.local/share/LockBox/main.py", shell=True)
    subprocess.run("chmod +x ~/.local/share/LockBox/dist/main", shell=True)
    os.makedirs(os.path.expanduser("~/.local/share/icons/"), exist_ok=True)
    subprocess.run("curl -L https://raw.githubusercontent.com/aahspaghetticode/LockBox/refs/heads/main/Icon.png -o ~/.local/share/icons/LockBox.png", shell=True)
    desktop_file_path = os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "LockBox.desktop")
    with open(desktop_file_path, "w") as file:
        file.write(f'''[Desktop Entry]
Version=1.0
Type=Application
Name=LockBox
Comment=Secure password storage
Exec={os.path.expanduser("~")}/.local/share/LockBox/dist/main
Icon={os.path.expanduser("~")}/.local/share/icons/LockBox.png
Terminal=false
Categories=Utility;
''')
    subprocess.run("chmod +x ~/.local/share/applications/LockBox.desktop", shell=True)
    subprocess.run("gtk-update-icon-cache ~/.local/share/icons/", shell=True)
    subprocess.run("update-desktop-database ~/.local/share/applications/", shell=True)
print("installing...")
subprocess.run("sudo apt update && sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3 python3-cryptography", shell=True)