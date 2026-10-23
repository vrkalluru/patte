$WshShell = New-Object -ComObject WScript.Shell
$ProjectDir = "C:\Users\vrkal\.gemini\antigravity\scratch\whispr-flow"
$PythonwPath = "$ProjectDir\venv\Scripts\pythonw.exe"
$IconPath = "$ProjectDir\assets\icon.ico"
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)

# 1. Create Desktop Shortcut
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\WhisprFlow.lnk")
$Shortcut.TargetPath = $PythonwPath
$Shortcut.Arguments = "main.py"
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.IconLocation = "$IconPath, 0"
$Shortcut.Description = "WhisprFlow — Push-to-Talk Speech-to-Text"
$Shortcut.Save()

Write-Host "Created Desktop Shortcut: $DesktopPath\WhisprFlow.lnk"

# 2. Create Start Menu Shortcut
$StartMenuPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::StartMenu) + "\Programs"
$StartShortcut = $WshShell.CreateShortcut("$StartMenuPath\WhisprFlow.lnk")
$StartShortcut.TargetPath = $PythonwPath
$StartShortcut.Arguments = "main.py"
$StartShortcut.WorkingDirectory = $ProjectDir
$StartShortcut.IconLocation = "$IconPath, 0"
$StartShortcut.Description = "WhisprFlow — Push-to-Talk Speech-to-Text"
$StartShortcut.Save()

Write-Host "Created Start Menu Shortcut: $StartMenuPath\WhisprFlow.lnk"
