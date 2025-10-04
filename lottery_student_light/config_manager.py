#!/usr/bin/env python3
"""
Gestionnaire de configuration pour les paramètres d'animation.
Permet de modifier interactivement les paramètres d'animation via le terminal.
"""

import json
import os
import sys

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
        print("✅ Configuration sauvegardée avec succès!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False

def display_config(config):
    """Affiche la configuration actuelle de manière lisible."""
    print("\n" + "="*60)
    print("🎨 CONFIGURATION ACTUELLE DES ANIMATIONS")
    print("="*60)
    
    print("\n📦 PARAMÈTRES DE MÉLANGE (shuffle):")
    shuffle = config["shuffle"]
    print(f"  • Nombre de cycles de mélange: {shuffle['max_shuffles']}")
    print(f"  • Incrément d'angle: {shuffle['angle_increment']}°")
    print(f"  • Décalage d'angle: {shuffle['angle_offset']}°")
    print(f"  • Rayon de base: {shuffle['base_radius']}px")
    print(f"  • Variation du rayon: {shuffle['radius_variation']}px")
    print(f"  • Fréquence variation: {shuffle['radius_frequency']}")
    print(f"  • Multiplicateur d'offset: {shuffle['offset_multiplier']}")
    print(f"  • Durée du mouvement: {shuffle['movement_duration']}ms")
    print(f"  • Délai minimum: {shuffle['delay_min']}ms")
    print(f"  • Variation du délai: {shuffle['delay_variation']}ms")
    print(f"  • Probabilité d'effet pulse: {shuffle['pulse_probability']}")
    print(f"  • Durée de l'effet pulse: {shuffle['pulse_duration']}ms")
    
    print("\n🎯 PARAMÈTRES DE SURBRILLANCE (highlight):")
    highlight = config["highlight"]
    print(f"  • Nombre de tours: {highlight['max_rounds']}")
    print(f"  • Délai minimum: {highlight['delay_min']}ms")
    print(f"  • Variation du délai: {highlight['delay_variation']}ms")
    
    print("\n⚙️ PARAMÈTRES GÉNÉRAUX:")
    general = config["general"]
    print(f"  • Délai d'affichage initial: {general['initial_display_delay']}ms")
    print(f"  • Durée désactivation transitions: {general['transition_disable_duration']}ms")

def modify_value(config, path, description, current_value, value_type=float):
    """Modifie une valeur de configuration."""
    print(f"\n🔧 {description}")
    print(f"   Valeur actuelle: {current_value}")
    
    while True:
        try:
            new_value = input(f"   Nouvelle valeur (Entrée pour garder {current_value}): ").strip()
            
            if not new_value:
                return current_value
                
            if value_type == int:
                return int(new_value)
            elif value_type == float:
                return float(new_value)
            else:
                return new_value
                
        except ValueError:
            print("   ❌ Valeur invalide! Essayez encore.")

def interactive_config_editor():
    """Interface interactive pour modifier la configuration."""
    config = load_config()
    if not config:
        return
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_config(config)
        
        print("\n" + "="*60)
        print("🛠️  MENU DE CONFIGURATION")
        print("="*60)
        print("1. Modifier les paramètres de mélange (shuffle)")
        print("2. Modifier les paramètres de surbrillance (highlight)")
        print("3. Modifier les paramètres généraux")
        print("4. Sauvegarder et quitter")
        print("5. Quitter sans sauvegarder")
        
        choice = input("\nVotre choix (1-5): ").strip()
        
        if choice == "1":
            modify_shuffle_params(config)
        elif choice == "2":
            modify_highlight_params(config)
        elif choice == "3":
            modify_general_params(config)
        elif choice == "4":
            if save_config(config):
                print("\n✅ Configuration sauvegardée! Appuyez sur Entrée pour continuer...")
                input()
                break
        elif choice == "5":
            print("\n👋 Configuration non sauvegardée. Au revoir!")
            break
        else:
            print("\n❌ Choix invalide! Appuyez sur Entrée pour continuer...")
            input()

def modify_shuffle_params(config):
    """Modifie les paramètres de mélange."""
    shuffle = config["shuffle"]
    
    print("\n🎲 MODIFICATION DES PARAMÈTRES DE MÉLANGE")
    print("=" * 50)
    
    shuffle["max_shuffles"] = modify_value(
        config, "shuffle.max_shuffles", 
        "Nombre de cycles de mélange (plus = plus long)", 
        shuffle["max_shuffles"], int
    )
    
    shuffle["movement_duration"] = modify_value(
        config, "shuffle.movement_duration",
        "Durée de chaque mouvement en ms (plus = plus lent)",
        shuffle["movement_duration"], int
    )
    
    shuffle["delay_min"] = modify_value(
        config, "shuffle.delay_min",
        "Délai minimum entre mouvements en ms",
        shuffle["delay_min"], int
    )
    
    shuffle["offset_multiplier"] = modify_value(
        config, "shuffle.offset_multiplier",
        "Multiplicateur d'amplitude (0.1-1.0, plus petit = plus doux)",
        shuffle["offset_multiplier"], float
    )
    
    shuffle["base_radius"] = modify_value(
        config, "shuffle.base_radius",
        "Rayon de base des mouvements en pixels",
        shuffle["base_radius"], int
    )

def modify_highlight_params(config):
    """Modifie les paramètres de surbrillance."""
    highlight = config["highlight"]
    
    print("\n✨ MODIFICATION DES PARAMÈTRES DE SURBRILLANCE")
    print("=" * 50)
    
    highlight["max_rounds"] = modify_value(
        config, "highlight.max_rounds",
        "Nombre de tours de surbrillance",
        highlight["max_rounds"], int
    )
    
    highlight["delay_min"] = modify_value(
        config, "highlight.delay_min",
        "Délai minimum entre surbrillances en ms",
        highlight["delay_min"], int
    )

def modify_general_params(config):
    """Modifie les paramètres généraux."""
    general = config["general"]
    
    print("\n⚙️ MODIFICATION DES PARAMÈTRES GÉNÉRAUX")
    print("=" * 50)
    
    general["initial_display_delay"] = modify_value(
        config, "general.initial_display_delay",
        "Délai d'initialisation en ms",
        general["initial_display_delay"], int
    )

def quick_presets():
    """Applique des préréglages rapides."""
    config = load_config()
    if not config:
        return
    
    print("\n🎨 PRÉRÉGLAGES RAPIDES")
    print("="*30)
    print("1. Ultra doux (animations très lentes)")
    print("2. Doux (animations modérées)")
    print("3. Normal (équilibré)")
    print("4. Rapide (animations vives)")
    print("5. Retour")
    
    choice = input("\nVotre choix (1-5): ").strip()
    
    presets = {
        "1": {  # Ultra doux
            "max_shuffles": 6,
            "movement_duration": 800,
            "delay_min": 400,
            "offset_multiplier": 0.3,
            "base_radius": 8
        },
        "2": {  # Doux
            "max_shuffles": 8,
            "movement_duration": 600,
            "delay_min": 350,
            "offset_multiplier": 0.4,
            "base_radius": 10
        },
        "3": {  # Normal
            "max_shuffles": 10,
            "movement_duration": 500,
            "delay_min": 300,
            "offset_multiplier": 0.5,
            "base_radius": 12
        },
        "4": {  # Rapide
            "max_shuffles": 12,
            "movement_duration": 300,
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
            print(f"\n✅ Préréglage appliqué avec succès!")
        input("Appuyez sur Entrée pour continuer...")

def main():
    """Fonction principale."""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Fichier {CONFIG_FILE} non trouvé!")
        print("Assurez-vous d'être dans le bon répertoire.")
        return
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🎮 GESTIONNAIRE DE CONFIGURATION - LOTTERY STUDENTS")
        print("="*60)
        print("1. Modifier la configuration interactive")
        print("2. Appliquer un préréglage rapide")
        print("3. Afficher la configuration actuelle")
        print("4. Quitter")
        
        choice = input("\nVotre choix (1-4): ").strip()
        
        if choice == "1":
            interactive_config_editor()
        elif choice == "2":
            quick_presets()
        elif choice == "3":
            config = load_config()
            if config:
                display_config(config)
                input("\nAppuyez sur Entrée pour continuer...")
        elif choice == "4":
            print("\n👋 Au revoir!")
            break
        else:
            print("\n❌ Choix invalide! Appuyez sur Entrée pour continuer...")
            input()

if __name__ == "__main__":
    main()