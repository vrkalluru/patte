# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

project_dir = os.path.abspath(SPECPATH)
venv_site = os.path.join(project_dir, 'venv', 'Lib', 'site-packages')

# Collect ctranslate2 binaries and data
ct2_dir = os.path.join(venv_site, 'ctranslate2')
ct2_binaries = []
if os.path.isdir(ct2_dir):
    for f in os.listdir(ct2_dir):
        if f.endswith('.dll') or f.endswith('.pyd'):
            ct2_binaries.append((os.path.join(ct2_dir, f), 'ctranslate2'))

# Collect sounddevice binaries
sd_data_dir = os.path.join(venv_site, '_sounddevice_data')
sd_binaries = []
if os.path.isdir(sd_data_dir):
    for root, dirs, files in os.walk(sd_data_dir):
        for f in files:
            if f.endswith('.dll'):
                rel = os.path.relpath(root, venv_site)
                sd_binaries.append((os.path.join(root, f), rel))

datas = [
    (os.path.join(project_dir, '.env'), '.'),
    (os.path.join(project_dir, 'assets'), 'assets'),
    (os.path.join(project_dir, 'gui'), 'gui'),
]
datas += collect_data_files('faster_whisper')
datas += collect_data_files('tokenizers')

binaries = ct2_binaries + sd_binaries

hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'faster_whisper',
    'ctranslate2',
    'sounddevice',
    'soundfile',
    'pynput',
    'pynput.keyboard._win32',
    'pynput.mouse._win32',
    'pyperclip',
    'requests',
    'dotenv',
    'numpy',
    'PIL',
]

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'torch', 'IPython'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Patte',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,   # <-- NO CONSOLE WINDOW!
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(project_dir, 'assets', 'icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Patte',
)
