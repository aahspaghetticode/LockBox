import os
import sys
import subprocess
def is_root():
    return os.geteuid() == 0

def elevate_with_pkexec():
    try:
        script_abs_path = os.path.abspath(sys.argv[0])
        print(f"Using script absolute path: {script_abs_path}")
        subprocess.check_call(["pkexec", sys.executable, script_abs_path] + sys.argv[1:])
    except subprocess.CalledProcessError:
        sys.exit(1)

if is_root() == False:
    print("Downloading...")
    os.makedirs(os.path.expanduser("~/.local/share/LockBox/"), exist_ok=True)
    subprocess.run("curl -L https://raw.githubusercontent.com/aahspaghetticode/LockBox/refs/heads/main/main -o ~/.local/share/LockBox/main", shell=True)
    subprocess.run("chmod +x ~/.local/share/LockBox/main", shell=True)
    os.makedirs(os.path.expanduser("~/.local/share/icons/"), exist_ok=True)
    subprocess.run("curl -L https://raw.githubusercontent.com/aahspaghetticode/LockBox/refs/heads/main/Icon.png -o ~/.local/share/icons/LockBox.png", shell=True)
    desktop_file_path = os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "LockBox.desktop")
    with open(desktop_file_path, "w") as file:
        file.write(f'''[Desktop Entry]
Version=1.0
Type=Application
Name=LockBox
Comment=Secure password storage
Exec={os.path.expanduser("~")}/.local/share/LockBox/main
Icon={os.path.expanduser("~")}/.local/share/icons/LockBox.png
Terminal=false
Categories=Utility;
''')
    subprocess.run("chmod +x ~/.local/share/applications/LockBox.desktop", shell=True)
    subprocess.run("gtk-update-icon-cache ~/.local/share/icons/", shell=True)
    subprocess.run("update-desktop-database ~/.local/share/applications/", shell=True)
    elevate_with_pkexec()
    sys.exit(0)
print("installing...")
subprocess.run("sudo apt update && sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 python3 python3-cryptography", shell=True)