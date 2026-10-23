import os
import subprocess

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
appdata = os.getenv("APPDATA")
localappdata = os.getenv("LOCALAPPDATA")
start_menu = os.path.join(appdata, r"Microsoft\Windows\Start Menu\Programs")

target = os.path.join(localappdata, "Programs", "Patte", "Patte.exe")
workdir = os.path.join(localappdata, "Programs", "Patte")
icon = os.path.join(workdir, "assets", "icon.ico")
if not os.path.exists(icon):
    icon = os.path.join(workdir, "_internal", "assets", "icon.ico")

shortcuts = [
    os.path.join(desktop, "Patte.lnk"),
    os.path.join(start_menu, "Patte.lnk")
]

ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
foreach ($path in @('{shortcuts[0]}', '{shortcuts[1]}')) {{
    $s = $WshShell.CreateShortcut($path)
    $s.TargetPath = '{target}'
    $s.WorkingDirectory = '{workdir}'
    $s.IconLocation = '{icon}'
    $s.Description = 'Patte Voice Dictation'
    $s.Save()
}}
"""

subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
print("Shortcuts created for Patte successfully.")

# Clean up old WhisprFlow shortcut on Desktop if exists
old_shortcut = os.path.join(desktop, "WhisprFlow.lnk")
if os.path.exists(old_shortcut):
    try:
        os.remove(old_shortcut)
        print("Removed old WhisprFlow.lnk shortcut.")
    except Exception:
        pass
