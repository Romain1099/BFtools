#!/usr/bin/env python3
"""
Gestionnaire de configuration simple pour les parametres d'animation.
Version simplifiee sans emojis pour compatibilite Windows.
"""

import json
import os

CONFIG_FILE = "animation_config.json"

def load_config():
    """Charge la configuration depuis le fichier JSON."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERREUR] Fichier {CONFIG_FILE} non trouve!")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERREUR] Erreur de format JSON: {e}")
        return None

def save_config(config):
    """Sauvegarde la configuration dans le fichier JSON."""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("[OK] Configuration sauvegardee avec succes!")
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la sauvegarde: {e}")
        return False

def display_config(config):
    """Affiche la configuration actuelle de maniere lisible."""
    print("\n" + "="*60)
    print("CONFIGURATION ACTUELLE DES ANIMATIONS")
    print("="*60)
    
    print("\nPARAMETRES DE MELANGE (shuffle):")
    shuffle = config["shuffle"]
    print(f"  - Nombre de cycles de melange: {shuffle['max_shuffles']}")
    print(f"  - Duree du mouvement: {shuffle['movement_duration']}ms")
    print(f"  - Delai minimum: {shuffle['delay_min']}ms")
    print(f"  - Multiplicateur d'offset: {shuffle['offset_multiplier']}")
    print(f"  - Rayon de base: {shuffle['base_radius']}px")

def quick_presets():
    """Applique des prereglages rapides."""
    config = load_config()
    if not config:
        return
    
    print("\nPREREGLAGES RAPIDES")
    print("="*30)
    print("1. Ultra doux (animations tres lentes)")
    print("2. Doux (animations moderees)")
    print("3. Normal (equilibre)")
    print("4. Rapide (animations vives)")
    print("5. Retour")
    
    choice = input("\nVotre choix (1-5): ").strip()
    
    presets = {
        "1": {  # Ultra doux
            "max_shuffles": 6,
            "movement_duration": 800,
            "delay_min": 450,
            "offset_multiplier": 0.25,
            "base_radius": 6
        },
        "2": {  # Doux
            "max_shuffles": 7,
            "movement_duration": 650,
            "delay_min": 400,
            "offset_multiplier": 0.35,
            "base_radius": 8
        },
        "3": {  # Normal
            "max_shuffles": 8,
            "movement_duration": 500,
            "delay_min": 300,
            "offset_multiplier": 0.5,
            "base_radius": 12
        },
        "4": {  # Rapide
            "max_shuffles": 10,
            "movement_duration": 350,
            "delay_min": 200,
            "offset_multiplier": 0.7,
            "base_radius": 15
        }
    }
    
    if choice in presets:
        preset = presets[choice]
        for key, value in preset.items():
            config["shuffle"][key] = value
        
        if save_config(config):
            print(f"\n[OK] Prerereglage applique avec succes!")
        input("Appuyez sur Entree pour continuer...")

def main():
    """Fonction principale."""
    if not os.path.exists(CONFIG_FILE):
        print(f"[ERREUR] Fichier {CONFIG_FILE} non trouve!")
        print("Assurez-vous d'etre dans le bon repertoire.")
        return
    
    while True:
        print("\n" + "="*60)
        print("GESTIONNAIRE DE CONFIGURATION - LOTTERY STUDENTS")
        print("="*60)
        print("1. Appliquer un prerereglage rapide")
        print("2. Afficher la configuration actuelle")
        print("3. Quitter")
        
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == "1":
            quick_presets()
        elif choice == "2":
            config = load_config()
            if config:
                display_config(config)
                input("\nAppuyez sur Entree pour continuer...")
        elif choice == "3":
            print("\nAu revoir!")
            break
        else:
            print("\n[ERREUR] Choix invalide! Appuyez sur Entree pour continuer...")
            input()

if __name__ == "__main__":
    main()