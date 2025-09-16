"""
Gestionnaire de logs avec rotation et nettoyage automatique
"""
import logging
from pathlib import Path
from datetime import datetime, timedelta
import os
from typing import Optional, Callable

class SyncLogger:
    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent
        
        self.logs_dir = project_root / "config" / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Nettoyage automatique des anciens logs
        self._cleanup_old_logs()
        
        # Configuration du logger
        self.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.logs_dir / f"sync_{self.current_session}.log"
        
        self.logger = logging.getLogger('SyncUSB')
        self.logger.setLevel(logging.INFO)
        
        # Handler pour fichier
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Format des logs
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Évite les doublons de handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
        
        # Callback pour l'interface
        self.ui_callback: Optional[Callable] = None
    
    def set_ui_callback(self, callback: Callable[[str], None]):
        """Définit la callback pour afficher dans l'interface"""
        self.ui_callback = callback
    
    def log(self, message: str, level: str = 'INFO'):
        """Log un message dans le fichier et l'interface"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        
        # Log dans le fichier
        if level == 'ERROR':
            self.logger.error(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        # Affichage dans l'interface
        if self.ui_callback:
            self.ui_callback(formatted_message)
    
    def log_sync_start(self, direction: str, mappings_count: int):
        """Log le début d'une synchronisation"""
        self.log(f"🚀 Début synchronisation {direction.upper()} - {mappings_count} mapping(s)")
        self.log(f"📁 Session: {self.current_session}")
    
    def log_sync_end(self, results: dict):
        """Log la fin d'une synchronisation"""
        self.log(f"✅ Synchronisation terminée:")
        self.log(f"   📈 {results['success']} fichiers copiés")
        self.log(f"   ⏭️ {results['skipped']} fichiers ignorés")
        if results['errors'] > 0:
            self.log(f"   ❌ {results['errors']} erreurs")
            for error in results.get('error_details', []):
                self.log(f"      • {error}", 'ERROR')
    
    def log_mapping(self, mapping: dict, action: str):
        """Log une action sur un mapping"""
        self.log(f"📂 {action}: {mapping['name']}")
        self.log(f"   Source: {mapping['source']}")
        self.log(f"   Destination: {mapping['destination']}")
    
    def _cleanup_old_logs(self):
        """Supprime les logs de plus de 7 jours"""
        if not self.logs_dir.exists():
            return
        
        cutoff_date = datetime.now() - timedelta(days=7)
        deleted_count = 0
        
        for log_file in self.logs_dir.glob("sync_*.log"):
            try:
                # Parse la date depuis le nom de fichier
                date_str = log_file.stem.replace('sync_', '')[:8]
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
                    
            except (ValueError, IndexError):
                # Si le parsing échoue, garde le fichier
                continue
        
        if deleted_count > 0:
            print(f"🗑️ {deleted_count} anciens logs supprimés")
    
    def get_recent_logs(self, days: int = 7) -> list:
        """Retourne la liste des logs récents"""
        if not self.logs_dir.exists():
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_logs = []
        
        for log_file in sorted(self.logs_dir.glob("sync_*.log"), reverse=True):
            try:
                date_str = log_file.stem.replace('sync_', '')[:8]
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                if file_date >= cutoff_date:
                    recent_logs.append({
                        'file': log_file,
                        'date': file_date,
                        'size': log_file.stat().st_size
                    })
                    
            except (ValueError, IndexError):
                continue
        
        return recent_logs