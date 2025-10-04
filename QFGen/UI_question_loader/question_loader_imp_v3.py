import customtkinter as ctk
import os
import json
import csv
from tkinter import Scrollbar, Text
from latexhighlighter.tex_highlighter import LatexText
from .scrollable_dropdown import CTkScrollableDropdownFrame,CTkScrollableDropdown
def default_callback(index,questions_dict):
    print(f"default_callback : question {index} dict : {questions_dict}")

class ScrollableEntryDropdown(ctk.CTkEntry):
    """
    CTkEntry avec une dropdown scrollable qui fonctionne comme un combobox
    mais en mode champ d'entrée texte.
    """
    def __init__(self, master, values=None, command=None, width=300, **kwargs):
        super().__init__(master, width=width, **kwargs)
        self.dropdown = None
        self.values = values or []
        self.command = command
        self.autocomplete = kwargs.get("autocomplete", True)
        #self.bind("<FocusIn>", self.show_dropdown)
        self.bind("<KeyRelease>", self.filter_dropdown)
        self.initialize_dropdown()
    def set(self, value):
        """Permet de définir directement la valeur de l'entry."""
        self.delete(0, ctk.END)
        self.insert(0, value)
    def initialize_dropdown(self):
        """Initialise le dropdown scrollable avec les valeurs."""
        self.dropdown = CTkScrollableDropdown(
            self, values=self.values, command=self.on_value_selected, autocomplete=self.autocomplete
        )
        #self.dropdown.place_forget()  # Caché par défaut

    def configure_values_old(self, new_values):
        """Met à jour les valeurs de la dropdown."""
        self.values = new_values
        print(new_values)
        self.initialize_dropdown()
        #self.dropdown.__setattr__("values",new_values)
    def configure_values(self, new_values):
        """Met à jour les valeurs de la dropdown."""
        self.values = new_values
        self.dropdown.configure(values=self.values)

    def on_value_selected(self, value):
        """Méthode appelée lorsqu'une valeur est sélectionnée dans la dropdown."""
        self.delete(0, ctk.END)
        self.insert(0, value)
        if self.command:
            self.command(value)

    def filter_dropdown(self, event=None):
        """Filtre les éléments de la dropdown en fonction du texte entré."""
        text = self.get().lower()
        if self.autocomplete:
            filtered_values = [v for v in self.values if text in v.lower()]
            self.dropdown.update_values(filtered_values)
        if not self.get():
            self.dropdown.update_values(self.values)

    def configure(self, **kwargs):
        """Permet de reconfigurer la dropdown dynamiquement."""
        if "values" in kwargs:
            self.configure_values(kwargs.pop("values"))
        super().configure(**kwargs)

class ScrollableComboBox(ctk.CTkComboBox):
    """Combobox avec surcouche scrollable pour faciliter l'utilisation dans l'app."""
    def __init__(self, master, values=None, command=None, width=300, **kwargs):
        super().__init__(master, values=values or [], command=command, width=width, **kwargs)
        self.dropdown = None
        self.values = values or []
        self.command = command
        self.autocomplete = kwargs.get("autocomplete", True)
        self.initialize_dropdown()

    def initialize_dropdown(self):
        """Initialise la dropdown avec les valeurs données."""
        self.dropdown = CTkScrollableDropdown(
            self, values=self.values, command=self.on_value_selected, autocomplete=self.autocomplete
        )

    def configure_values(self, new_values):
        """Met à jour les valeurs du combobox et de la dropdown."""
        self.values = new_values
        self.configure(values=new_values)
        self.initialize_dropdown()

    def on_value_selected(self, value):
        """Méthode appelée lorsqu'une valeur est sélectionnée."""
        self.set(value)
        if self.command:
            self.command(value)

class JsonQuestionLoader(ctk.CTkToplevel):
    def __init__(self, master, json_data_folder: str = "",callback:callable = default_callback,currindex = "0",niveau="6ème"):
        super().__init__(master)
        self.question_data_folder_csv_base = os.path.join(os.path.abspath("UI_question_loader"), "questions_data_folders.csv")
        self.already_done_questions_filepath = "UI_question_loader/already_done.csv"
        self.already_done_list = self.load_already_done_questions(self.already_done_questions_filepath)
        self.callback=callback
        self.master=master
        self.currindex = currindex
        self.niveau=niveau
        self.json_data_folder_list = self.load_json_data_folders()#json_data_folder
        if self.json_data_folder_list:
            self.json_data_folder = self.json_data_folder_list[0]
        else:
            self.json_data_folder=""
        
        #print(self.already_done_list)
        self.check_folder()
        self.questions_filepath = self.load_questions_filenames()
        #self.already_done_questions_filepath = self.load_already_done_questions()
        #self.questions_dict = self.match_done_questions()
        self.master.iconify()
        
        ###

        self.base_folder_list = self.load_json_data_folders()
        if self.base_folder_list:
            self.current_base_folder = self.base_folder_list[0]
        else:
            self.current_base_folder = ""
        self.questions_dict = {}
        self.question_files = []

        ###
        # Configurer la fermeture de la fenêtre
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        #self.attributes('-topmost', True)  # Fenêtre toujours au premier plan
        self.init_widgets()
        self.initialize_default_selection()

    def on_close(self):
        """Actions lors de la fermeture de la fenêtre secondaire"""
        # Restaurer la fenêtre principale
        self.master.deiconify()
        # Fermer la fenêtre secondaire
        self.destroy()
        
    def default_callback(self):
        print("Callback par défaut déclenché")

    def load_json_data_folders(self):
        """
        Charge les noms de répertoires contenus dans questions_data_folders.csv
        et renvoie une liste de répertoires valides.
        """
        csv_path = self.question_data_folder_csv_base
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Le fichier {csv_path} est introuvable. Veuillez le créer et ajouter une colonne 'data_folders'.")

        data_folders = []
        with open(csv_path, "r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            
            if "data_folders" not in reader.fieldnames:
                raise ValueError(f"Le fichier {csv_path} doit contenir une colonne 'data_folders'.")

            for row in reader:
                folder = row["data_folders"]
                if os.path.isdir(folder):  # Vérifie si le chemin est un répertoire
                    data_folders.append(folder)
                else:
                    print(f"Avertissement : {folder} n'est pas un répertoire valide, il sera ignoré.")

        if not data_folders:
            raise ValueError("Aucun répertoire valide trouvé dans le fichier questions_data_folders.csv.")

        return data_folders
    
    def check_folder(self):
        if self.json_data_folder=="":
            print(f"Dossier vide")
            return "Vide"
        if not os.path.exists(self.json_data_folder):
            raise FileExistsError(
                f"Le dossier {self.json_data_folder} n'existe pas ou n'est pas trouvé. \n"
                f"Chargez le {self.__class__.__name__} en renseignant json_data_folder = <absolute_path>"
            )

    def load_questions_folders(self,folder_path=""):
        if folder_path=="":
            folder_path=self.json_data_folder
        folders_list=[]
        for root, folders, files in os.walk(self.json_data_folder):
            for folder in folders:
                folders_list.append(folder)
        return folders_list
    def load_questions_files(self,folder_path=""):
        if folder_path=="":
            folder_path=self.json_data_folder
        files_list=[]
        for root, folders, files in os.walk(self.json_data_folder):
            for folder in folders:
                #print(files)
                files_list.append(folder)
        return files_list
    
    def load_questions_filenames(self,folder="") -> list:
        file_list = []
        #for root, _, files in os.walk(self.json_data_folder):
        if folder =="":
            folder = self.json_data_folder
        for root, _, files in os.walk(folder):
            for file in files:
                if file.endswith('.json'):
                    relative_path = os.path.relpath(os.path.join(root, file), self.json_data_folder)
                    file_list.append(relative_path)
        return file_list

    def load_already_done_questions(self,path)->list:
        csv_path = path#self.already_done_questions_basepath
        if not os.path.exists(csv_path):
            with open(csv_path, "w", encoding='utf-8') as csv_file:
                csv.writer(csv_file).writerow(["done_questions"])
        with open(csv_path, "r", encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            return [row[0] for row in reader if row]

    def match_done_questions(self,path):
        questions_dict = {}
        #already_done_list = self.already_done_questions_filepath
        already_done_list = self.already_done_list
            #full_path = os.path.join(self.json_data_folder, question_fpath)
        with open(path, "r", encoding='utf-8') as file:
            content = json.load(file)
            questions = content
            done_list = [
                f"{path}.json__v{index}"
                for index in range(len(questions))
                if f"{path}.json__v{index}" in already_done_list
            ]
            questions_dict = {
                "done_list": done_list,
                "questions_list": questions
            }
        return questions_dict

    def init_widgets(self):
        # Géométrie de la fenêtre
        self.title("Chargeur de Questions JSON")
        self.geometry("900x600")

        # 1. Frame pour le répertoire de base (en haut)
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.pack(fill="x", expand=False, pady=10, padx=10)

        # Combobox Base Folder
        self.combo_base_folder = ScrollableEntryDropdown(
            self.folder_frame,
            values=self.base_folder_list,
            command=self.on_base_folder_selected
        )
        self.combo_base_folder.pack(side="left", fill="x", expand=True, padx=5)

        # Bouton pour ajouter un répertoire
        self.button_add_base_folder = ctk.CTkButton(
            self.folder_frame,
            text="Ajouter un dossier",
            command=self.add_new_base_folder
        )
        self.button_add_base_folder.pack(side="right", padx=5)

        # 2. Frame pour les 4 combobox en ligne
        self.selection_frame = ctk.CTkFrame(self)
        self.selection_frame.pack(fill="x", expand=False, pady=10, padx=10)

        # Combobox Niveau
        self.combo_level_folder = ScrollableEntryDropdown(
            self.selection_frame,
            command=self.on_level_folder_selected,
            width=200
        )
        self.combo_level_folder.pack(side="left", fill="x", expand=True, padx=5)

        # Combobox Thème
        self.combo_theme_folder = ScrollableEntryDropdown(
            self.selection_frame,
            command=self.on_theme_folder_selected,
            width=200
        )
        self.combo_theme_folder.pack(side="left", fill="x", expand=True, padx=5)

        # Combobox Fichier JSON
        self.combo_filenames = ScrollableEntryDropdown(
            self.selection_frame,
            command=self.on_filename_selected,
            width=200
        )
        self.combo_filenames.pack(side="left", fill="x", expand=True, padx=5)

        # Combobox Questions
        self.combo_questions = ScrollableEntryDropdown(
            self.selection_frame,
            command=self.on_question_selected,
            width=200
        )
        self.combo_questions.pack(side="left", fill="x", expand=True, padx=5)

        # 3. Frame pour la zone de prévisualisation
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.pack(fill="both", expand=True, pady=10, padx=10)

        # Scrollbar pour le texte
        #self.scrollbar = Scrollbar(self.preview_frame, orient="vertical")
        #self.scrollbar.pack(side="right", fill="y")

        # Zone de texte pour afficher la question
        self.text_preview = LatexText(
            self.preview_frame,
            wrap="word",
            #yscrollcommand=self.scrollbar.set,
            state="disabled",
            height=20
        )
        self.text_preview.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        #self.scrollbar.config(command=self.text_preview.yview)

        # 4. Frame pour les boutons en bas
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", expand=False, pady=10, padx=10)

        # Bouton Annuler
        self.button_cancel = ctk.CTkButton(
            self.button_frame,
            text="Annuler",
            command=self.on_close
        )
        self.button_cancel.pack(side="left", padx=5, pady=5)

        # Bouton Charger la question
        self.button_load_question = ctk.CTkButton(
            self.button_frame,
            text="Charger cette question",
            command=self.load_selected_question
        )
        self.button_load_question.pack(side="right", padx=5, pady=5)

    def insert_method(self, e, label):
        """Insère le texte sélectionné dans le champ d'entrée."""
        label.set(e)


    def select_first_unused_question(self, question_display,first_file):
        """
        question_display : la liste des questions telle qu'affichée dans le combobox
        first_file : le filename sélectionné
        """
        # Sélectionner la première question non effectuée
        done_list = self.already_done_list#questions_parsed_dict["done_list"]
        
        question_text="Question 1"
        for index, question in enumerate(question_display,start=1):
            unique_id = f"{first_file}.json__v{index}"
            #print(f"{unique_id} : {unique_id in done_list}")
            if unique_id not in done_list:
                question_text = f"Question {index}"
                self.combo_questions.set(question_text)
                self.on_question_selected(question_text)
                return question_text
        return question_text
        
    def initialize_default_selection(self):
        """Initialise les sélections par défaut."""
        # Charger le premier répertoire
        if self.json_data_folder_list:
            self.combo_base_folder.set(self.current_base_folder) #self.json_data_folder_list[0])
            self.on_base_folder_selected(self.current_base_folder) #self.json_data_folder_list[0])

    def on_base_folder_selected(self, folder):
        """Lorsqu'un répertoire de base est sélectionné."""
        self.current_base_folder = folder
        level_folders = [f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))]
        self.combo_level_folder.configure_values(level_folders)
        if level_folders:
            self.combo_level_folder.set(self.niveau)#level_folders[0])
            self.on_level_folder_selected(self.niveau)#level_folders[0])
        else:
            self.combo_level_folder.set("Pas de niveaux")

    def on_level_folder_selected(self, folder):
        """Lorsqu'un dossier de niveau est sélectionné."""
        self.current_level_folder = os.path.join(self.current_base_folder, folder)
        theme_folders = [f for f in os.listdir(self.current_level_folder) if os.path.isdir(os.path.join(self.current_level_folder, f))]
        self.combo_theme_folder.configure_values(theme_folders)
        if theme_folders:
            self.combo_theme_folder.set(theme_folders[0])
            self.on_theme_folder_selected(theme_folders[0])
        else:
            self.combo_theme_folder.set("Pas de thème")

    def on_theme_folder_selected(self, folder):
        """Lorsqu'un dossier de thème est sélectionné."""
        self.current_theme_folder = os.path.join(self.current_level_folder, folder)
        json_files = [f[:-5] for f in os.listdir(self.current_theme_folder) if f.endswith(".json")]
        self.combo_filenames.configure_values(json_files)
        if json_files:
            self.combo_filenames.set(json_files[0])
            self.on_filename_selected(json_files[0])
        else:
            self.combo_filenames.set(f"Pas de fichier dans {folder}")

    def on_filename_selected(self, filename):
        """Lorsqu'un fichier est sélectionné, charge les questions."""
        self.current_filename = filename
        self.current_filename = os.path.join(self.current_theme_folder, f"{filename}.json")
        with open(self.current_filename, "r", encoding="utf-8") as file:
            self.questions_dict = json.load(file)
        #questions = [f"Question {i}" for i,_ in enumerate(self.questions_dict,start=1)]
        #questions_parsed_dict = self.match_done_questions(self.current_filename)#self.questions_dict[first_file]["done_list"]
        #questions = questions_parsed_dict["questions_list"]
        done_list = self.already_done_list#questions_parsed_dict["done_list"]
        # print(f'\n\n{filename}.json\n\n{done_list}\n\n')
        question_display = [
            f"Question {i} {'    ✔' if f'{filename}.json__v{i}' in done_list else ''}"
            for i,_ in enumerate(self.questions_dict,start=1)
        ]#
        self.combo_questions.configure_values(question_display)

        self.combo_questions.set(self.select_first_unused_question(question_display,first_file=filename))

    def on_question_selected(self, question):
        """Lorsqu'une question est sélectionnée, affiche son contenu."""
        index = int(question.split()[1])
        content = self.make_preview_from_json_dumps(self.questions_dict[index-1])#json.dumps(self.questions_dict[index], indent=4, ensure_ascii=False)
        self.text_preview.config(state="normal")
        self.text_preview.delete("1.0", "end")
        self.text_preview.insert("1.0", content)
        self.text_preview.config(state="disabled")

    def add_new_base_folder(self):
        """
        Ouvre une boîte de dialogue pour sélectionner un nouveau répertoire
        et l'ajoute au fichier CSV des répertoires de base.
        """
        # Désactiver temporairement le mode topmost pour la boîte de dialogue
        self.attributes('-topmost', False)

        try:
            # Ouvre la boîte de dialogue pour choisir un répertoire
            new_folder = ctk.filedialog.askdirectory(title="Sélectionnez un nouveau dossier de base")
            if new_folder and os.path.isdir(new_folder):
                csv_path = self.question_data_folder_csv_base  # Chemin vers le fichier CSV

                # Ajoute le nouveau répertoire au fichier CSV
                with open(csv_path, "a", encoding="utf-8", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow([new_folder])

                # Met à jour la liste des répertoires dans l'application
                self.json_data_folder_list.append(new_folder)
                self.combo_base_folder.configure(values=self.json_data_folder_list)
                print(f"Ajouté : {new_folder}")
        finally:
            # Réactiver le mode topmost après la sélection
            self.attributes('-topmost', True)

    def make_preview_from_json_dumps(self, q_dict:dict)->str:
        texts = []
        for key,value in q_dict.items():
            texts.append(f"--- {key.upper()} ---\n{value}\n")
        return ''.join(texts)
    
    def load_selected_question(self):
        # Logique pour charger la question sélectionnée
        selected_file_display = self.combo_filenames.get()
        selected_question = self.combo_questions.get()
        if not selected_file_display or not selected_question:
            ctk.CTkMessageBox.show_error("Erreur", "Veuillez sélectionner un fichier et une question.")
            return
        selected_file = selected_file_display.split("    ")[0]
        question_index = int(selected_question.split()[1])
        #print(json.dumps(self.questions_dict,ensure_ascii=True,indent=4))
        question_content = self.questions_dict[question_index-1]#important pour charger la bonne question car l'index commence à 0...#[selected_file]["questions_list"]
        #print(f"Chargement de la question {self.currindex} portant le numéro {question_index} dans le db : {question_content}")
        #print(question_content["questions"])
        questions_dict = {
            "question":question_content["enonce"],
            "answer":question_content["reponse"], #[question_index]
            "details":question_content["details"],
            "theme":question_content["theme"],
        }
        self.callback(index=self.currindex,questions_dict=questions_dict)
        self.add_question_in_done_csv(absolute_path = selected_file,question_index=question_index)
        self.on_close()

    def add_question_in_done_csv(self, absolute_path, question_index):
        # Ouvre le fichier CSV et ajoute une entrée si elle n'existe pas déjà
        unique_id = f"{absolute_path}.json__v{question_index}"
        csv_path = self.already_done_questions_filepath

        # Vérifie si l'entrée existe déjà dans le fichier
        if unique_id in self.already_done_list:
            print(f"Question déjà ajoutée : {unique_id}")
            return

        # Ajoute l'entrée au fichier CSV
        with open(csv_path, "a", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([unique_id])
        print(f"Question ajoutée au fichier : {unique_id}")