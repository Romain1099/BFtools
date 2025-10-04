# -*- mode: python ; coding: utf-8 -*-
"""
Fichier de spécification PyInstaller pour Lottery Sessions
Génère un executable Windows standalone
"""

import os
from pathlib import Path

block_cipher = None

# Chemins
BASE_DIR = Path(os.path.abspath(SPECPATH))
TEMPLATES_DIR = BASE_DIR / 'templates'
STATIC_DIR = BASE_DIR / 'static'
STATIC_MODULES_DIR = BASE_DIR / 'static' / 'modules'
BACKEND_DIR = BASE_DIR / 'backend'

a = Analysis(
    ['lottery_sessions.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=[
        (str(TEMPLATES_DIR), 'templates'),
        (str(STATIC_DIR), 'static'),
        (str(STATIC_MODULES_DIR), 'static/modules'),
        (str(BACKEND_DIR), 'backend'),
    ],
    hiddenimports=[
        'flask',
        'flask_cors',
        'csv',
        'webbrowser',
        'threading',
        'socket',
        'signal',
        'shutil',
        'backend.csv_manager',
        'backend.session_tracker',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'tkinter',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='lottery_sessions',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Mode fenêtré (pas de console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Vous pouvez ajouter un fichier .ico ici
    version_file=None,
)