"""
Hook personnalisé pour tkinter qui évite les problèmes TCL
"""
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
import sys

# Collecte les données tkinter
datas = []

# Trouve le chemin TCL depuis l'installation Python de base
if hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
    python_dir = sys.base_prefix
else:
    python_dir = os.path.dirname(sys.executable)

tcl_dir = os.path.join(python_dir, 'tcl')
if os.path.exists(tcl_dir):
    for root, dirs, files in os.walk(tcl_dir):
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.relpath(src, tcl_dir)
            datas.append((src, os.path.join('tcl', dst)))

# Collecte les modules cachés
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    '_tkinter'
]