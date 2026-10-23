"""
installer_setup.py — Official Windows Installer for Patte (Patte-Setup.exe).
Installs Patte into %LOCALAPPDATA%\\Programs\\Patte, creates Desktop & Start Menu
shortcuts, registers Patte in Windows Installed Apps (Add or Remove Programs),
and launches the application.
"""

import os
import sys
import shutil
import zipfile
import winreg
import subprocess
import ctypes

APP_NAME = "Patte"
APP_VERSION = "2.0.0"
APP_PUBLISHER = "Patte Voice AI"
INSTALL_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Programs", "Patte")


def get_payload_zip_or_dir():
    """Find bundled Patte_payload.zip (inside onefile installer) or adjacent dist/Patte folder."""
    if getattr(sys, "frozen", False):
        bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        zip_path = os.path.join(bundle_dir, "Patte_payload.zip")
        if os.path.exists(zip_path):
            return ("zip", zip_path)
        exe_dir = os.path.dirname(sys.executable)
        adj_dir = os.path.join(exe_dir, "Patte")
        if os.path.isdir(adj_dir):
            return ("dir", adj_dir)
    adj_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "Patte")
    if os.path.isdir(adj_dir):
        return ("dir", adj_dir)
    return (None, None)


def create_shortcuts(target_exe: str, work_dir: str, icon_path: str):
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    start_menu = os.path.join(
        os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs"
    )
    shortcuts = [
        os.path.join(desktop, f"{APP_NAME}.lnk"),
        os.path.join(start_menu, f"{APP_NAME}.lnk"),
    ]
    ps_cmd = f"""
$WshShell = New-Object -ComObject WScript.Shell
foreach ($p in @('{shortcuts[0]}', '{shortcuts[1]}')) {{
    $s = $WshShell.CreateShortcut($p)
    $s.TargetPath = '{target_exe}'
    $s.WorkingDirectory = '{work_dir}'
    $s.IconLocation = '{icon_path}'
    $s.Description = 'Patte — Local AI Voice Dictation'
    $s.Save()
}}
"""
    subprocess.run(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_cmd],
        capture_output=True,
    )


def register_uninstaller(install_dir: str, target_exe: str, icon_path: str):
    """Register Patte in Windows Settings -> Installed Apps (HKCU Uninstall registry)."""
    uninstall_bat = os.path.join(install_dir, "uninstall.bat")
    with open(uninstall_bat, "w", encoding="utf-8") as f:
        f.write(f"""@echo off
taskkill /F /IM Patte.exe /T >nul 2>&1
del "%USERPROFILE%\\Desktop\\Patte.lnk" >nul 2>&1
del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Patte.lnk" >nul 2>&1
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Patte" /f >nul 2>&1
cd /d "%LOCALAPPDATA%\\Programs"
rmdir /S /Q "{install_dir}"
""")

    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Patte"
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Patte — AI Voice Dictation")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, APP_PUBLISHER)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, icon_path)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'cmd.exe /c "{uninstall_bat}"')
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
    except Exception:
        pass


def run_install(silent: bool = False):
    mode, src = get_payload_zip_or_dir()
    if not mode:
        if not silent:
            ctypes.windll.user32.MessageBoxW(
                0,
                "Could not locate Patte application files. Please run build.bat first.",
                "Patte Setup Error",
                0x10,
            )
        sys.exit(1)

    if not silent:
        resp = ctypes.windll.user32.MessageBoxW(
            0,
            f"Welcome to the Patte v{APP_VERSION} Setup Wizard.\n\n"
            f"This will install Patte on your computer at:\n{INSTALL_DIR}\n\n"
            f"• Creates Desktop & Start Menu shortcuts\n"
            f"• Registers Patte in Windows Installed Apps\n\n"
            f"Click OK to install.",
            "Patte Setup",
            0x01 | 0x40,  # MB_OKCANCEL | MB_ICONINFORMATION
        )
        if resp != 1:
            sys.exit(0)

    # Stop any running Patte instance before overwriting files
    subprocess.run(["taskkill", "/F", "/IM", "Patte.exe", "/T"], capture_output=True)

    os.makedirs(INSTALL_DIR, exist_ok=True)

    if mode == "zip":
        with zipfile.ZipFile(src, "r") as zf:
            zf.extractall(INSTALL_DIR)
    else:
        shutil.copytree(src, INSTALL_DIR, dirs_exist_ok=True)

    target_exe = os.path.join(INSTALL_DIR, "Patte.exe")
    icon_path = os.path.join(INSTALL_DIR, "_internal", "assets", "icon.ico")
    if not os.path.exists(icon_path):
        icon_path = target_exe

    create_shortcuts(target_exe, INSTALL_DIR, icon_path)
    register_uninstaller(INSTALL_DIR, target_exe, icon_path)

    if not silent:
        ctypes.windll.user32.MessageBoxW(
            0,
            "Patte has been installed successfully!\n\n"
            "• Shortcut added to your Desktop and Start Menu\n"
            "• Registered in Windows Installed Apps\n\n"
            "Patte will now launch in your System Tray. Hold Ctrl+Space anywhere to dictate!",
            "Patte Setup Complete",
            0x40,
        )
        subprocess.Popen([target_exe], cwd=INSTALL_DIR)


if __name__ == "__main__":
    is_silent = "/S" in sys.argv or "--silent" in sys.argv
    run_install(silent=is_silent)
