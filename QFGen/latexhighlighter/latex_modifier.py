import re
import importlib
import os
import sys
import customtkinter as ctk
from tkinter import simpledialog, messagebox, ttk
import time
from latexhighlighter.minimal_text_area import MinimalLaTeXtext
import latexhighlighter.modifier_list as mod
    
class LaTeXModifier(ctk.CTkToplevel):
    def __init__(self,parent,texte,master_widget = None,topmost_option=False):
        super().__init__(parent)
        self.parent = parent
        self.master_widget = master_widget
        self.topmost_option = topmost_option
        if self.master_widget and self.topmost_option:
            self.master_widget.attributes("-topmost", False)
        self.texte = texte
        self.commandes_disponibles = None
        self.modifier_file = "latexhighlighter/modifier_list.py"
        self.command_params:dict={}
        self.init_commands()
        self.init_widgets()

    

    def init_widgets(self):
        self.title("Options de modification")
        self.attributes("-topmost", True)
        
        # Ligne de commandes
        command_frame = ctk.CTkFrame(self)
        command_frame.pack(fill="x", padx=5, pady=5)
        self.command_selector = ctk.CTkComboBox(command_frame, values = self.commandes_disponibles, command=self.on_combobox_selected)
        self.command_selector.pack(side="left", padx=5, pady=5)

        self.command_params_frame=ctk.CTkFrame(command_frame)
        self.command_params_frame.pack(fill="x",padx=5,pady=5)

        apply_button = ctk.CTkButton(command_frame, text="Appliquer", command=self.apply_command)
        apply_button.pack(side="left", padx=5, pady=5)

        add_command_button = ctk.CTkButton(command_frame, text="Ajouter", command=self.add_command)
        add_command_button.pack(side="left", padx=5, pady=5)

        # Fenetre de texte principale
        self.text_edit_area = MinimalLaTeXtext(parent = self,wrap="word", height=10)
        self.text_edit_area.pack(expand=1, fill="both", padx=5, pady=5)
        self.text_edit_area.insert("0.0", self.texte)

        # Fenetre de prompts pour l'IA
        prompt_frame = ctk.CTkFrame(self)
        prompt_frame.pack(fill="x", padx=5, pady=5)

        self.prompt_area = MinimalLaTeXtext(prompt_frame, wrap="word", height=5)
        self.prompt_area.pack(side="left", expand=1, fill="both", padx=5, pady=5)

        assistant_button = ctk.CTkButton(prompt_frame, text="Appeler l'assistant", command=self.call_assistant)
        assistant_button.pack(side="left", padx=5, pady=5)

        # Boutons Annuler et Conserver
        action_frame = ctk.CTkFrame(self)
        action_frame.pack(fill="x", padx=5, pady=5)

        cancel_button = ctk.CTkButton(action_frame, text="Annuler", command=self.destroy)
        cancel_button.pack(side="left", padx=5, pady=5)

        save_button = ctk.CTkButton(action_frame, text="Conserver", command=self.save_changes)
        save_button.pack(side="left", padx=5, pady=5)

    def on_combobox_selected(self, selected_command):
        # Nettoyer le frame des paramètres
        for widget in self.command_params_frame.winfo_children():
            widget.destroy()

        # Charger les paramètres de la fonction sélectionnée
        command_params = self.command_params[selected_command]

        print(f"{selected_command} : {command_params}")
        # Placer les widgets dans la grille
        row = 0
        col = 0
        for key, value in command_params.items():
            label = ctk.CTkLabel(self.command_params_frame, text=key)
            label.grid(row=row, column=col, padx=5, pady=5)
            entry = ctk.CTkEntry(self.command_params_frame)
            entry.insert(0, value)
            entry.grid(row=row, column=col+1, padx=5, pady=5)
            col += 2
            if col >= 4:  # Passer à la ligne suivante toutes les deux colonnes
                col = 0
                row += 1

    def get_command_params(self,selected_command):
        print(self.command_params[selected_command])
        return self.command_params[selected_command]
    
    def init_commands(self):
        module_name = os.path.splitext(os.path.basename(self.modifier_file))[0]
        if module_name in sys.modules:
            del sys.modules[module_name]
        spec = importlib.util.spec_from_file_location(module_name, self.modifier_file)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        with open(self.modifier_file) as function_file:
            content = function_file.read()
        
        """# Rechercher toutes les définitions de fonctions
        functions_list = re.findall(r'def (\w+)\((.*?)\):', content)"""
        # Rechercher toutes les définitions de fonctions
        functions_list = re.findall(r'def (\w+)\(([^)]*)\)(?:->str)?:', content)
        print(f"functions_list : \n {functions_list}")
        self.commandes_disponibles = ["Uppercase", "Lowercase", "Capitalize"]
        for func_name, params in functions_list:
            self.commandes_disponibles.append(func_name)
            param_dict = {}
            if params:
                param_pairs = params.split(',')
                for pair in param_pairs:
                    param, default = (pair.split('=') + [None])[:2]  # handle parameters without defaults
                    param = param.strip()
                    if param != "texte":
                        param_dict[param] = default.strip() if default else ""
            self.command_params[func_name] = param_dict
        print("------------------------------\n------------------------------")
        print(self.command_params)
        return 0

    def init_commands_old(self):
        module_name = os.path.splitext(os.path.basename(self.modifier_file))[0]
        if module_name in sys.modules:
            del sys.modules[module_name]
        spec = importlib.util.spec_from_file_location(module_name, self.modifier_file)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        with open(self.modifier_file) as function_file:
            content = function_file.read()
        
        # Rechercher toutes les définitions de fonctions
        functions_list = re.findall(r'def (\w+)\(', content)
        self.command_params=""#chercher les paramètres de chaque fonction avec leurs valeurs par défaut ( sauf le paramètre texte )
        self.commandes_disponibles = ["Uppercase","Lowercase","Capitalize"]
        self.commandes_disponibles.extend(functions_list)
        return 0

    def apply_command(self):
        selected_command = self.command_selector.get()
        text_content = self.text_edit_area.get("1.0", "end-1c")

        if selected_command == "Uppercase":
            modified_text = text_content.upper()
        elif selected_command == "Lowercase":
            modified_text = text_content.lower()
        elif selected_command == "Capitalize":
            modified_text = text_content.capitalize()
        elif selected_command in self.commandes_disponibles:
            # Utiliser eval pour appeler la commande dynamique
            modified_text = eval(f"mod.{selected_command}")(text_content)
        else:
            messagebox.showerror("Erreur", "Commande non reconnue.")
            return

        self.text_edit_area.delete("1.0", "end")
        self.text_edit_area.insert("1.0", modified_text)
        self.text_edit_area.highlight_syntax()

    def add_command(self):
        # Désactive l'option topmost de self
        self.attributes('-topmost', False)
        self.new_command_data = None
        # Initie un objet CommandAdder de sorte à recueillir les spécifications de la commande
        self.adder = CommandAdder(parent=self, title="Ajouter une commande")

    def apply_changes(self):
    
        if self.new_command_data:
            # Stocke la nouvelle commande dans self.modifier_file (chemin vers le fichier) en 'a'
            with open(self.modifier_file, 'a') as f:
                f.write(f"\n\ndef {self.new_command_data['name']}({self.new_command_data['arg']})->str:\n\t{self.new_command_data['code']}")

            time.sleep(2)
            # Recharge le fichier de commandes
            self.init_commands()

            # Actualise le combobox
            self.command_selector.configure(values=self.commandes_disponibles)
            self.command_selector.set(self.new_command_data['name'])


    def call_assistant(self):
        prompt_text = self.prompt_area.get("1.0", "end-1c")
        # Implémentez ici l'appel à l'IA avec le texte de prompt_text
        # Par exemple, utilisez une API ou une bibliothèque pour l'intégration d'IA
        response = "Réponse de l'IA pour le prompt : " + prompt_text  # Placeholder
        messagebox.showinfo("Réponse de l'IA", response)

    def save_changes(self):
        modified_text = self.text_edit_area.get("1.0", "end-1c")
        self.parent.delete("sel.first", "sel.last")
        self.parent.insert("insert", modified_text)
        self.parent.highlight_syntax()
        if self.master_widget and self.topmost_option:
            self.master_widget.attributes("-topmost",True)
        self.destroy()

class CommandAdder(ctk.CTkToplevel):
    def __init__(self, parent, title=None):
        super().__init__(parent)
        self.parent=parent
        self.title(title)
        self.attributes('-topmost', True)
        self.geometry("500x300")

        self.result = None

        self.body()

    def body(self):
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=10, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Nom de la commande:").grid(row=0, column=0, pady=5, padx=5)
        ctk.CTkLabel(frame, text="Argument de la commande:").grid(row=1, column=0, pady=5, padx=5)
        ctk.CTkLabel(frame, text="Code de la commande:").grid(row=2, column=0, pady=5, padx=5)

        self.command_name = ctk.CTkEntry(frame)
        self.command_arg = ctk.CTkEntry(frame)
        self.command_code = ctk.CTkEntry(frame)

        self.command_name.grid(row=0, column=1, pady=5, padx=5)
        self.command_arg.grid(row=1, column=1, pady=5, padx=5)
        self.command_code.grid(row=2, column=1, pady=5, padx=5)

        self.submit_button = ctk.CTkButton(frame, text="Submit", command=self.apply)
        self.submit_button.grid(row=3, columnspan=2, pady=10)

    def apply(self):
        self.result = {
            'name': self.command_name.get(),
            'arg': self.command_arg.get(),
            'code': self.command_code.get()
        }
        self.parent.attributes('-topmost', True)

        self.parent.new_command_data = self.result
        self.parent.apply_changes()

        self.destroy()