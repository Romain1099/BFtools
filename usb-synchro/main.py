#!/usr/bin/env python3
"""
Programme principal de synchronisation USB
"""
import sys
from pathlib import Path
import os

# Configuration TCL pour PyInstaller
if getattr(sys, 'frozen', False):
    # Si on est dans un exécutable PyInstaller
    bundle_dir = Path(sys._MEIPASS)
    tcl_dir = bundle_dir / 'tcl'
    if tcl_dir.exists():
        # Trouve le dossier tcl8.x
        tcl_versions = list(tcl_dir.glob('tcl8.*'))
        if tcl_versions:
            os.environ["TCL_LIBRARY"] = str(tcl_versions[0])
        tk_versions = list(tcl_dir.glob('tk8.*'))
        if tk_versions:
            os.environ["TK_LIBRARY"] = str(tk_versions[0])
else:
    # Mode développement - votre chemin TCL correct
    os.environ["TCL_LIBRARY"] = r"C:\Users\Utilisateur\AppData\Local\Programs\Python\Python311\tcl\tcl8.6"
# Ajoute le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.gui import SyncUSBApp

def main():
    """Point d'entrée principal"""
    try:
        app = SyncUSBApp()
        app.run()
    except KeyboardInterrupt:
        print("\nArrêt du programme")
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)

if __name__ == "__main__":
    main()