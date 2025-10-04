import customtkinter as ctk
import os
import json
import csv
from tkinter import Scrollbar, Text
from scrollable_dropdown import CTkScrollableDropdownFrame,CTkScrollableDropdown
def default_callback(index,questions_dict):
    print(f"default_callback : question {index} dict : {questions_dict}")
class JsonQuestionLoader(ctk.CTkToplevel):
    def __init__(self, master, json_data_folder: str = "",callback:callable = default_callback,currindex = "0"):
        super().__init__(master)
        self.question_data_folder_csv_base = os.path.join(os.path.abspath("UI_question_loader"), "questions_data_folders.csv")
        self.callback=callback
        self.currindex = currindex
        self.json_data_folder_list = self.load_json_data_folders()#json_data_folder
        self.json_data_folder = self.json_data_folder_list[0]
        self.already_done_questions_basepath = "UI_question_loader/already_done.csv"
        self.check_folder()
        self.questions_filepath = self.load_questions_filenames()
        self.already_done_questions_filepath = self.load_already_done_questions()
        self.questions_dict = self.match_done_questions()
        self.init_widgets()
        self.attributes('-topmost', True)  # Fenêtre toujours au premier plan

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
        if not os.path.exists(self.json_data_folder):
            raise FileExistsError(
                f"Le dossier {self.json_data_folder} n'existe pas ou n'est pas trouvé. \n"
                f"Chargez le {self.__class__.__name__} en renseignant json_data_folder = <absolute_path>"
            )

    def load_questions_filenames(self) -> list:
        file_list = []
        for root, _, files in os.walk(self.json_data_folder):
            for file in files:
                if file.endswith('.json'):
                    relative_path = os.path.relpath(os.path.join(root, file), self.json_data_folder)
                    file_list.append(relative_path)
        return file_list

    def load_already_done_questions(self):
        csv_path = self.already_done_questions_basepath
        if not os.path.exists(csv_path):
            with open(csv_path, "w", encoding='utf-8') as csv_file:
                csv.writer(csv_file).writerow(["done_questions"])
        with open(csv_path, "r", encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            return [row[0] for row in reader if row]

    def match_done_questions(self):
        questions_dict = {}
        already_done_list = self.already_done_questions_filepath

        for question_fpath in self.questions_filepath:
            full_path = os.path.join(self.json_data_folder, question_fpath)
            with open(full_path, "r", encoding='utf-8') as file:
                content = json.load(file)
                questions = content
                done_list = [
                    f"{question_fpath}__v{index}"
                    for index in range(len(questions))
                    if f"{question_fpath}__v{index}" in already_done_list
                ]
                questions_dict[question_fpath] = {
                    "done_list": done_list,
                    "questions_list": questions
                }
        return questions_dict

    def init_widgets(self):
        # Géométrie de la fenêtre
        self.title("Chargeur de Questions JSON")
        self.geometry("800x600")

        # Frame pour le sélecteur de répertoire et le bouton Ajouter un dossier
        self.folder_frame = ctk.CTkFrame(self)
        self.folder_frame.pack(fill="x", expand=False, pady=10, padx=10)

        # Combobox 0 : base folders
        self.combo_base_folders = ctk.CTkComboBox(
            self.folder_frame,
            values=self.json_data_folder_list,
            command=self.on_combobox_0_selected
        )
        self.combo_base_folders.pack(side="left", fill="x", expand=True, padx=5)
        self.combo_base_folders.set(self.json_data_folder)  # Définit le répertoire par défaut

        # Bouton pour ajouter un nouveau base folder
        self.button_add_base_folder = ctk.CTkButton(
            self.folder_frame,
            text="Ajouter un dossier",
            command=self.add_new_base_folder
        )
        self.button_add_base_folder.pack(side="right", padx=5)

        # Frame pour les sélecteurs de fichiers et de questions
        self.selection_frame = ctk.CTkFrame(self)
        self.selection_frame.pack(fill="x", expand=False, pady=10, padx=10)

        # Combobox 1 : fichiers JSON
        self.combo_filenames = ctk.CTkComboBox(
            self.selection_frame,
            values=[],
            command=self.on_combobox_1_selected
        )
        self.combo_filenames.pack(side="left", fill="x", expand=True, padx=5)

        # Combobox 2 : questions dans le fichier sélectionné
        self.combo_questions = ctk.CTkComboBox(
            self.selection_frame,
            values=[],
            command=self.on_combobox_2_selected
        )
        self.combo_questions.pack(side="right", fill="x", expand=True, padx=5)

        # Frame pour le label de prévisualisation avec scroll
        self.preview_frame = ctk.CTkFrame(self)
        self.preview_frame.pack(fill="both", expand=True, pady=10, padx=10)

        self.scrollbar = Scrollbar(self.preview_frame, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.label_question_preview = Text(self.preview_frame, wrap="word", yscrollcommand=self.scrollbar.set, state="disabled", height=20)
        self.label_question_preview.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.scrollbar.config(command=self.label_question_preview.yview)

        # Frame pour les boutons
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(fill="x", expand=False, pady=10, padx=10)

        # Boutons Annuler et Charger
        self.button_cancel = ctk.CTkButton(self.button_frame, text="Annuler", command=self.destroy)
        self.button_cancel.pack(side="left", padx=5, pady=5)

        self.button_load_question = ctk.CTkButton(self.button_frame, text="Charger cette question", command=self.load_selected_question)
        self.button_load_question.pack(side="right", padx=5, pady=5)

        # Initialisation automatique
        self.initialize_default_selection()

    def initialize_default_selection(self):
        """
        Charge automatiquement :
        - Le répertoire 0 dans le combobox des dossiers.
        - Le fichier 0 dans le combobox des fichiers.
        - La première question non effectuée dans le combobox des questions.
        """
        # Charger le premier répertoire
        if self.json_data_folder_list:
            self.combo_base_folders.set(self.json_data_folder_list[0])
            self.on_combobox_0_selected(self.json_data_folder_list[0])

        # Charger le premier fichier
        if self.questions_dict:
            first_file = list(self.questions_dict.keys())[0]
            self.combo_filenames.set(first_file)
            self.on_combobox_1_selected(first_file)
            self.select_first_unused_question(first_file)

    def select_first_unused_question(self,first_file):
        # Sélectionner la première question non effectuée
        done_list = self.questions_dict[first_file]["done_list"]
        questions = self.questions_dict[first_file]["questions_list"]
        for index, question in enumerate(questions):
            unique_id = f"{first_file}__v{index}"
            if unique_id not in done_list:
                self.combo_questions.set(f"Question {index}")
                self.on_combobox_2_selected(f"Question {index}")
                break

    def on_combobox_0_selected(self, selected_base_folder):
        """
        Méthode appelée lorsque le base folder est modifié.
        Actualise la liste des fichiers JSON dans le nouveau répertoire.
        """
        self.json_data_folder = selected_base_folder
        self.questions_filepath = self.load_questions_filenames()
        self.questions_dict = self.match_done_questions()

        # Met à jour le combobox des fichiers JSON
        file_display = [
            f"{file}    {len(self.questions_dict[file]['done_list'])}/{len(self.questions_dict[file]['questions_list'])}"
            for file in self.questions_dict
        ]
        self.combo_filenames.configure(values=file_display)

        self.combo_filenames.set(file_display[1])

    def on_combobox_1_selected(self, selected_file_display):
        """
        Méthode appelée lorsque le fichier JSON est modifié.
        Actualise la liste des questions dans le fichier sélectionné.
        """
        selected_file = selected_file_display.split("    ")[0]
        questions = self.questions_dict[selected_file]["questions_list"]
        done_list = self.questions_dict[selected_file]["done_list"]
        question_display = [
            f"Question {i} {'    ✔' if f'{selected_file}__v{i}' in done_list else ''}"
            for i in range(len(questions))
        ]
        self.combo_questions.configure(values=question_display)
        first_question = self.select_first_unused_question(selected_file)
        self.combo_questions.set(first_question)

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
                self.combo_base_folders.configure(values=self.json_data_folder_list)
                print(f"Ajouté : {new_folder}")
        finally:
            # Réactiver le mode topmost après la sélection
            self.attributes('-topmost', True)

    def on_combobox_2_selected(self, selected_question):
        # Extraire l'indice de la question sélectionnée
        if not selected_question:
            return
        question_index = int(selected_question.split()[1])  # Extrait l'indice après "Question"
        selected_file_display = self.combo_filenames.get()
        selected_file = selected_file_display.split("    ")[0]
        question_preview = json.dumps(self.questions_dict[selected_file]["questions_list"][question_index], indent=4, ensure_ascii=False)

        # Afficher dans le label avec mise à jour de l'état
        self.label_question_preview.config(state="normal")
        self.label_question_preview.delete("1.0", "end")
        self.label_question_preview.insert("1.0", question_preview)
        self.label_question_preview.config(state="disabled")

    def load_selected_question(self):
        # Logique pour charger la question sélectionnée
        selected_file_display = self.combo_filenames.get()
        selected_question = self.combo_questions.get()
        if not selected_file_display or not selected_question:
            ctk.CTkMessageBox.show_error("Erreur", "Veuillez sélectionner un fichier et une question.")
            return
        selected_file = selected_file_display.split("    ")[0]
        question_index = int(selected_question.split()[1])
        question_content = self.questions_dict[selected_file]["questions_list"][question_index]
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
        self.destroy()

    def add_question_in_done_csv(self, absolute_path, question_index):
        # Ouvre le fichier CSV et ajoute une entrée si elle n'existe pas déjà
        unique_id = f"{absolute_path}__v{question_index}"
        csv_path = self.already_done_questions_basepath

        # Vérifie si l'entrée existe déjà dans le fichier
        if unique_id in self.already_done_questions_filepath:
            print(f"Question déjà ajoutée : {unique_id}")
            return

        # Ajoute l'entrée au fichier CSV
        with open(csv_path, "a", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([unique_id])
        print(f"Question ajoutée au fichier : {unique_id}")