"""
Interface graphique principale avec customtkinter
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
from typing import Dict, List, Optional

from .usb_detector import USBDetector
from .config_manager import ConfigManager
from .sync_engine import SyncEngine

class SyncUSBApp:
    def __init__(self):
        # Initialisation des composants
        self.usb_detector = USBDetector()
        self.config_manager = ConfigManager()
        
        # S'assure que tous les mappings existants ont des filtres
        self.config_manager.ensure_all_mappings_have_filters()
        
        self.sync_engine = SyncEngine(self.config_manager)
        
        # Configuration du thème
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("Synchronisation USB")
        
        # Variables
        self.selected_usb = tk.StringVar()
        self.sync_in_progress = False
        
        self.setup_ui()
        self.refresh_usb_drives()
        
        # Callbacks pour le sync engine
        self.sync_engine.set_progress_callback(self.update_progress)
        self.sync_engine.set_log_callback(self.add_log)
        
        # Force le plein écran après initialisation
        self.root.after(100, lambda: self.root.state('zoomed'))
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Onglets principaux
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Onglets
        tab_usb = self.tabview.add("🔌 USB")
        tab_up = self.tabview.add("⬆️ Sync UP")
        tab_down = self.tabview.add("⬇️ Sync DOWN")
        tab_filters = self.tabview.add("🔧 Filtres")
        tab_logs = self.tabview.add("📋 Logs")
        
        self.setup_usb_tab(tab_usb)
        self.setup_sync_tab(tab_up, "up")
        self.setup_sync_tab(tab_down, "down")
        self.setup_filters_tab(tab_filters)
        self.setup_logs_tab(tab_logs)
    
    def setup_usb_tab(self, parent):
        """Configure l'onglet de gestion USB"""
        # Section sélection USB
        usb_frame = ctk.CTkFrame(parent)
        usb_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(usb_frame, text="🔌 Clés USB détectées", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Liste des USB
        self.usb_listbox = ctk.CTkScrollableFrame(usb_frame, height=150)
        self.usb_listbox.pack(fill="x", padx=10, pady=5)
        
        # Boutons
        button_frame = ctk.CTkFrame(usb_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="🔄 Actualiser", command=self.refresh_usb_drives).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="⭐ Définir par défaut", command=self.set_default_usb).pack(side="left", padx=5)
        
        # Section clé par défaut
        default_frame = ctk.CTkFrame(parent)
        default_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(default_frame, text="⭐ Clé USB par défaut", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.default_usb_label = ctk.CTkLabel(default_frame, text="Aucune clé définie")
        self.default_usb_label.pack(pady=5)
        
        self.update_default_usb_display()
    
    def setup_sync_tab(self, parent, direction: str):
        """Configure un onglet de synchronisation"""
        direction_label = "Ordinateur → USB" if direction == "up" else "USB → Ordinateur"
        
        # En-tête
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(header_frame, text=f"📂 Synchronisation {direction_label}", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Liste des mappings
        mappings_frame = ctk.CTkFrame(parent)
        mappings_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(mappings_frame, text="Dossiers configurés:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        # ScrollableFrame pour les mappings
        scroll_frame = ctk.CTkScrollableFrame(mappings_frame, height=300)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Stocker la référence
        if direction == "up":
            self.up_mappings_frame = scroll_frame
        else:
            self.down_mappings_frame = scroll_frame
        
        # Boutons d'action
        action_frame = ctk.CTkFrame(parent)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(action_frame, text="➕ Ajouter dossier", 
                     command=lambda: self.add_mapping_dialog(direction)).pack(side="left", padx=5)
        
        ctk.CTkButton(action_frame, text=f"🚀 Lancer Sync {direction.upper()}", 
                     command=lambda: self.start_sync(direction), 
                     fg_color="green", hover_color="darkgreen").pack(side="right", padx=5)
        
        # Barre de progression
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        if direction == "up":
            self.up_progress = ctk.CTkProgressBar(progress_frame)
            self.up_progress.pack(fill="x", padx=10, pady=5)
            self.up_progress.set(0)
            self.up_progress_label = ctk.CTkLabel(progress_frame, text="Prêt")
            self.up_progress_label.pack(pady=2)
        else:
            self.down_progress = ctk.CTkProgressBar(progress_frame)
            self.down_progress.pack(fill="x", padx=10, pady=5)
            self.down_progress.set(0)
            self.down_progress_label = ctk.CTkLabel(progress_frame, text="Prêt")
            self.down_progress_label.pack(pady=2)
        
        self.refresh_mappings(direction)
    
    def setup_filters_tab(self, parent):
        """Configure l'onglet des filtres"""
        # En-tête
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(header_frame, text="🔧 Filtres par défaut", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkLabel(header_frame, text="Ces filtres seront appliqués aux nouveaux mappings", 
                    text_color="gray70").pack(pady=2)
        
        # ScrollableFrame principal
        main_scroll = ctk.CTkScrollableFrame(parent, height=450)
        main_scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Section répertoires exclus
        self.setup_filter_section(main_scroll, "Répertoires exclus", 
                                 "excluded_directories", "🚫 Répertoires à ignorer")
        
        # Section fichiers contenant
        self.setup_filter_section(main_scroll, "Fichiers contenant", 
                                 "excluded_filename_contains", "🚫 Ignorer si le nom contient")
        
        # Section extensions exclues
        self.setup_filter_section(main_scroll, "Extensions exclues", 
                                 "excluded_extensions", "🚫 Extensions à ignorer")
        
        # Section extensions incluses
        self.setup_filter_section(main_scroll, "Extensions autorisées", 
                                 "included_extensions", "✅ Extensions autorisées (si vide = toutes)")
        
        # Section sensibilité à la casse
        case_frame = ctk.CTkFrame(main_scroll)
        case_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(case_frame, text="Options", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        filters = self.config_manager.get_default_filters()
        self.case_sensitive_var = tk.BooleanVar(value=filters.get("case_sensitive", False))
        
        case_check = ctk.CTkCheckBox(case_frame, text="Sensible à la casse", 
                                   variable=self.case_sensitive_var,
                                   command=self.update_case_sensitivity)
        case_check.pack(pady=5)
    
    def setup_filter_section(self, parent, title: str, filter_key: str, description: str):
        """Crée une section de filtres"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=10)
        
        # Titre
        ctk.CTkLabel(section_frame, text=title, 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        ctk.CTkLabel(section_frame, text=description, 
                    text_color="gray70").pack(pady=2)
        
        # Liste des éléments
        list_frame = ctk.CTkScrollableFrame(section_frame, height=100)
        list_frame.pack(fill="x", padx=10, pady=5)
        
        # Stocker les références des frames
        if not hasattr(self, 'filter_frames'):
            self.filter_frames = {}
        self.filter_frames[filter_key] = list_frame
        
        # Zone d'ajout
        add_frame = ctk.CTkFrame(section_frame)
        add_frame.pack(fill="x", padx=10, pady=5)
        
        entry_var = tk.StringVar()
        entry = ctk.CTkEntry(add_frame, textvariable=entry_var, 
                           placeholder_text=f"Nouveau {title.lower()}")
        entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(add_frame, text="Ajouter", width=80,
                     command=lambda: self.add_filter_item(filter_key, entry_var)).pack(side="right", padx=5)
        
        self.refresh_filter_section(filter_key)
    
    def refresh_filter_section(self, filter_key: str):
        """Actualise une section de filtres"""
        if filter_key not in self.filter_frames:
            return
        
        frame = self.filter_frames[filter_key]
        
        # Vide le frame
        for widget in frame.winfo_children():
            widget.destroy()
        
        filters = self.config_manager.get_default_filters()
        items = filters.get(filter_key, [])
        
        if not items:
            ctk.CTkLabel(frame, text="Aucun élément", text_color="gray50").pack(pady=10)
        else:
            for item in items:
                item_frame = ctk.CTkFrame(frame)
                item_frame.pack(fill="x", padx=5, pady=2)
                
                ctk.CTkLabel(item_frame, text=item).pack(side="left", padx=10, pady=5)
                
                ctk.CTkButton(item_frame, text="🗑️", width=30, fg_color="red", hover_color="darkred",
                             command=lambda i=item: self.remove_filter_item(filter_key, i)).pack(side="right", padx=5)
    
    def add_filter_item(self, filter_key: str, entry_var: tk.StringVar):
        """Ajoute un élément à un filtre"""
        item = entry_var.get().strip()
        if not item:
            return
        
        # Ajoute selon le type aux filtres par défaut
        current_defaults = self.config_manager.get_default_filters()
        if filter_key not in current_defaults:
            current_defaults[filter_key] = []
        
        # Traite les extensions
        if filter_key in ["excluded_extensions", "included_extensions"]:
            if not item.startswith('.'):
                item = '.' + item
        
        if item not in current_defaults[filter_key]:
            current_defaults[filter_key].append(item)
            self.config_manager.update_default_filters(current_defaults)
        
        entry_var.set("")
        self.refresh_filter_section(filter_key)
    
    def remove_filter_item(self, filter_key: str, item: str):
        """Supprime un élément des filtres par défaut"""
        current_defaults = self.config_manager.get_default_filters()
        
        # Traite les extensions
        if filter_key in ["excluded_extensions", "included_extensions"]:
            if not item.startswith('.'):
                item = '.' + item
        
        if filter_key in current_defaults and item in current_defaults[filter_key]:
            current_defaults[filter_key].remove(item)
            self.config_manager.update_default_filters(current_defaults)
        
        self.refresh_filter_section(filter_key)
    
    def update_case_sensitivity(self):
        """Met à jour la sensibilité à la casse dans les filtres par défaut"""
        filters = {"case_sensitive": self.case_sensitive_var.get()}
        self.config_manager.update_default_filters(filters)
    
    def setup_logs_tab(self, parent):
        """Configure l'onglet des logs"""
        logs_frame = ctk.CTkFrame(parent)
        logs_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(logs_frame, text="📋 Journal de synchronisation", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.logs_text = ctk.CTkTextbox(logs_frame, height=400)
        self.logs_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Bouton effacer logs
        ctk.CTkButton(logs_frame, text="🗑️ Effacer logs", 
                     command=self.clear_logs).pack(pady=5)
    
    def refresh_usb_drives(self):
        """Actualise la liste des clés USB"""
        # Vide la liste actuelle
        for widget in self.usb_listbox.winfo_children():
            widget.destroy()
        
        drives = self.usb_detector.get_usb_drives()
        
        if not drives:
            ctk.CTkLabel(self.usb_listbox, text="❌ Aucune clé USB détectée").pack(pady=20)
        else:
            for i, drive in enumerate(drives):
                size_gb = drive['size'] / (1024**3)
                free_gb = drive['free'] / (1024**3)
                
                drive_frame = ctk.CTkFrame(self.usb_listbox)
                drive_frame.pack(fill="x", padx=5, pady=2)
                
                # Radio button pour sélection
                radio = ctk.CTkRadioButton(drive_frame, text="", 
                                         variable=self.selected_usb, value=drive['letter'])
                radio.pack(side="left", padx=5)
                
                # Info du drive
                info_text = f"{drive['label']} ({drive['letter']}) - {size_gb:.1f}GB ({free_gb:.1f}GB libre)"
                ctk.CTkLabel(drive_frame, text=info_text).pack(side="left", padx=10)
    
    def set_default_usb(self):
        """Définit la clé USB sélectionnée comme défaut"""
        selected = self.selected_usb.get()
        if not selected:
            messagebox.showwarning("Attention", "Veuillez sélectionner une clé USB")
            return
        
        drives = self.usb_detector.get_usb_drives()
        for drive in drives:
            if drive['letter'] == selected:
                self.config_manager.set_default_usb(drive['letter'], drive['label'])
                self.config_manager.add_known_drive(drive)
                self.update_default_usb_display()
                messagebox.showinfo("Succès", f"Clé {drive['label']} définie par défaut")
                break
    
    def update_default_usb_display(self):
        """Met à jour l'affichage de la clé par défaut"""
        default = self.config_manager.get_default_usb()
        if default:
            self.default_usb_label.configure(text=f"{default['label']} ({default['letter']})")
        else:
            self.default_usb_label.configure(text="Aucune clé définie")
    
    def add_mapping_dialog(self, direction: str):
        """Dialogue pour ajouter un mapping"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Ajouter mapping {direction.upper()}")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        
        # Variables
        source_var = tk.StringVar()
        dest_var = tk.StringVar()
        name_var = tk.StringVar()
        
        # Labels de direction
        if direction == "up":
            source_label = "Dossier source (ordinateur):"
            dest_label = "Dossier destination (USB):"
        else:
            source_label = "Dossier source (USB):"
            dest_label = "Dossier destination (ordinateur):"
        
        # Interface
        ctk.CTkLabel(dialog, text="Nom du mapping:").pack(pady=5)
        ctk.CTkEntry(dialog, textvariable=name_var, width=400).pack(pady=5)
        
        ctk.CTkLabel(dialog, text=source_label).pack(pady=5)
        source_frame = ctk.CTkFrame(dialog)
        source_frame.pack(pady=5)
        ctk.CTkEntry(source_frame, textvariable=source_var, width=350).pack(side="left", padx=5)
        ctk.CTkButton(source_frame, text="📁", width=40, 
                     command=lambda: self.browse_folder(source_var)).pack(side="left")
        
        ctk.CTkLabel(dialog, text=dest_label).pack(pady=5)
        dest_frame = ctk.CTkFrame(dialog)
        dest_frame.pack(pady=5)
        ctk.CTkEntry(dest_frame, textvariable=dest_var, width=350).pack(side="left", padx=5)
        ctk.CTkButton(dest_frame, text="📁", width=40, 
                     command=lambda: self.browse_folder(dest_var)).pack(side="left")
        
        # Boutons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)
        
        def save_mapping():
            if not source_var.get() or not dest_var.get():
                messagebox.showwarning("Attention", "Veuillez remplir tous les champs")
                return
            
            self.config_manager.add_sync_mapping(
                direction, source_var.get(), dest_var.get(), name_var.get()
            )
            self.refresh_mappings(direction)
            dialog.destroy()
        
        ctk.CTkButton(button_frame, text="✅ Ajouter", command=save_mapping).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="❌ Annuler", command=dialog.destroy).pack(side="left", padx=5)
    
    def browse_folder(self, var: tk.StringVar):
        """Ouvre un dialogue de sélection de dossier"""
        folder = filedialog.askdirectory()
        if folder:
            var.set(folder)
    
    def refresh_mappings(self, direction: str):
        """Actualise l'affichage des mappings"""
        frame = self.up_mappings_frame if direction == "up" else self.down_mappings_frame
        
        # Vide le frame
        for widget in frame.winfo_children():
            widget.destroy()
        
        mappings = self.config_manager.get_sync_mappings(direction)
        
        if not mappings:
            ctk.CTkLabel(frame, text="Aucun dossier configuré").pack(pady=20)
        else:
            for i, mapping in enumerate(mappings):
                mapping_frame = ctk.CTkFrame(frame)
                mapping_frame.pack(fill="x", padx=5, pady=2)
                
                # Checkbox enable/disable
                enabled_var = tk.BooleanVar(value=mapping.get("enabled", True))
                checkbox = ctk.CTkCheckBox(mapping_frame, text="", variable=enabled_var,
                                         command=lambda idx=i: self.toggle_mapping(direction, idx))
                checkbox.pack(side="left", padx=5)
                
                # Info du mapping
                info_frame = ctk.CTkFrame(mapping_frame)
                info_frame.pack(side="left", fill="x", expand=True, padx=5)
                
                ctk.CTkLabel(info_frame, text=mapping['name'], font=ctk.CTkFont(weight="bold")).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"📂 {mapping['source']}", text_color="gray70").pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"📁 {mapping['destination']}", text_color="gray70").pack(anchor="w")
                
                # Boutons
                button_frame = ctk.CTkFrame(mapping_frame)
                button_frame.pack(side="right", padx=5)
                
                # Bouton filtres
                ctk.CTkButton(button_frame, text="🔧", width=40, 
                             command=lambda idx=i, dir=direction: self.edit_mapping_filters(dir, idx)).pack(side="left", padx=2)
                
                # Bouton supprimer
                ctk.CTkButton(button_frame, text="🗑️", width=40, fg_color="red", hover_color="darkred",
                             command=lambda idx=i: self.remove_mapping(direction, idx)).pack(side="left", padx=2)
    
    def toggle_mapping(self, direction: str, index: int):
        """Active/désactive un mapping"""
        self.config_manager.toggle_mapping_enabled(direction, index)
        self.refresh_mappings(direction)
    
    def remove_mapping(self, direction: str, index: int):
        """Supprime un mapping"""
        if messagebox.askyesno("Confirmer", "Supprimer ce mapping ?"):
            self.config_manager.remove_sync_mapping(direction, index)
            self.refresh_mappings(direction)
    
    def edit_mapping_filters(self, direction: str, index: int):
        """Ouvre la boîte de dialogue des filtres pour un mapping"""
        mappings = self.config_manager.get_sync_mappings(direction)
        if index >= len(mappings):
            return
        
        mapping = mappings[index]
        
        # Crée la fenêtre de dialogue
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Filtres - {mapping['name']}")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()  # Modal
        
        # En-tête
        header_frame = ctk.CTkFrame(dialog)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(header_frame, text=f"🔧 Filtres pour: {mapping['name']}", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        ctk.CTkLabel(header_frame, text=f"📂 {mapping['source']} → {mapping['destination']}", 
                    text_color="gray70").pack(pady=2)
        
        # Zone scrollable
        scroll_frame = ctk.CTkScrollableFrame(dialog, height=350)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Variables pour stocker les filtres temporaires
        current_filters = self.config_manager.get_mapping_filters(direction, index)
        
        # Stockage des frames et variables
        filter_vars = {}
        filter_list_frames = {}
        
        # Section répertoires exclus
        self.create_filter_dialog_section(scroll_frame, "Répertoires exclus", 
                                         "excluded_directories", current_filters, 
                                         filter_vars, filter_list_frames, direction, index)
        
        # Section fichiers contenant
        self.create_filter_dialog_section(scroll_frame, "Fichiers contenant", 
                                         "excluded_filename_contains", current_filters, 
                                         filter_vars, filter_list_frames, direction, index)
        
        # Section extensions exclues
        self.create_filter_dialog_section(scroll_frame, "Extensions exclues", 
                                         "excluded_extensions", current_filters, 
                                         filter_vars, filter_list_frames, direction, index)
        
        # Section extensions incluses
        self.create_filter_dialog_section(scroll_frame, "Extensions autorisées", 
                                         "included_extensions", current_filters, 
                                         filter_vars, filter_list_frames, direction, index)
        
        # Sensibilité à la casse
        case_frame = ctk.CTkFrame(scroll_frame)
        case_frame.pack(fill="x", pady=10)
        
        case_sensitive_var = tk.BooleanVar(value=current_filters.get("case_sensitive", False))
        ctk.CTkCheckBox(case_frame, text="Sensible à la casse", 
                       variable=case_sensitive_var).pack(pady=10)
        
        # Boutons de contrôle
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        def apply_and_close():
            # Met à jour la sensibilité à la casse
            updated_filters = {"case_sensitive": case_sensitive_var.get()}
            self.config_manager.update_mapping_filters(direction, index, updated_filters)
            self.refresh_mappings(direction)
            dialog.destroy()
        
        def reset_to_defaults():
            if messagebox.askyesno("Confirmer", "Réinitialiser avec les filtres par défaut ?"):
                default_filters = self.config_manager.get_default_filters()
                self.config_manager.update_mapping_filters(direction, index, {
                    "excluded_directories": default_filters.get("excluded_directories", []).copy(),
                    "excluded_filename_contains": default_filters.get("excluded_filename_contains", []).copy(),
                    "excluded_extensions": default_filters.get("excluded_extensions", []).copy(),
                    "included_extensions": default_filters.get("included_extensions", []).copy(),
                    "case_sensitive": default_filters.get("case_sensitive", False)
                })
                dialog.destroy()
                # Relance le dialogue avec les nouvelles valeurs
                self.edit_mapping_filters(direction, index)
        
        ctk.CTkButton(button_frame, text="🔄 Réinitialiser", 
                     command=reset_to_defaults).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="✅ Fermer", 
                     command=apply_and_close).pack(side="right", padx=5)
    
    def create_filter_dialog_section(self, parent, title: str, filter_type: str, 
                                   current_filters: dict, filter_vars: dict, 
                                   filter_list_frames: dict, direction: str, mapping_index: int):
        """Crée une section de filtres dans la boîte de dialogue"""
        section_frame = ctk.CTkFrame(parent)
        section_frame.pack(fill="x", pady=10)
        
        # Titre
        ctk.CTkLabel(section_frame, text=title, 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        # Liste actuelle
        list_frame = ctk.CTkScrollableFrame(section_frame, height=80)
        list_frame.pack(fill="x", padx=10, pady=5)
        filter_list_frames[filter_type] = list_frame
        
        # Zone d'ajout
        add_frame = ctk.CTkFrame(section_frame)
        add_frame.pack(fill="x", padx=10, pady=5)
        
        entry_var = tk.StringVar()
        filter_vars[filter_type] = entry_var
        
        ctk.CTkEntry(add_frame, textvariable=entry_var, 
                    placeholder_text=f"Ajouter {title.lower()}").pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(add_frame, text="➕", width=40,
                     command=lambda: self.add_dialog_filter_item(
                         direction, mapping_index, filter_type, entry_var, 
                         filter_list_frames[filter_type])).pack(side="right", padx=5)
        
        # Remplit la liste
        self.refresh_dialog_filter_list(direction, mapping_index, filter_type, list_frame)
    
    def refresh_dialog_filter_list(self, direction: str, mapping_index: int, 
                                  filter_type: str, list_frame):
        """Actualise la liste des filtres dans la boîte de dialogue"""
        # Vide le frame
        for widget in list_frame.winfo_children():
            widget.destroy()
        
        current_filters = self.config_manager.get_mapping_filters(direction, mapping_index)
        items = current_filters.get(filter_type, [])
        
        if not items:
            ctk.CTkLabel(list_frame, text="Aucun élément", text_color="gray50").pack(pady=5)
        else:
            for item in items:
                item_frame = ctk.CTkFrame(list_frame)
                item_frame.pack(fill="x", padx=5, pady=2)
                
                ctk.CTkLabel(item_frame, text=item).pack(side="left", padx=5)
                
                ctk.CTkButton(item_frame, text="🗑️", width=30, fg_color="red", hover_color="darkred",
                             command=lambda i=item: self.remove_dialog_filter_item(
                                 direction, mapping_index, filter_type, i, list_frame)).pack(side="right", padx=5)
    
    def add_dialog_filter_item(self, direction: str, mapping_index: int, 
                              filter_type: str, entry_var: tk.StringVar, list_frame):
        """Ajoute un élément de filtre depuis la boîte de dialogue"""
        item = entry_var.get().strip()
        if not item:
            return
        
        self.config_manager.add_mapping_filter_item(direction, mapping_index, filter_type, item)
        entry_var.set("")
        self.refresh_dialog_filter_list(direction, mapping_index, filter_type, list_frame)
    
    def remove_dialog_filter_item(self, direction: str, mapping_index: int, 
                                 filter_type: str, item: str, list_frame):
        """Supprime un élément de filtre depuis la boîte de dialogue"""
        self.config_manager.remove_mapping_filter_item(direction, mapping_index, filter_type, item)
        self.refresh_dialog_filter_list(direction, mapping_index, filter_type, list_frame)
    
    def start_sync(self, direction: str):
        """Démarre la synchronisation"""
        if self.sync_in_progress:
            messagebox.showwarning("Attention", "Une synchronisation est déjà en cours")
            return
        
        mappings = self.config_manager.get_sync_mappings(direction)
        enabled_mappings = [m for m in mappings if m.get("enabled", True)]
        
        if not enabled_mappings:
            messagebox.showwarning("Attention", "Aucun dossier configuré pour la synchronisation")
            return
        
        # Lance la sync dans un thread séparé
        self.sync_in_progress = True
        thread = threading.Thread(target=self._run_sync, args=(direction, enabled_mappings))
        thread.daemon = True
        thread.start()
    
    def _run_sync(self, direction: str, mappings: List[Dict]):
        """Execute la synchronisation dans un thread séparé"""
        try:
            results = self.sync_engine.sync_directories(mappings, direction=direction)
            self.config_manager.update_last_sync(direction)
            
        except Exception as e:
            self.add_log(f"❌ Erreur lors de la synchronisation: {str(e)}")
        finally:
            self.sync_in_progress = False
            # Reset progress bar
            progress = self.up_progress if direction == "up" else self.down_progress
            progress_label = self.up_progress_label if direction == "up" else self.down_progress_label
            self.root.after(0, lambda: progress.set(0))
            self.root.after(0, lambda: progress_label.configure(text="Terminé"))
    
    def update_progress(self, current: int, total: int, current_file: str):
        """Met à jour la barre de progression"""
        progress_value = current / total if total > 0 else 0
        
        # Utilise after pour thread-safe update
        def update_ui():
            # Détermine quelle barre de progression utiliser
            # (dans un vrai contexte, il faudrait tracker quelle sync est en cours)
            if hasattr(self, 'up_progress'):
                self.up_progress.set(progress_value)
                self.up_progress_label.configure(text=f"{current}/{total} - {current_file}")
            if hasattr(self, 'down_progress'):
                self.down_progress.set(progress_value)
                self.down_progress_label.configure(text=f"{current}/{total} - {current_file}")
        
        self.root.after(0, update_ui)
    
    def add_log(self, message: str):
        """Ajoute un message aux logs"""
        def update_logs():
            self.logs_text.insert(tk.END, message + "\n")
            self.logs_text.see(tk.END)
        
        self.root.after(0, update_logs)
    
    def clear_logs(self):
        """Efface les logs"""
        self.logs_text.delete(1.0, tk.END)
    
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SyncUSBApp()
    app.run()