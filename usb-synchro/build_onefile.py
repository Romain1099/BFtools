#!/usr/bin/env python3
"""
Script pour créer un exécutable onefile avec PyInstaller
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Installe PyInstaller si nécessaire"""
    try:
        import PyInstaller
        print("PyInstaller déjà installé")
    except ImportError:
        print("Installation de PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

def build_onefile():
    """Construit l'exécutable onefile"""
    print("Construction de l'exécutable onefile...")
    
    # Chemins Python - cherche le vrai Python, pas le venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # On est dans un venv, utilise l'installation Python de base
        python_dir = Path(sys.base_prefix)
    else:
        python_dir = Path(sys.executable).parent
    
    tcl_dir = python_dir / "tcl"
    
    print(f"Chemin Python: {python_dir}")
    print(f"Chemin TCL: {tcl_dir}")
    print(f"TCL existe: {tcl_dir.exists()}")
    
    # Commande PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--console",  # Mode console pour debug
        "--name=SyncUSB",
        "--icon=icon.ico",  # Si vous avez une icône
        "--add-data=src;src",
        "--additional-hooks-dir=.",  # Utilise notre hook personnalisé
        "--hidden-import=customtkinter",
        "--hidden-import=psutil", 
        "--hidden-import=PIL",
        "--collect-submodules=customtkinter",
        "--noupx",  # Désactive UPX qui peut causer des problèmes
        "--distpath=dist",
        "--workpath=build",
        "main.py"
    ]
    
    # TCL est maintenant géré par le hook personnalisé
    
    # Retire l'icône si elle n'existe pas
    if not Path("icon.ico").exists():
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Construction réussie!")
        print(f"Exécutable créé dans: dist/SyncUSB.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la construction: {e}")
        print(f"Sortie d'erreur: {e.stderr}")
        return False
    
    return True

def clean_build():
    """Nettoie les fichiers de construction"""
    print("Nettoyage des fichiers temporaires...")
    
    for folder in ["build", "__pycache__"]:
        if Path(folder).exists():
            shutil.rmtree(folder)
            print(f"Supprimé: {folder}")
    
    # Supprime les fichiers .pyc récursivement
    for pyc_file in Path(".").rglob("*.pyc"):
        pyc_file.unlink()
    
    # Supprime les dossiers __pycache__ récursivement
    for pycache_dir in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache_dir)

def main():
    """Fonction principale"""
    print("=== Construction SyncUSB OnFile ===")
    
    # Vérification de l'environnement
    if not Path("main.py").exists():
        print("Erreur: main.py introuvable")
        sys.exit(1)
    
    if not Path("src").exists():
        print("Erreur: dossier src/ introuvable")
        sys.exit(1)
    
    try:
        # Installation des dépendances
        install_pyinstaller()
        
        # Construction
        if build_onefile():
            print("\n✓ Construction terminée avec succès!")
            print("L'exécutable se trouve dans le dossier dist/")
        else:
            print("\n✗ Échec de la construction")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nArrêt par l'utilisateur")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        sys.exit(1)
    finally:
        # Nettoyage
        clean_build()

if __name__ == "__main__":
    main()