"""
Module pour détecter et gérer les clés USB
"""
import psutil
import os
from typing import List, Dict, Optional

class USBDetector:
    def __init__(self):
        self.known_drives = set()
        
    def get_usb_drives(self) -> List[Dict[str, str]]:
        """Retourne la liste des clés USB connectées"""
        usb_drives = []
        
        # Récupère tous les disques montés
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            # Filtre les drives amovibles (USB)
            if 'removable' in partition.opts or partition.fstype in ['FAT32', 'exFAT', 'NTFS']:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Vérifie que c'est accessible et pas trop gros (critère USB)
                    if usage.total < 2 * 1024**4:  # Moins de 2TB = probablement USB
                        drive_info = {
                            'letter': partition.device,
                            'label': self._get_drive_label(partition.device),
                            'size': usage.total,
                            'free': usage.free,
                            'mountpoint': partition.mountpoint
                        }
                        usb_drives.append(drive_info)
                        
                except (PermissionError, FileNotFoundError):
                    continue
                    
        return usb_drives
    
    def _get_drive_label(self, device: str) -> str:
        """Récupère le label d'un drive"""
        try:
            import win32api
            return win32api.GetVolumeInformation(device)[0] or f"Drive {device[0]}"
        except:
            return f"Drive {device[0]}"
    
    def monitor_usb_changes(self) -> Dict[str, List[str]]:
        """Détecte les changements de clés USB"""
        current_drives = {drive['letter'] for drive in self.get_usb_drives()}
        
        added = current_drives - self.known_drives
        removed = self.known_drives - current_drives
        
        self.known_drives = current_drives
        
        return {
            'added': list(added),
            'removed': list(removed)
        }