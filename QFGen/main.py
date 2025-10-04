import os
from qf_gen_config.cfg import read_tcl_path

# Configurer TCL_LIBRARY si disponible
tcl_path = read_tcl_path()
if tcl_path:
    os.environ["TCL_LIBRARY"] = tcl_path

import tkinter as tk

import customtkinter as ctk

from tkinter import filedialog, messagebox,Toplevel
import json
import re
from collections import OrderedDict
from latexcompiler import LaTeXCompiler
from datetime import datetime
from qf_gen_config.cfg import read_api_key
from autoindent_tex import clean_and_indent_latex_file
from latexhighlighter.tex_highlighter import LatexText
from latexhighlighter.syntax_checker_v2 import check_latex_code
from UI_question_loader.scrollable_dropdown import CTkScrollableDropdownFrame,CTkScrollableDropdown
from UI_question_loader.question_loader_imp_v3 import JsonQuestionLoader
from auto_question_maker import MultiQuestionGeneratorUI,MonoQuestionGeneratorUI,QuestionGenerator
import threading
from threading import Thread
from functools import partial
from prompt_system_manager import PSManager
from tex_eval_maker import load_json_files_in_date_range,parse_date_from_key,extract_questions_by_date
import asyncio
import random
import platform

#import logging

#logging.basicConfig(level=logging.DEBUG)

class QuestionnaireApp(ctk.CTk):
    def __init__(self, tex_path):
        super().__init__()
        self.api_key = read_api_key().strip().strip('"')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        #logging.debug("Application initialized")
        self.assistant_question=[]
        self.update_id = None
        self.check_dpi_id = None
        self.closed=False
        self.schedule_updates()
        self.model_QF_file = "modele_QF.tex"
        self.model_QF_eval_file = "Modele_QF_eval.tex"
        self.title("Créateur de Questions Flash")
        self.geometry("1800x790")
        self.geometry("-10+0")  # Positionner en haut à gauche de l'écran
        self.fullscreen_state = False  # Initialiser l'état plein écran
        self.bind("<F11>", self.toggle_fullscreen)  # Lier la touche F11 pour le plein écran
        self.bind("<Escape>", self.end_fullscreen)  # Lier la touche Échap pour quitter le plein écran
        #self.toggle_fullscreen()  # Activer le plein écran au démarrage
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.long_term_self_setup = True
        self.new_question_option = False
        self.last_questions_data_path = "last_questions_data.json"
        self.questions_database_directory = "databases"
        self.generation_main_repo = "generated"
        self.generations_directory = "generated/tex"
        self.output_pdf_directory = "generated/pdf"
        self.eval_generations_directory = "generated/eval_tex"
        self.output_eval_pdf_directory = "generated/eval_pdf"
        self.current_class = "Non sélectionné"
        self.first_load_data()

        self.questions_data = {}
        self.questions_loaders = {}
        self.questions = []
        self.responses = []
        self.details = []
        self.themes = []
        self.prompts=[]
        self.AI_buttons=[]
        self.prompt_example="Vérifie que le contenu suivant est correct. Si oui, recopie le, si non, corrige les erreurs."
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.complete_bottom_frame()
        self.complete_header_frame()
        self.complete_main_frame()
        for key,value in self.last_questions_data.items():
            last_question_id=key
        self.load_question(question_id=last_question_id)
        self.question_id_combo.set(last_question_id)
        #self.load_last_question()

    def toggle_fullscreen(self, event=None):
        """Active ou désactive le mode plein écran."""
        self.fullscreen_state = not self.fullscreen_state
        self.attributes("-fullscreen", self.fullscreen_state)
        return "break"

    def end_fullscreen(self, event=None):
        """Désactive le mode plein écran."""
        self.fullscreen_state = False
        self.attributes("-fullscreen", False)
        return "break"

    def schedule_updates(self):
        if not self.closed:
            self.update_id = self.after(1000, self.update)
            self.check_dpi_id = self.after(2000, self.check_dpi_scaling)

    def update(self):
        if not self.closed:
            #logging.debug("Update function called")
            self.update_id = self.after(1000, self.update)

    def check_dpi_scaling(self):
        if not self.closed:
            #logging.debug("check_dpi_scaling function called")
            self.check_dpi_id = self.after(2000, self.check_dpi_scaling)

    def on_closing(self):
        #logging.debug("Application closing")
        self.closed = True
        if self.update_id is not None:
            self.after_cancel(self.update_id)
            self.update_id = None
        if self.check_dpi_id is not None:
            self.after_cancel(self.check_dpi_id)
            self.check_dpi_id = None
        self.destroy()
        #logging.debug("Application closed")

    def complete_header_frame(self):
        label_classe = ctk.CTkLabel(self.header_frame, text="Classe ciblée :")
        label_classe.grid(row=0, column=0, padx=10, pady=5)
        classes = ["6ème", "5ème", "4ème", "3ème","2nde","1ere","Tle"]
        self.classe_combo = ctk.CTkComboBox(self.header_frame, values=classes, command=self.load_data)
        #last_class=self.last_questions_data.get('classe')
        last_class="Non sélectionné"
        for key,value in self.last_questions_data.items():
            last_class=value['classe']
            last_question_id=key
        self.classe_combo.set(last_class)#"Non sélectionné")
        self.classe_combo.grid(row=0, column=1, padx=10, pady=5)
        label_date = ctk.CTkLabel(self.header_frame, text="Date :")
        label_date.grid(row=0, column=2, padx=10, pady=5)
        self.date_entry = ctk.CTkEntry(self.header_frame)
        self.date_entry.grid(row=0, column=3, padx=10, pady=5)
        self.date_entry.insert(0,datetime.today().strftime("%d_%m_%Y"))
        label_question_id = ctk.CTkLabel(self.header_frame, text="ID Question :")
        label_question_id.grid(row=0, column=4, padx=10, pady=5)
        self.question_id_combo = ctk.CTkComboBox(self.header_frame, values=[], command=self.load_question)
        self.question_id_combo.grid(row=0, column=5, padx=10, pady=5)
        self.load_data(event=last_class)
        #self.load_question(question_id=last_question_id)


    def complete_main_frame(self):
        #tab = ctk.CTkTabview(self)
        #tab.pack(pady=10, padx=20, fill="both", expand=True)
        for i in range(3):
            frame = ctk.CTkFrame(self)
            frame.pack(pady=10, padx=20, fill="both", expand=True)

            theme_label = ctk.CTkLabel(frame, text=f"Thème {i+1}")
            theme_label.grid(row=0, column=4, padx=10, pady=5)
            theme_entry = ctk.CTkEntry(frame)
            theme_entry.grid(row=1, column=4, padx=10, pady=5)
            self.themes.append(theme_entry)
            prompt_label = ctk.CTkLabel(frame, text=f"Prompt {i+1}")
            prompt_label.grid(row=0, column=0, padx=10, pady=5)
            

            question_label = ctk.CTkLabel(frame, text=f"Question {i+1}")
            question_label.grid(row=0, column=1, padx=10, pady=5)
            question_entry = LatexText(parent=frame, width=40, height=8)
            question_entry.bind("<Control-Double-1>", lambda event, index=i, widget=question_entry: self.open_mono_question_generator_ui(index,widget))

            question_entry.highlight_syntax()
            question_entry.grid(row=1, column=1, padx=10, pady=5)
            self.questions.append(question_entry)

            response_label = ctk.CTkLabel(frame, text=f"Réponse {i+1}")
            response_label.grid(row=0, column=2, padx=10, pady=5)
            response_entry = LatexText(parent=frame, width=40, height=8)
            response_entry.bind("<Control-Double-1>", lambda event, index=i, widget=response_entry: self.open_mono_question_generator_ui(index,widget))

            response_entry.highlight_syntax()
            response_entry.grid(row=1, column=2, padx=10, pady=5)
            self.responses.append(response_entry)

            details_label = ctk.CTkLabel(frame, text=f"Détails {i+1}")
            details_label.grid(row=0, column=3, padx=10, pady=5)
            details_entry = LatexText(parent=frame, width=40, height=8)
            details_entry.bind("<Control-Double-1>", lambda event, index=i, widget=details_entry: self.open_mono_question_generator_ui(index,widget))

            details_entry.highlight_syntax()
            details_entry.grid(row=1, column=3, padx=10, pady=5)
            self.details.append(details_entry)
            load_frame = ctk.CTkFrame(frame)
            prompt_entry = LatexText(parent=load_frame, width=40, height=4)
            prompt_entry.bind("<Control-Double-1>", lambda event, index=i, widget=prompt_entry: self.open_mono_question_generator_ui(index,widget))
            prompt_entry.highlight_syntax()
            prompt_entry.grid(row=0, column=0, padx=10, pady=5)
            self.prompts.append(prompt_entry)
            
            load_buttons_frame = ctk.CTkFrame(load_frame)
            AI_button = ctk.CTkButton(load_buttons_frame, text="Appeler l'assistant", command=lambda index=i: self.autocomplete_question(index))
            
            #self.AI_buttons[i] = ctk.CTkButton(frame, text="Appeler l'assistant", command=self.autocomplete_question)
            AI_button.grid(row=0, column=0, padx=10, pady=5)
            LOAD_button = ctk.CTkButton(load_buttons_frame, text="Charger un modèle", command=lambda index=i: self.load_question_by_model(index))
            
            #self.AI_buttons[i] = ctk.CTkButton(frame, text="Appeler l'assistant", command=self.autocomplete_question)
            LOAD_button.grid(row=0, column=1, padx=10, pady=5)
            load_buttons_frame.grid(row=1, column=0, padx=10, pady=5)
            load_frame.grid(row=1, column=0, padx=10, pady=5)
            self.AI_buttons.append(AI_button)

    def load_question_by_model(self,index:int):
        niveau=self.classe_combo.get()
        print(f"Niveau sélectionné : {niveau}")
        self.questions_loaders[index] = JsonQuestionLoader(master=self,callback = self.callback_load_questions,currindex = index,niveau=niveau)
    def open_mono_question_generator_ui(self, index, widget):
        """top = ctk.CTkToplevel(self)
        top.title(f"MonoQuestionGeneratorUI - {index + 1}")
        top.geometry("800x600")
        """
        content = widget.get("1.0", "end-1c")  # Obtenez le contenu du widget text
        prompt_example=f"{self.prompt_example}"# \n{content}"
        print(content)
        self.assistant_question=MonoQuestionGeneratorUI(api_key=self.api_key,content=content,prompt_example=prompt_example,initial_widget=widget)
        #self.assistant_question.pack(self.assistant_question)

    def complete_bottom_frame(self):
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(pady=10, padx=20, fill="both", expand=True)
        #self.long_term_button = ctk.CTkCheckBox(master=bottom_frame, text="Activer les modifications sur la base de données", command=self.change_long_term_param)
        #self.long_term_button.grid(row=0, column=1, padx=10, pady=5)
        #self.new_cpt_button = ctk.CTkCheckBox(master=bottom_frame, text="Créer un nouvel objet", command=self.change_new_option_param)
        #self.new_cpt_button.grid(row=0, column=2, padx=10, pady=5)
        generate_button = ctk.CTkButton(bottom_frame, text="Générer LaTeX", command=self.generate_latex)
        generate_button.grid(row=0, column=3, padx=10, pady=5)
        save_button = ctk.CTkButton(bottom_frame, text="Sauvegarder les modifications", command=self.save_data)
        save_button.grid(row=0, column=4, padx=10, pady=5)

        # Nouveau bouton pour créer une nouvelle question
        new_question_button = ctk.CTkButton(bottom_frame, text="Créer une nouvelle série", command=self.create_new_question)
        new_question_button.grid(row=0, column=5, padx=10, pady=5)

        # Nouveau bouton pour créer une nouvelle question
        load_data_from_question_button = ctk.CTkButton(bottom_frame, text="Charger un contenu précédent", command=self.load_existing_question)
        load_data_from_question_button.grid(row=0, column=6, padx=10, pady=5)

        # Nouveau bouton pour créer une évaluation
        create_new_eval_button = ctk.CTkButton(bottom_frame, text="Créer une évaluation", command=self.generate_eval)
        create_new_eval_button.grid(row=0, column=7, padx=10, pady=5)

        # Nouveau bouton pour créer une évaluation
        open_folder_button = ctk.CTkButton(bottom_frame, text="Ouvrir le répertoire des questions Flash", command=self.open_tex_pdf_folder)
        open_folder_button.grid(row=0, column=8, padx=10, pady=5)


    def open_tex_pdf_folder(self):
        """
        Ouvre le répertoire self.generation_main_repo dans une fenêtre d'explorateur de fichiers.
        Fonctionne sous Windows, macOS et Linux.
        """
        if hasattr(self, 'generation_main_repo') and os.path.isdir(self.generation_main_repo):
            path = os.path.abspath(self.generation_main_repo)

            system_name = platform.system()
            try:
                if system_name == "Windows":
                    os.startfile(path)  # Ouvre l'explorateur Windows
                else:
                    print("Système d'exploitation non pris en charge")
            except Exception as e:
                print(f"Erreur lors de l'ouverture du répertoire : {e}")
        else:
            print("Le répertoire spécifié n'existe pas ou n'est pas défini.")

    def load_existing_question(self):
        
        class_id= self.classe_combo.get().strip()
        question_keys = list(self.questions_data.keys())
        result=self.ask_question_id(class_id=class_id,question_keys=question_keys)
        question_id = result['question_id']
        selected_path=result['path']
        if question_id=="stop":
            return 
        else:
            print(f"Question sélectionnée : {question_id} dans le fichier {selected_path}")

        #question_id = asyncio.run(self.ask_question_id(class_id=class_id,question_keys=question_keys))

        date = datetime.today().strftime("%d_%m_%Y")
        questions_data=self.load_questions_from_file(selected_path)
        if question_id in questions_data:
            self.current_questions_data = questions_data[question_id]
            print(f"self.current_questions_data : {self.current_questions_data}")
            self.classe_combo.set(class_id)
            #self.date_entry.delete(0, tk.END)
            #self.date_entry.insert(0, date)

            for i in range(3):
                question_data = self.current_questions_data["questions"].get(f"question{i+1}", {})
                self.questions[i].delete("1.0", tk.END)
                self.questions[i].insert("1.0", question_data.get("enonce", ""))
                self.questions[i].highlight_syntax()

                self.responses[i].delete("1.0", tk.END)
                self.responses[i].insert("1.0", question_data.get("reponse", ""))
                self.responses[i].highlight_syntax()

                self.details[i].delete("1.0", tk.END)
                self.details[i].insert("1.0", question_data.get("details", ""))
                self.details[i].highlight_syntax()

                self.prompts[i].delete("1.0", tk.END)
                self.prompts[i].insert("1.0", question_data.get("prompt", ""))
                #self.prompts[i].highlight_syntax()

                self.themes[i].delete(0, tk.END)
                self.themes[i].insert(0, question_data.get("theme", ""))
                
        else:
            messagebox.showerror("Erreur", f"L'ID {self.current_question_id} n'existe pas.")
    def load_questions_from_file(self,file):
        with open(file,'r', encoding='utf-8')as f:
            content=json.load(f)
        return content
    def ask_question_id(self,class_id,question_keys):
        # Créer une fenêtre de dialogue
        dialog = ctk.CTkToplevel(self)
        dialog.title("Sélectionner une question")
        dialog.geometry("400x200")
        dialog.resizable(False, False)

        # Centrer la fenêtre
        window_width = 400
        window_height = 400
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Désactiver les interactions avec la fenêtre principale
        dialog.transient(self)
        dialog.grab_set()

        # Ajouter une variable pour stocker la sélection
        result = {
                    "question_id": None,
                    "path": None
                }

        def get_classes_and_dates(databases_folder="databases"):
            """
            Analyse le dossier databases pour récupérer les classes et les dates disponibles sous la forme {year}_{month}.
            """
            classes = []
            dates_by_class = {}

            if not os.path.exists(databases_folder):
                print(f"Le dossier {databases_folder} n'existe pas.")
                return [], {}

            for folder in os.listdir(databases_folder):
                class_path = os.path.join(databases_folder, folder)
                if os.path.isdir(class_path):# and folder.startswith("database_"):
                    print(f"folder {folder}")

                    class_name = folder.replace("database_", "")

                    print(f"new_class_name : {class_name}")
                    classes.append(class_name)
                    print(classes)
                    dates_by_class[class_name] = []

                    for file in os.listdir(class_path):
                        print(f" file {file}")
                        if file.endswith(".json"):
                            parts = file.replace("database_", "").replace(".json", "").split("_")
                            print(f"parts : {parts}")
                            if len(parts) == 2:
                                year_month = f"{parts[0]}_{parts[1]}"
                                dates_by_class[class_name].append(year_month)
                            elif len(parts) == 1:
                                year_month = f"{parts[0]}"
                                dates_by_class[class_name].append(year_month)
            return classes, dates_by_class
        # Récupérer les classes et dates depuis le dossier databases
        classes, dates_by_class = get_classes_and_dates()

        #classes=[""].extend(classes)
        print(f"classes : {classes}")

        month=datetime.today().month
        year=datetime.today().year

        class_id_combo = ctk.CTkComboBox(dialog, values=classes, font=("Arial", 12), width=300)
        class_id_combo.pack(pady=10)
        class_id_combo.set(class_id.replace('è','e'))

        date_id_combo = ctk.CTkComboBox(dialog, values=[], font=("Arial", 12), width=300)
        date_id_combo.pack(pady=10)
        date_id_combo.set(f"{year}_{month}")
        # Ajouter un label
        label = ctk.CTkLabel(dialog, text="Sélectionnez une question :", font=("Arial", 12))
        label.pack(pady=10)

        # Ajouter une combobox
        question_id_combo = ctk.CTkComboBox(dialog, values=question_keys, font=("Arial", 12), width=300)
        question_id_combo.pack(pady=10)
        
        # Ajouter des boutons OK et Annuler
        def get_questions_keys(database):
            #ouvre le json et retourne la liste des keys de ce json. 
            database=database.replace('è','e')
            try:
                with open(database, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                return list(data.keys())
            except FileNotFoundError:
                print(f"Fichier non trouvé : {database}")
                return []
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON pour le fichier : {database}")
                return []
        
        def update_dates(*args):
            """
            Met à jour les dates disponibles en fonction de la classe sélectionnée.
            """
            classe = class_id_combo.get().strip()
            if classe in dates_by_class:
                date_id_combo.configure(values=dates_by_class[classe])
                if dates_by_class[classe]:
                    date_id_combo.set(dates_by_class[classe][0])
                else:
                    date_id_combo.set(f"{year}_{month}")
            else:
                date_id_combo.configure(values=[])
                date_id_combo.set(f"{year}_{month}")

        def update_questions(*args):
            """
            Met à jour les questions disponibles en fonction de la classe et de la date sélectionnées.
            """
            classe = class_id_combo.get().strip()
            date = date_id_combo.get().strip()
            if classe and date:
                database = f"databases/database_{classe}/database_{date}.json"
                keys = get_questions_keys(database)
                question_id_combo.configure(values=keys)
                if keys:
                    question_id_combo.set(keys[0])
                else:
                    question_id_combo.set("")
            else:
                question_id_combo.configure(values=[])
                question_id_combo.set("")

        # Lier les combobox pour mise à jour dynamique
        class_id_combo.configure(command=update_dates)
        date_id_combo.configure(command=update_questions)

        # Initialiser les valeurs de date et de question
        update_dates()
        update_questions()

        def on_ok():
            result["question_id"] = question_id_combo.get()
            result_filename=f"databases/database_{class_id_combo.get()}/database_{date_id_combo.get()}.json"
            result["path"] = result_filename
            dialog.destroy()

        def on_cancel():
            result["question_id"] = "stop"
            dialog.destroy()

        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)

        ok_button = ctk.CTkButton(button_frame, text="OK", command=on_ok)
        ok_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(button_frame, text="Annuler", command=on_cancel)
        cancel_button.pack(side="left", padx=10)

        dialog.wait_window()  # Attend la fermeture de la fenêtre

        return result#["question_id"]

    def change_new_option_param(self):
        self.new_question_option = not self.new_question_option

    def change_long_term_param(self):
        self.long_term_self_setup = not self.long_term_self_setup

    def first_load_data(self):
        if os.path.exists(self.last_questions_data_path):
            with open(self.last_questions_data_path, 'r', encoding='utf-8') as file:
                self.last_questions_data = json.load(file)
        else:
            self.last_questions_data = {}

    def load_data(self, event=None):
        try:
            self.current_class = self.classe_combo.get().strip()
        except:
            self.current_class = "6ème"

        class_file_names_dict = {
            "6ème": "6eme",
            "5ème": "5eme",
            "4ème": "4eme",
            "3ème": "3eme",
            "2nde":"2nde",
            "1ere":"1ere",
            "Tle":"Tle"
        }
        
        classe_name = class_file_names_dict[self.current_class]
        month=datetime.today().month
        year=datetime.today().year
        new_file_name = os.path.join(f"database_{classe_name}",f"database_{year}_{month}.json") #accession à databases/<classe>/database_<année>_<mois> 
        print(f"new_file_name : {new_file_name}")
        file_name = f"database_{classe_name}.json"
        self.questions_data_path = os.path.join(self.questions_database_directory, new_file_name) #remplacer par new_file_name pour le nouveau système de database.
        
        if os.path.exists(self.questions_data_path):
            with open(self.questions_data_path, 'r', encoding='utf-8') as file:
                self.questions_data = json.load(file)
            self.update_question_id_combo()
        else:
            self.questions_data = {}
            self.question_id_combo.set("")
            self.question_id_combo.configure(values=[])

    def update_question_id_combo(self):
        question_keys = list(self.questions_data.keys())
        self.question_id_combo.configure(values=question_keys)
        self.question_id_combo.set(question_keys[0])

    def save_data(self):
        if not self.current_question_id:
            self.current_question_id = self.generate_new_question_id()
        else:
            if self.long_term_self_setup and self.new_question_option:
                self.current_question_id = self.generate_new_question_id()

        data = {
            "classe": self.classe_combo.get().strip(),
            "date": self.date_entry.get().strip(),
            "questions": {f"question{i+1}": {
                "enonce": q.get("1.0", tk.END).strip(),
                "reponse": self.responses[i].get("1.0", tk.END).strip(),
                "details": self.details[i].get("1.0", tk.END).strip(),
                "theme": self.themes[i].get().strip(),
                "prompt": self.prompts[i].get("1.0", tk.END).strip()
            } for i, q in enumerate(self.questions)}
        }

        self.questions_data[self.current_question_id] = data
        temp_data = {self.current_question_id: data}

        with open(self.last_questions_data_path, 'w', encoding='utf-8') as file:
            json.dump(temp_data, file, ensure_ascii=False, indent=4)

        if self.long_term_self_setup:
            self.save_to_long_term()

    def save_to_long_term(self):
        if os.path.exists(self.questions_data_path):
            with open(self.questions_data_path, 'r+', encoding='utf-8') as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = {}

                existing_data.update(self.questions_data)
                file.seek(0)
                json.dump(existing_data, file, ensure_ascii=False, indent=4)
                file.truncate()
        else:
            directory = os.path.dirname(self.questions_data_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(self.questions_data_path, 'w', encoding='utf-8') as file:
                json.dump(self.questions_data, file, ensure_ascii=False, indent=4)

    def load_last_question(self):
        if self.last_questions_data:
            last_question_id = next(iter(self.last_questions_data))
            self.load_question(last_question_id)

    def load_question(self, question_id=None):
        if not question_id:
            self.current_question_id = self.question_id_combo.get()
        else:
            self.current_question_id = question_id

        if self.current_question_id in self.questions_data:
            self.current_questions_data = self.questions_data[self.current_question_id]

            self.classe_combo.set(self.current_questions_data["classe"])
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(0, self.current_questions_data["date"])

            for i in range(3):
                question_data = self.current_questions_data["questions"].get(f"question{i+1}", {})
                self.questions[i].delete("1.0", tk.END)
                self.questions[i].insert("1.0", question_data.get("enonce", ""))
                self.questions[i].highlight_syntax()

                self.responses[i].delete("1.0", tk.END)
                self.responses[i].insert("1.0", question_data.get("reponse", ""))
                self.responses[i].highlight_syntax()

                self.details[i].delete("1.0", tk.END)
                self.details[i].insert("1.0", question_data.get("details", ""))
                self.details[i].highlight_syntax()

                self.prompts[i].delete("1.0", tk.END)
                self.prompts[i].insert("1.0", question_data.get("prompt", ""))
                #self.prompts[i].highlight_syntax()

                self.themes[i].delete(0, tk.END)
                self.themes[i].insert(0, question_data.get("theme", ""))
                
        else:
            messagebox.showerror("Erreur", f"L'ID {self.current_question_id} n'existe pas.")

    def callback_load_questions(self,index,questions_dict):
        """
        Callback pour la question_loader_imp afin de peupler les encadrés
        """
        widget_question=self.questions[index]#[index+1] [index]#
        widget_answer=self.responses[index]#[index+1]
        widget_details=self.details[index]#[index+1]
        widget_theme=self.themes[index]#[index+1]
        widget_question.delete("1.0", "end")
        widget_answer.delete("1.0", "end")
        widget_details.delete("1.0", "end")
        widget_theme.delete(0, 'end')
        widget_question.insert("end", questions_dict["question"])
        widget_answer.insert("end", questions_dict["answer"])
        widget_details.insert("end", questions_dict["details"])
        widget_theme.insert("end", questions_dict["theme"])

    def autocomplete_question(self,index):
        if self.api_key == None:
            messagebox.showerror("Erreur", "Pour bénéficier de cette fonctionnalité, une clé api 'openai' doit être renseignée dans le fichier qf_gen_config/api_key")
            return

        widget_question=self.questions[index]#[index+1] [index]#
        widget_answer=self.responses[index]#[index+1]
        widget_details=self.details[index]#[index+1]
        widget_theme=self.themes[index]#[index+1]
        generator = QuestionGenerator(self.api_key, widget_question=widget_question, widget_answer_short=widget_answer, widget_answer_details=widget_details,widget_theme=widget_theme)
        prompt=self.prompts[index].get("1.0", "end-1c").split("\n")
        classe=self.classe_combo.get()
        date=self.date_entry.get()
        widget_question.delete("1.0", "end")
        widget_answer.delete("1.0", "end")
        widget_details.delete("1.0", "end")
        #widget_theme.delete("1.0", "end")
        widget_theme.delete(0, 'end')

        thread_done_event = threading.Event()
    
        def thread_function():
            generator.generate_questions(classe=classe, date=date, conditions=prompt, callback=lambda text: self.update_result_text(index, text))
            thread_done_event.set()
        
        thread = threading.Thread(target=thread_function)
        thread.start()
        
        def check_thread():
            if thread_done_event.is_set():
                widget_question.highlight_syntax()
                widget_answer.highlight_syntax()
                widget_details.highlight_syntax()
            else:
                self.after(100, check_thread)
        
        self.after(100, check_thread)
        #comment je fais pour qu'une fois que le thread est terminé, j'apelle  la méthode .highlight_syntax() pour le widget_question ; answer et details ?    


    def update_result_text(self, index, text):
        widget_question = self.questions[index]
        widget_answer = self.responses[index]
        widget_details = self.details[index]
        widget_theme = self.themes[index]

        # Gérer les messages d'erreur (string) et les résultats (dict)
        if isinstance(text, dict):
            widget_question.insert("end", text.get('question', ''))
            widget_answer.insert("end", text.get('answer_short', ''))
            widget_details.insert("end", text.get('answer_details', ''))
            widget_theme.insert("end", text.get('theme', ''))
        else:
            # Si c'est un string (message d'erreur), l'afficher dans la question
            widget_question.insert("end", str(text))

        widget_question.update_idletasks()
        widget_answer.update_idletasks()
        widget_details.update_idletasks()
        widget_theme.update_idletasks()


    def create_new_question(self):
        classe = self.classe_combo.get().strip()
        date = self.date_entry.get().strip()
        def on_form_submit(new_classe, new_date):
            # Mise à jour des champs avec les nouvelles valeurs
            self.classe_combo.set(new_classe)
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, new_date)
            
            if classe == "Non sélectionné" or not date:
                messagebox.showerror("Erreur", "Veuillez sélectionner une classe et entrer une date.")
                return

            new_question_id = self.generate_new_question_id()
            self.current_question_id=new_question_id
            self.questions_data[new_question_id] = {
                "classe": classe,
                "date": date,
                "questions": {
                    "question1": {"enonce": "", "reponse": "", "details": "", "theme": "", "prompt": ""},
                    "question2": {"enonce": "", "reponse": "", "details": "", "theme": "", "prompt": ""},
                    "question3": {"enonce": "", "reponse": "", "details": "", "theme": "", "prompt": ""}
                }
            }

            self.update_question_id_combo()
            self.question_id_combo.set(new_question_id)
            self.load_question(new_question_id)
            messagebox.showinfo("Succès", f"La nouvelle question pour le niveau {classe} avec l'ID {new_question_id} a été créée.")

        # Création de la fenêtre de modification avec les valeurs actuelles
        form = QuestionForm(self, classe, date, on_form_submit)
        form.grab_set()
        


    def generate_new_question_id(self):
        date = self.date_entry.get().strip().replace('/', '_')
        classe = self.classe_combo.get().strip()
        base_id = f"QF_{date}"

        existing_ids = self.questions_data.keys()
        new_id = base_id
        counter = 1
        while new_id in existing_ids:
            new_id = f"QF{counter}_{date}"
            counter += 1

        return new_id

    def generate_latex(self):
        self.question_id_combo.get().strip()
        #print(f"question_id_combo : {self.question_id_combo.get().strip()}\n current question id : {self.current_question_id} \n date :{self.date_entry.get().strip()}")
        self.save_data()
        questions = [q.get("1.0", tk.END).strip() for q in self.questions]
        for i,q in enumerate(questions):
            boo,mes = check_latex_code(q)
            if boo == False:
                messagebox.showerror("Erreur LaTeX détectée", f"Dans la question {i} :\n\n{mes}")
                print(q)
                return
        responses = [r.get("1.0", tk.END).strip() for r in self.responses]
        for i,q in enumerate(responses):
            boo,mes = check_latex_code(q)
            if boo == False:
                print(q)
                messagebox.showerror("Erreur LaTeX détectée", f"Dans la réponse {i} :\n\n{mes}")
                return
        themes = [t.get().strip() for t in self.themes]
        details = [d.get("1.0", tk.END).strip() for d in self.details]
        for i,q in enumerate(details):
            boo,mes = check_latex_code(q)
            if boo == False:
                messagebox.showerror("Erreur LaTeX détectée", f"Dans les détails de la réponse {i} :\n\n{mes}")
                print(q)
                return
        classe = self.classe_combo.get().strip()
        date = self.date_entry.get().strip()
        date_for_files=self.question_id_combo.get().strip()#date.replace('/','_')
        content = self.create_latex_content(classe, date, themes, questions, responses, details)
        print(date_for_files)
        month=date_for_files.split('_')[-2]
        year=date_for_files.split('_')[-1]
        file_path = f"{self.generations_directory}/{classe}/{year}/{month}/{date_for_files}_{classe}.tex"
        pdf_output_directory=f"{self.output_pdf_directory}/{classe}/{year}/{month}"
        print(f"generate_latex_filepath : {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        os.makedirs(os.path.dirname(pdf_output_directory), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        clean_and_indent_latex_file(file_path, file_path)
        compiler = LaTeXCompiler([file_path], auxiliary_suppressor_on=True)
        if compiler.compile_and_open(document_path=file_path, output_directory=pdf_output_directory, double_compile=False):
            print("Compilation du fichier réussie.")

    def create_latex_content(self, classe, date, themes, questions, responses, details):
        with open(self.model_QF_file, 'r', encoding='utf-8') as file:
            content = file.read()

        metadata = f"%niveau estimé : {classe}\n%date de projection : {date}\n%themes abordés : {', '.join(themes)}"
        content = content.replace("%metadata", metadata)

        for i in range(1, 4):
            content = content.replace(f"%question{i}", questions[i-1])
            content = content.replace(f"%reponse{i}", responses[i-1])
            content = content.replace(f"%details{i}", details[i-1])

        return content
    
    def create_latex_eval(self, classe, date_min,date_max,number_question):
        """
        fabrique l'évaluation sur une période donnée. il reste à l'enregistrer et à compiler
        """
        with open(self.model_QF_eval_file, 'r', encoding='utf-8') as file:
            content = file.read()

        metadata = f"%niveau estimé : {classe}\n"
        content = content.replace("%metadata", metadata)
        questions = []
        responses = []
        details = []
        json_files = load_json_files_in_date_range(self.questions_database_directory, classe, date_min, date_max)
        print(f"json_files : {json_files}")
        # Étape 2 : Extraire les questions pertinentes
        selected_questions = extract_questions_by_date(json_files, date_min, date_max, number_question)
        print(f"selected_questions : {len(selected_questions)} questions sélectionnées")

        added_content = []
        added_short_answer = []
        added_answer = []
        added_theme = set()
        for i,q in enumerate(selected_questions):
            number= random.randint(1,3)
            questions = q['questions'][f'question{number}']['enonce']
            theme = q['questions'][f'question{number}']['theme']
            responses = q['questions'][f'question{number}']['reponse']
            details = q['questions'][f'question{number}']['details'].replace(r'\columnbreak',r'%\columnbreak')
            date_question = q['date']
            if questions:
                added_theme.add(f"\\competence{{{theme.strip()}}}")

            if questions:
                added_content.append(f"%Question {number} du {date_question}\n  \\item \itempoint{{1}}[-0.5] {questions} \\begin{{crep}}[extra lines=2] \\end{{crep}}")
            else:
                added_content.append(f"\\item \itempoint{{1}} Pas de question \\begin{{crep}}[extra lines=2] \\end{{crep}}")

            if added_short_answer:
                added_short_answer.append(f"\\item {{\n{responses}\n}}")
            else:
                added_short_answer.append(f"\\item Pas de réponse")

            if added_answer:
                added_answer.append(f"\\item {{\n{details}\n}}")
            else:
                added_answer.append(f"\\item Pas de détails")
        
        content = content.replace(r"%questions",'\n'.join(added_content))
        unique_ordered_themes = list(OrderedDict.fromkeys(added_theme))
        content = content.replace(r"%competences", '\n'.join(unique_ordered_themes))
        content = re.sub(r'\\competence\{\}', '', content)
        content = content.replace(r"%answers",'\n'.join(added_answer))
        content.replace("""
\\item                
""","""
%\\item                
""")
        content = self.add_percent_inside_document(latex_content=content)
        return content

    def add_percent_inside_document(self,latex_content: str) -> str:
        """
        Ajoute un '%' à la fin de chaque ligne non vide et aux lignes vides
        uniquement à l'intérieur de l'environnement \\begin{document} et \\end{document}.
        """
        inside_document = False
        cleaned_lines = []

        for line in latex_content.splitlines():
            stripped_line = line.rstrip()

            if r'\begin{document}' in stripped_line:
                inside_document = True
                cleaned_lines.append(stripped_line)
                continue
            
            if r'\end{document}' in stripped_line:
                inside_document = False
                cleaned_lines.append(stripped_line)
                continue

            if inside_document:
                if stripped_line:  # Ligne non vide
                    if not stripped_line.endswith('%'):
                        cleaned_lines.append(stripped_line + ' %')
                    else:
                        cleaned_lines.append(stripped_line)
                else:  # Ligne vide, ajouter un '%'
                    cleaned_lines.append('%')
            else:
                cleaned_lines.append(stripped_line)

        return '\n'.join(cleaned_lines)

    def get_infos_for_eval(self):
        """
        Crée une interface pour recueillir les informations nécessaires : classe, date_min, date_max, number_question.
        Retourne ces informations sous forme de tuple.
        """
        dialog = ctk.CTk()
        dialog.title("Saisie des informations pour l'évaluation")
        dialog.geometry("400x400")

        def submit():
            nonlocal classe, date_min, date_max, number_question
            classe = class_entry.get().strip()
            date_min = date_min_entry.get().strip()
            date_max = date_max_entry.get().strip()
            try:
                number_question = int(number_question_entry.get().strip())
            except ValueError:
                number_question = 0
            dialog.quit()

        ctk.CTkLabel(dialog, text="Classe :", font=("Arial", 12)).pack(pady=5)
        class_entry = ctk.CTkEntry(dialog, width=300)
        class_entry.pack(pady=5)
        class_entry.insert(0,"4eme")
        ctk.CTkLabel(dialog, text="Date minimum (JJ_MM_AAAA) :", font=("Arial", 12)).pack(pady=5)
        max_date_placeholder=datetime.strftime(datetime.today(),"%d_%m_%Y")
        min_date_placeholder=datetime.strftime(datetime(year=datetime.today().year,month=datetime.today().month-2,day=datetime.today().day),"%d_%m_%Y")
        date_min_entry = ctk.CTkEntry(dialog, width=300)
        date_min_entry.pack(pady=5)
        date_min_entry.insert(0,min_date_placeholder) #"12_11_2024")

        ctk.CTkLabel(dialog, text="Date maximum (JJ_MM_AAAA) :", font=("Arial", 12)).pack(pady=5)
        date_max_entry = ctk.CTkEntry(dialog, width=300)
        date_max_entry.pack(pady=5)
        date_max_entry.insert(0,max_date_placeholder)
        ctk.CTkLabel(dialog, text="Nombre de questions :", font=("Arial", 12)).pack(pady=5)
        number_question_entry = ctk.CTkEntry(dialog, width=300)
        number_question_entry.pack(pady=5)
        number_question_entry.insert(0,"10")
        submit_button = ctk.CTkButton(dialog, text="Valider", command=submit)
        submit_button.pack(pady=20)

        classe, date_min, date_max, number_question = None, None, None, None
        dialog.mainloop()
        dialog.destroy()

        return classe, date_min, date_max, number_question
    def generate_eval(self):
        classe, date_min,date_max,number_question = self.get_infos_for_eval()
        content = self.create_latex_eval(classe, date_min,date_max,number_question)
        year=date_max.split("_")[-1].strip()
        file_path = f"{self.eval_generations_directory}/{classe}/{year}/eval_{date_min}_{date_max}_{classe}.tex"
        pdf_output_directory=f"{self.output_eval_pdf_directory}/{classe}/{year}"
        print(f"generate_latex_filepath : {file_path}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        os.makedirs(os.path.dirname(pdf_output_directory), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        clean_and_indent_latex_file(file_path, file_path)
        compiler = LaTeXCompiler([file_path], auxiliary_suppressor_on=True)
        if compiler.compile_and_open(document_path=file_path, output_directory=pdf_output_directory, double_compile=True):
            print("Compilation du fichier réussie.")
        

class QuestionForm(ctk.CTkToplevel):
    def __init__(self, parent, classe_value, date_value, on_submit_callback):
        super().__init__(parent)
        self.title("Modifier les informations")
        self.geometry("300x200")
        self.on_submit_callback = on_submit_callback

        # Ajout des widgets pour la classe et la date
        ctk.CTkLabel(self, text="Classe :").pack(pady=5)
        self.classe_entry = ctk.CTkEntry(self)
        self.classe_entry.insert(0, classe_value)  # Valeur recueillie
        self.classe_entry.pack(pady=5, fill="x", padx=10)

        ctk.CTkLabel(self, text="Date :").pack(pady=5)
        self.date_entry = ctk.CTkEntry(self)
        self.date_entry.insert(0, date_value)  # Valeur recueillie
        self.date_entry.pack(pady=5, fill="x", padx=10)

        # Bouton OK pour valider les modifications
        self.ok_button = ctk.CTkButton(self, text="OK", command=self.submit)
        self.ok_button.pack(pady=20)

    def submit(self):
        # Récupération des nouvelles valeurs entrées par l'utilisateur
        new_classe = self.classe_entry.get().strip()
        new_date = self.date_entry.get().strip()
        
        # Appel du callback pour envoyer les valeurs au parent
        self.on_submit_callback(new_classe, new_date)
        self.destroy()  # Ferme la fenêtre après soumission

if __name__ == "__main__":
    tex_final_filepath = "test_1_qf.tex"
    #logging.debug("Starting application")

    app = QuestionnaireApp(tex_final_filepath)
    app.mainloop()
