"""
Module pour charger et injecter la configuration d'animation dans le JavaScript.
"""

import json
import os

def load_animation_config():
    """
    Charge la configuration d'animation depuis le fichier JSON.
    
    Returns:
        dict: Configuration d'animation ou configuration par défaut
    """
    config_file = "animation_config.json"
    
    # Configuration par défaut en cas de problème
    default_config = {
        "shuffle": {
            "max_shuffles": 8,
            "angle_increment": 25,
            "angle_offset": 35,
            "base_radius": 12,
            "radius_variation": 8,
            "radius_frequency": 0.15,
            "offset_multiplier": 0.5,
            "movement_duration": 500,
            "delay_min": 300,
            "delay_variation": 100,
            "pulse_probability": 0.1,
            "pulse_duration": 500
        },
        "highlight": {
            "max_rounds": 4,
            "delay_min": 400,
            "delay_variation": 200
        },
        "general": {
            "initial_display_delay": 50,
            "transition_disable_duration": 250
        }
    }
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Vérifier que toutes les clés nécessaires sont présentes
                for section in default_config:
                    if section not in config:
                        config[section] = default_config[section]
                    else:
                        for key in default_config[section]:
                            if key not in config[section]:
                                config[section][key] = default_config[section][key]
                return config
        else:
            print(f"Fichier {config_file} non trouvé, utilisation de la configuration par défaut.")
            return default_config
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        print("Utilisation de la configuration par défaut.")
        return default_config

def generate_config_js(config):
    """
    Génère le code JavaScript contenant la configuration.
    
    Args:
        config (dict): Configuration d'animation
        
    Returns:
        str: Code JavaScript avec les constantes de configuration
    """
    shuffle = config["shuffle"]
    highlight = config["highlight"]
    general = config["general"]
    
    return f"""
    // Configuration d'animation chargée depuis animation_config.json
    const ANIMATION_CONFIG = {{
        shuffle: {{
            maxShuffles: {shuffle['max_shuffles']},
            angleIncrement: {shuffle['angle_increment']},
            angleOffset: {shuffle['angle_offset']},
            baseRadius: {shuffle['base_radius']},
            radiusVariation: {shuffle['radius_variation']},
            radiusFrequency: {shuffle['radius_frequency']},
            offsetMultiplier: {shuffle['offset_multiplier']},
            movementDuration: {shuffle['movement_duration']},
            delayMin: {shuffle['delay_min']},
            delayVariation: {shuffle['delay_variation']},
            pulseProbability: {shuffle['pulse_probability']},
            pulseDuration: {shuffle['pulse_duration']}
        }},
        highlight: {{
            maxRounds: {highlight['max_rounds']},
            delayMin: {highlight['delay_min']},
            delayVariation: {highlight['delay_variation']}
        }},
        general: {{
            initialDisplayDelay: {general['initial_display_delay']},
            transitionDisableDuration: {general['transition_disable_duration']}
        }}
    }};
    """