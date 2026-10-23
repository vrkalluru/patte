Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\vrkal\.gemini\antigravity\scratch\whispr-flow"
WshShell.Run "venv\Scripts\python.exe main.py", 1, False
