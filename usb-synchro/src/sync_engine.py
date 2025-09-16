"""
Moteur de synchronisation pour copier les fichiers
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Callable, Optional
from datetime import datetime

from .logger import SyncLogger

class SyncEngine:
    def __init__(self, config_manager=None):
        self.progress_callback: Optional[Callable] = None
        self.logger = SyncLogger()
        self.config_manager = config_manager
        
    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """Définit la callback pour le progrès (current, total, current_file)"""
        self.progress_callback = callback
        
    def set_log_callback(self, callback: Callable[[str], None]):
        """Définit la callback pour les logs UI"""
        self.logger.set_ui_callback(callback)
    
    def _log(self, message: str, level: str = 'INFO'):
        """Log un message"""
        self.logger.log(message, level)
    
    def _should_skip_file(self, file_path: Path, mapping_filters: Dict = None) -> bool:
        """Détermine si un fichier doit être ignoré selon les filtres configurés"""
        if not mapping_filters or not self.config_manager:
            return False
        
        # Fusionne les filtres : global + local (local prioritaire)
        filters = self._merge_filters(mapping_filters)
        case_sensitive = filters.get("case_sensitive", False)
        
        # Nom du fichier pour comparaison
        filename = file_path.name if case_sensitive else file_path.name.lower()
        extension = file_path.suffix if case_sensitive else file_path.suffix.lower()
        
        # 1. Vérifie si le fichier contient des chaînes exclues
        excluded_contains = filters.get("excluded_filename_contains", [])
        for exclude_text in excluded_contains:
            compare_text = exclude_text if case_sensitive else exclude_text.lower()
            if compare_text in filename:
                self._log(f"🚫 Fichier ignoré (contient '{exclude_text}'): {file_path.name}")
                return True
        
        # 2. Vérifie les extensions exclues
        excluded_extensions = filters.get("excluded_extensions", [])
        for ext in excluded_extensions:
            compare_ext = ext if case_sensitive else ext.lower()
            if extension == compare_ext:
                self._log(f"🚫 Fichier ignoré (extension '{ext}'): {file_path.name}")
                return True
        
        # 3. Vérifie les extensions incluses (whitelist)
        included_extensions = filters.get("included_extensions", [])
        if included_extensions:  # Si la whitelist n'est pas vide
            extension_allowed = False
            for ext in included_extensions:
                compare_ext = ext if case_sensitive else ext.lower()
                if extension == compare_ext:
                    extension_allowed = True
                    break
            
            if not extension_allowed:
                self._log(f"🚫 Fichier ignoré (extension non autorisée): {file_path.name}")
                return True
        
        return False
    
    def _should_skip_directory(self, dir_path: Path, mapping_filters: Dict = None) -> bool:
        """Détermine si un répertoire doit être ignoré"""
        if not mapping_filters or not self.config_manager:
            return False
        
        # Fusionne les filtres : global + local (local prioritaire)
        filters = self._merge_filters(mapping_filters)
        case_sensitive = filters.get("case_sensitive", False)
        
        dir_name = dir_path.name if case_sensitive else dir_path.name.lower()
        
        excluded_directories = filters.get("excluded_directories", [])
        for exclude_dir in excluded_directories:
            compare_dir = exclude_dir if case_sensitive else exclude_dir.lower()
            if dir_name == compare_dir:
                self._log(f"🚫 Répertoire ignoré: {dir_path.name}")
                return True
        
        return False
    
    def _merge_filters(self, mapping_filters: Dict) -> Dict:
        """Fusionne les filtres globaux et locaux avec priorité locale"""
        if not self.config_manager:
            return mapping_filters
        
        # Récupère les filtres par défaut (globaux)
        global_filters = self.config_manager.get_default_filters()
        
        # Prépare le résultat avec les filtres globaux
        merged_filters = {
            "excluded_directories": global_filters.get("excluded_directories", []).copy(),
            "excluded_filename_contains": global_filters.get("excluded_filename_contains", []).copy(),
            "excluded_extensions": global_filters.get("excluded_extensions", []).copy(),
            "included_extensions": global_filters.get("included_extensions", []).copy(),
            "case_sensitive": global_filters.get("case_sensitive", False)
        }
        
        # Applique les filtres locaux avec priorité
        local_filters = mapping_filters or {}
        
        # Sensibilité à la casse : local override global
        if "case_sensitive" in local_filters:
            merged_filters["case_sensitive"] = local_filters["case_sensitive"]
        
        # Extensions incluses : si local défini, ignore global (whitelist locale prioritaire)
        if local_filters.get("included_extensions"):
            merged_filters["included_extensions"] = local_filters["included_extensions"].copy()
        
        # Extensions exclues : fusionne global + local, mais local peut "débloquer" des globales
        local_excluded_ext = local_filters.get("excluded_extensions", [])
        local_included_ext = merged_filters["included_extensions"]
        
        # Commence avec les exclusions globales
        merged_excluded_ext = merged_filters["excluded_extensions"].copy()
        
        # Ajoute les exclusions locales
        for ext in local_excluded_ext:
            if ext not in merged_excluded_ext:
                merged_excluded_ext.append(ext)
        
        # Si une extension est dans included_extensions, elle ne peut pas être exclue
        merged_excluded_ext = [ext for ext in merged_excluded_ext if ext not in local_included_ext]
        merged_filters["excluded_extensions"] = merged_excluded_ext
        
        # Répertoires exclus : fusionne global + local
        local_excluded_dirs = local_filters.get("excluded_directories", [])
        for dir_name in local_excluded_dirs:
            if dir_name not in merged_filters["excluded_directories"]:
                merged_filters["excluded_directories"].append(dir_name)
        
        # Fichiers contenant : fusionne global + local
        local_excluded_contains = local_filters.get("excluded_filename_contains", [])
        for contains in local_excluded_contains:
            if contains not in merged_filters["excluded_filename_contains"]:
                merged_filters["excluded_filename_contains"].append(contains)
        
        return merged_filters
    
    def _sync_directory_recursive(self, current_dir: Path, dest_base: Path, source_base: Path, 
                                 mapping_filters: Dict, results: Dict, current_file: int, 
                                 total_files: int, dry_run: bool) -> int:
        """Synchronise un répertoire de manière récursive avec filtrage"""
        if not current_dir.exists() or not current_dir.is_dir():
            return current_file
        
        # Liste le contenu du répertoire actuel
        try:
            items = list(current_dir.iterdir())
        except (PermissionError, FileNotFoundError):
            self._log(f"🚫 Accès refusé: {current_dir}", 'ERROR')
            return current_file
        
        for item in items:
            try:
                if item.is_dir():
                    # Vérifie si le répertoire doit être ignoré
                    if self._should_skip_directory(item, mapping_filters):
                        continue
                    
                    # Récursion dans le sous-répertoire
                    current_file = self._sync_directory_recursive(
                        item, dest_base, source_base, mapping_filters, 
                        results, current_file, total_files, dry_run
                    )
                
                elif item.is_file():
                    # Filtrage des fichiers
                    if self._should_skip_file(item, mapping_filters):
                        continue
                    
                    current_file += 1
                    rel_path = item.relative_to(source_base)
                    dst_file = dest_base / rel_path
                    
                    if self.progress_callback:
                        self.progress_callback(current_file, total_files, str(item))
                    
                    # Vérifie si le fichier doit être copié
                    should_copy = True
                    if dst_file.exists():
                        src_mtime = item.stat().st_mtime
                        dst_mtime = dst_file.stat().st_mtime
                        
                        # Source plus récente que destination = doit copier
                        if src_mtime > dst_mtime:
                            should_copy = True
                            src_time = datetime.fromtimestamp(src_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            dst_time = datetime.fromtimestamp(dst_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            self._log(f"📝 {rel_path} - Source plus récente ({src_time} > {dst_time})")
                        else:
                            should_copy = False
                            results["skipped"] += 1
                            self._log(f"⏭️ {rel_path} - Fichier à jour, ignoré")
                    
                    if should_copy:
                        if not dry_run:
                            dst_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, dst_file)
                        results["success"] += 1
                        self._log(f"✅ Copié: {rel_path}")
            
            except (PermissionError, FileNotFoundError) as e:
                self._log(f"🚫 Erreur d'accès à {item}: {str(e)}", 'ERROR')
                continue
        
        return current_file
    
    def sync_directories(self, mappings: List[Dict], dry_run: bool = False, direction: str = "unknown") -> Dict:
        """Synchronise selon les mappings donnés"""
        results = {
            "success": 0,
            "errors": 0,
            "skipped": 0,
            "total_files": 0,
            "error_details": []
        }
        
        # Log début de sync
        enabled_mappings = [m for m in mappings if m.get("enabled", True)]
        self.logger.log_sync_start(direction, len(enabled_mappings))
        
        # Calcule le nombre total de fichiers
        total_files = 0
        for mapping in enabled_mappings:
            source_path = Path(mapping["source"])
            if source_path.exists():
                total_files += sum(1 for _ in source_path.rglob("*") if _.is_file())
        
        results["total_files"] = total_files
        current_file = 0
        
        for mapping in enabled_mappings:
            source = Path(mapping["source"])
            destination = Path(mapping["destination"])
            mapping_filters = mapping.get("filters", {})
            
            self.logger.log_mapping(mapping, "Synchronisation")
            
            if not source.exists():
                error_msg = f"Source n'existe pas: {source}"
                self._log(error_msg, 'ERROR')
                results["errors"] += 1
                results["error_details"].append(error_msg)
                continue
            
            try:
                # Crée le répertoire de destination
                if not dry_run:
                    destination.mkdir(parents=True, exist_ok=True)
                
                # Synchronise récursivement avec filtrage intelligent
                current_file = self._sync_directory_recursive(source, destination, source, mapping_filters, 
                                                             results, current_file, total_files, dry_run)
                
            except Exception as e:
                error_msg = f"Erreur lors de la sync de {mapping['name']}: {str(e)}"
                self._log(error_msg, 'ERROR')
                results["errors"] += 1
                results["error_details"].append(error_msg)
        
        # Log fin de sync
        self.logger.log_sync_end(results)
        
        return results