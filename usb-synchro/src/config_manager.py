"""
Gestionnaire de configuration pour le programme de synchronisation USB
"""
import json
import os
from typing import Dict, List, Optional
from pathlib import Path

class ConfigManager:
    def __init__(self):
        # Config dans le dossier du projet
        project_root = Path(__file__).parent.parent
        self.config_dir = project_root / "config"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Charge la configuration depuis le fichier"""
        default_config:Dict = {
            "default_usb": None,
            "known_drives": [],
            "sync_mappings": {
                "up": [],  # ordinateur -> USB
                "down": []  # USB -> ordinateur
            },
            "last_sync": {
                "up": None,
                "down": None
            },
            "default_filters": {
                "excluded_directories": ["__pycache__", ".git", ".vscode", "node_modules"],
                "excluded_filename_contains": ["bfpoints", ".tmp", "~$"],
                "excluded_extensions": [".log", ".cache", ".bak", ".aux"],
                "included_extensions": [],  # Si vide = tous, sinon seulement ceux-là
                "case_sensitive": False
            },
            "filters": {
                "excluded_directories": ["__pycache__", ".git", ".vscode", "node_modules"],
                "excluded_filename_contains": ["bfpoints", ".tmp", "~$"],
                "excluded_extensions": [".log", ".cache", ".bak"],
                "included_extensions": [],  # Si vide = tous, sinon seulement ceux-là
                "case_sensitive": False
            }
        }
        
        if not self.config_file.exists():
            return default_config
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                # Merge avec config par défaut pour compatibilité
                default_config.update(loaded_config)
                return default_config
        except (json.JSONDecodeError, FileNotFoundError):
            return default_config
    
    def save_config(self):
        """Sauvegarde la configuration"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def set_default_usb(self, drive_letter: str, drive_label: str):
        """Définit la clé USB par défaut"""
        self.config["default_usb"] = {
            "letter": drive_letter,
            "label": drive_label
        }
        self.save_config()
    
    def get_default_usb(self) -> Optional[Dict]:
        """Retourne la clé USB par défaut"""
        return self.config.get("default_usb")
    
    def add_known_drive(self, drive_info: Dict):
        """Ajoute une clé à la liste des clés connues"""
        known = self.config["known_drives"]
        # Évite les doublons
        for drive in known:
            if drive["letter"] == drive_info["letter"]:
                return
        
        known.append(drive_info)
        self.save_config()
    
    def get_known_drives(self) -> List[Dict]:
        """Retourne la liste des clés connues"""
        return self.config["known_drives"]
    
    def add_sync_mapping(self, direction: str, source: str, destination: str, name: str = ""):
        """Ajoute un mapping de synchronisation avec filtres par défaut"""
        # Copie les filtres par défaut
        default_filters = self.config.get("default_filters", {
            "excluded_directories": [],
            "excluded_filename_contains": [],
            "excluded_extensions": [],
            "included_extensions": [],
            "case_sensitive": False
        })
        
        mapping = {
            "name": name or f"{os.path.basename(source)} -> {os.path.basename(destination)}",
            "source": source,
            "destination": destination,
            "enabled": True,
            "filters": {
                "excluded_directories": default_filters.get("excluded_directories", []).copy(),
                "excluded_filename_contains": default_filters.get("excluded_filename_contains", []).copy(),
                "excluded_extensions": default_filters.get("excluded_extensions", []).copy(),
                "included_extensions": default_filters.get("included_extensions", []).copy(),
                "case_sensitive": default_filters.get("case_sensitive", False)
            }
        }
        
        self.config["sync_mappings"][direction].append(mapping)
        self.save_config()
    
    def get_sync_mappings(self, direction: str) -> List[Dict]:
        """Retourne les mappings pour une direction donnée"""
        return self.config["sync_mappings"].get(direction, [])
    
    def remove_sync_mapping(self, direction: str, index: int):
        """Supprime un mapping de synchronisation"""
        mappings = self.config["sync_mappings"][direction]
        if 0 <= index < len(mappings):
            mappings.pop(index)
            self.save_config()
    
    def toggle_mapping_enabled(self, direction: str, index: int):
        """Active/désactive un mapping"""
        mappings = self.config["sync_mappings"][direction]
        if 0 <= index < len(mappings):
            mappings[index]["enabled"] = not mappings[index]["enabled"]
            self.save_config()
    
    def update_last_sync(self, direction: str):
        """Met à jour la date de dernière synchronisation"""
        from datetime import datetime
        self.config["last_sync"][direction] = datetime.now().isoformat()
        self.save_config()
    
    def get_last_sync(self, direction: str) -> Optional[str]:
        """Retourne la date de dernière synchronisation"""
        return self.config["last_sync"].get(direction)
    
    def get_filters(self) -> Dict:
        """Retourne la configuration des filtres"""
        return self.config.get("filters", {})
    
    def update_filters(self, filters: Dict):
        """Met à jour la configuration des filtres"""
        self.config["filters"].update(filters)
        self.save_config()
    
    def add_excluded_directory(self, directory: str):
        """Ajoute un répertoire à exclure"""
        excluded = self.config["filters"]["excluded_directories"]
        if directory not in excluded:
            excluded.append(directory)
            self.save_config()
    
    def remove_excluded_directory(self, directory: str):
        """Supprime un répertoire des exclusions"""
        excluded = self.config["filters"]["excluded_directories"]
        if directory in excluded:
            excluded.remove(directory)
            self.save_config()
    
    def add_excluded_filename_contains(self, text: str):
        """Ajoute un texte à exclure dans les noms de fichiers"""
        excluded = self.config["filters"]["excluded_filename_contains"]
        if text not in excluded:
            excluded.append(text)
            self.save_config()
    
    def remove_excluded_filename_contains(self, text: str):
        """Supprime un texte des exclusions de noms de fichiers"""
        excluded = self.config["filters"]["excluded_filename_contains"]
        if text in excluded:
            excluded.remove(text)
            self.save_config()
    
    def add_excluded_extension(self, extension: str):
        """Ajoute une extension à exclure"""
        if not extension.startswith('.'):
            extension = '.' + extension
        excluded = self.config["filters"]["excluded_extensions"]
        if extension not in excluded:
            excluded.append(extension)
            self.save_config()
    
    def remove_excluded_extension(self, extension: str):
        """Supprime une extension des exclusions"""
        if not extension.startswith('.'):
            extension = '.' + extension
        excluded = self.config["filters"]["excluded_extensions"]
        if extension in excluded:
            excluded.remove(extension)
            self.save_config()
    
    def add_included_extension(self, extension: str):
        """Ajoute une extension à inclure (whitelist)"""
        if not extension.startswith('.'):
            extension = '.' + extension
        included = self.config["filters"]["included_extensions"]
        if extension not in included:
            included.append(extension)
            self.save_config()
    
    def remove_included_extension(self, extension: str):
        """Supprime une extension des inclusions"""
        if not extension.startswith('.'):
            extension = '.' + extension
        included = self.config["filters"]["included_extensions"]
        if extension in included:
            included.remove(extension)
            self.save_config()
    
    def update_mapping_filters(self, direction: str, mapping_index: int, filters: Dict):
        """Met à jour les filtres d'un mapping spécifique"""
        mappings = self.config["sync_mappings"][direction]
        if 0 <= mapping_index < len(mappings):
            # S'assure que le mapping a une section filters
            if "filters" not in mappings[mapping_index]:
                mappings[mapping_index]["filters"] = {
                    "excluded_directories": [],
                    "excluded_filename_contains": [],
                    "excluded_extensions": [],
                    "included_extensions": [],
                    "case_sensitive": False
                }
            mappings[mapping_index]["filters"].update(filters)
            self.save_config()
    
    def get_mapping_filters(self, direction: str, mapping_index: int) -> Dict:
        """Récupère les filtres d'un mapping spécifique"""
        mappings = self.config["sync_mappings"][direction]
        if 0 <= mapping_index < len(mappings):
            mapping = mappings[mapping_index]
            # S'assure que le mapping a des filtres par défaut
            if "filters" not in mapping:
                mapping["filters"] = {
                    "excluded_directories": [],
                    "excluded_filename_contains": [],
                    "excluded_extensions": [],
                    "included_extensions": [],
                    "case_sensitive": False
                }
                self.save_config()
            return mapping["filters"]
        return {}
    
    def add_mapping_filter_item(self, direction: str, mapping_index: int, filter_type: str, item: str):
        """Ajoute un élément de filtre à un mapping"""
        mappings = self.config["sync_mappings"][direction]
        if 0 <= mapping_index < len(mappings):
            filters = self.get_mapping_filters(direction, mapping_index)
            
            # Traite les extensions
            if filter_type in ["excluded_extensions", "included_extensions"]:
                if not item.startswith('.'):
                    item = '.' + item
            
            if item not in filters[filter_type]:
                filters[filter_type].append(item)
                self.save_config()
    
    def remove_mapping_filter_item(self, direction: str, mapping_index: int, filter_type: str, item: str):
        """Supprime un élément de filtre d'un mapping"""
        mappings = self.config["sync_mappings"][direction]
        if 0 <= mapping_index < len(mappings):
            filters = self.get_mapping_filters(direction, mapping_index)
            
            # Traite les extensions
            if filter_type in ["excluded_extensions", "included_extensions"]:
                if not item.startswith('.'):
                    item = '.' + item
            
            if item in filters[filter_type]:
                filters[filter_type].remove(item)
                self.save_config()
    
    def get_default_filters(self) -> Dict:
        """Retourne les filtres par défaut"""
        return self.config.get("default_filters", {})
    
    def update_default_filters(self, filters: Dict):
        """Met à jour les filtres par défaut"""
        if "default_filters" not in self.config:
            self.config["default_filters"] = {}
        self.config["default_filters"].update(filters)
        self.save_config()
    
    def ensure_all_mappings_have_filters(self):
        """S'assure que tous les mappings existants ont des filtres (vides si pas définis)"""
        updated = False
        
        for direction in ["up", "down"]:
            mappings = self.config["sync_mappings"].get(direction, [])
            for mapping in mappings:
                if "filters" not in mapping:
                    # Ajoute des filtres vides (les filtres globaux seront appliqués via _merge_filters)
                    mapping["filters"] = {
                        "excluded_directories": [],
                        "excluded_filename_contains": [],
                        "excluded_extensions": [],
                        "included_extensions": [],
                        "case_sensitive": False
                    }
                    updated = True
        
        if updated:
            self.save_config()