import customtkinter as ctk
import string
import sys
import os
import re

# Charger le chemin TCL depuis le fichier de configuration
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
tcl_config_path = os.path.join(project_root, ".tcl_path.txt")

if os.path.exists(tcl_config_path):
    with open(tcl_config_path, 'r') as f:
        tcl_path = f.read().strip()
        os.environ["TCL_LIBRARY"] = tcl_path
        print(f"TCL_LIBRARY configuré : {tcl_path}")
else:
    # Fallback sur l'ancien chemin si le fichier n'existe pas
    os.environ["TCL_LIBRARY"] = r"C:\Users\Utilisateur\AppData\Local\Programs\Python\Python311\tcl\tcl8.6"
    print("Attention: Fichier .tcl_path.txt non trouvé, utilisation du chemin par défaut")

# Ajouter dynamiquement le chemin vers la racine
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
print(project_root)
if project_root not in sys.path:
    sys.path.append(project_root)
# Importer le widget LatexText
from QF_generator.latexhighlighter.tex_highlighter import LatexText
from QF_generator.latexhighlighter.color_manager import ColorManager
from tkinter import filedialog
from version_maker import make_json_UI,spec_for_QF
from number_generators_manager import NumberGeneratorManager,NumberGeneratorType
from numbers_def import find_class_number_to_generate
from abstractor.abstract_exo_ui import AbstractExoUI
from abstractor.question_abstractor import abstract_AI

import json
class ExerciseEditor(ctk.CTk):  # Toplevel
    def __init__(self):
        super().__init__()

        self.title("Éditeur d'Exercices")
        self.geometry("800x600")
        self.exo_numbers_generators = ["ExoNumber","ArithmeticNumber"]
        self.generator_manager = NumberGeneratorManager()
        self.init_widgets()

    def init_widgets(self):
        """
        Initialise l'interface principale avec un menubar à gauche (15%) 
        et un tabview à droite (85%).
        """
        # Configuration de la grille principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        # Menubar (15%)
        self.menubar_frame = ctk.CTkFrame(self, width=150)
        self.menubar_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        self.create_menubar()

        # Tabview (85%)
        self.tabview_frame = ctk.CTkFrame(self)
        self.tabview_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        self.create_tabview(self.tabview_frame)

    def load_model_command(self):
        """
        Ouvre une boîte de dialogue pour sélectionner un fichier modèle 
        et appelle la méthode pour charger le modèle.
        """
        print(os.path.join(os.path.dirname(os.path.abspath(__file__)),"inputs"))
        filetypes = [("LaTeX Files", "*.sty *.tex"), ("Tous les fichiers", "*.*")]
        filepath = filedialog.askopenfilename(
            title="Sélectionner un fichier modèle",
            filetypes=filetypes,
            initialdir=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"inputs")
        )
        if filepath:
            self.load_existing_model(filepath)
            print(f"Modèle chargé depuis : {filepath}")

    def load_existing_model(self,filepath):
        #ouvre le document
        with open(filepath,'r',encoding='utf-8') as file:
            content=file.read()
        
        #split('%%')
        try:
            number_versions,variable_defs,enonce,solution_detaillee,version_qcm,reponse_courte,theme,*html=content.split('%%')
            try:
                print(f"HTML : '{html}'")
            except:
                html=""
        except:
            html=""
            raise ValueError(f"Le fichier chargé ne respecte par les conventions de l'application.\nSéparer les parties du contenu par des séparateurs '%%' en les disposant dans cet ordre : number_versions,variable_defs,enonce,solution_detaillee,version_qcm,reponse_courte,theme ")
        enonce=enonce#.strip()
        #enonce=re.sub(r"\n","",enonce)
        solution_detaillee=solution_detaillee#.strip()
        #re.sub(r"\n","",solution_detaillee)
        version_qcm=version_qcm#.strip()
        #version_qcm=re.sub(r"\n","",version_qcm)
        reponse_courte=reponse_courte.strip()
        reponse_courte=re.sub(r"\n","",reponse_courte)
        #appelle pour le contenu de chaque partie : 
        # self.insert_content(widget_name, content)
        self.num_versions.set(int(number_versions))
        #self.variables=[]
        self.reset_variables_defs()
        #self.insert_tab_content("Variables",variable_defs)
        self.load_variables_defs(variable_defs)
        self.insert_tab_content("Enoncé",enonce)
        self.insert_tab_content("Solution détaillée",solution_detaillee)
        self.insert_tab_content("Réponse courte",reponse_courte)
        self.insert_tab_content("Version QCM",version_qcm)
        self.insert_tab_content("Version html", html)
        self.insert_tab_content("Thème",theme)

        self.selected_theme.set(os.path.dirname(filepath).split('/')[-1:][0])
        self.selected_level.set(os.path.dirname(os.path.dirname(filepath)).split('/')[-1:][0])
        self.file_name.set(str(filepath.split('/')[-1:][0]).replace('.sty','').replace('.tex',''))
        self.update_theme_combobox(str(os.path.dirname(os.path.dirname(filepath)).split('/')[-1:][0]))
    def reset_variables_defs(self):
        for frame in self.variables:
            frame.destroy()
        self.variables = []
        
    def load_variables_defs(self,variable_defs):
        list_var=self.split_vars(variable_defs)
        for v in list_var:
            print(v)
            self.add_variable(options=v)
        #self.add_variable(options=variable_defs)

    def split_vars(self, variable_defs: str) -> list:
        """Divise les définitions LaTeX en une liste d'éléments exploitables.

        Args:
            variable_defs (str): Chaîne contenant les définitions des variables.

        Returns:
            list: Liste des définitions des variables extraites.
        """
        # Expression régulière pour repérer les définitions \def\<nom_variable>{<specs>}
        #pattern = r"\\def\\(\\w+)"
        #matches = re.findall(pattern, variable_defs)
        #number_generator=NumberGeneratorManager()
        numbers_found,nums = find_class_number_to_generate(variable_defs)
        matches=nums.split("\\def")
        # Crée une liste de dictionnaires pour chaque variable détectée
        variables = [
            f"\\def{match}" for match in matches if match.strip()!=""
        ]
        for n in numbers_found:
            variables.append(n)
        return variables
    
    def create_menubar(self):
        """
        Crée un menubar avec :
        - Niveau (combobox) : dossiers dans inputs/
        - Thème (combobox) : sous-dossiers du niveau sélectionné
        - Nom de fichier (entrée texte)
        - Nombre de versions (sélecteur entier)
        """
        # Variables
        self.selected_level = ctk.StringVar()
        self.selected_theme = ctk.StringVar()
        self.file_name = ctk.StringVar()
        self.num_versions = ctk.IntVar(value=1)
        
        # Titre du menubar
        menubar_title = ctk.CTkLabel(self.menubar_frame, text="Menu", font=("Arial", 16, "bold"))
        menubar_title.pack(pady=10)
        # Bouton Charger un modèle
        self.load_model_button = ctk.CTkButton(
            self.menubar_frame, 
            text="Charger un modèle", 
            command=self.load_model_command
        )
        self.load_model_button.pack(pady=10)

        # Bouton Abstraire un exercice
        self.load_model_button = ctk.CTkButton(
            self.menubar_frame, 
            text="Abstraire un exercice", 
            command=self.abstract_command
        )
        self.load_model_button.pack(pady=10)
        # Combobox Niveau
        ctk.CTkLabel(self.menubar_frame, text="Niveau").pack(pady=(10, 2))
        self.level_combobox = ctk.CTkComboBox(
            self.menubar_frame, variable=self.selected_level, values=self.get_folders("inputs"),
            command=self.update_theme_combobox
        )
        self.level_combobox.pack(fill="x", pady=5)

        # Combobox Thème
        ctk.CTkLabel(self.menubar_frame, text="Séquence").pack(pady=(10, 2))
        self.theme_combobox = ctk.CTkComboBox(self.menubar_frame, variable=self.selected_theme)
        self.theme_combobox.pack(fill="x", pady=5)

        # Entrée Nom du fichier
        ctk.CTkLabel(self.menubar_frame, text="Nom du fichier").pack(pady=(10, 2))
        self.file_entry = ctk.CTkEntry(self.menubar_frame, textvariable=self.file_name)
        self.file_entry.pack(fill="x", pady=5)

        # Sélecteur Nombre de versions
        ctk.CTkLabel(self.menubar_frame, text="Nombre de versions").pack(pady=(10, 2))
        self.version_selector = ctk.CTkEntry(self.menubar_frame, textvariable=self.num_versions)
        self.version_selector.pack(fill="x", pady=5)

        # Bouton Ajouter un nouveau niveau/thème
        self.add_folder_button = ctk.CTkButton(self.menubar_frame, text="Ajouter un dossier", command=self.add_new_folder)
        self.add_folder_button.pack(pady=10)

        self.add_folder_button = ctk.CTkButton(self.menubar_frame, text="Exporter le modèle", command=self.export_exercise)
        self.add_folder_button.pack(pady=10)
    def abstract_command(self):
        # charge un AbstractExoUI avec le callback(self.load_model_by_AI)
        #Fonctionnement de la classe AbstractExoUI : 
        #ctktoplevel contenant un latextext dans lequelle coller le code "input" et un bouton "abstraire". 
        #Une fois abstraire cliqué, on appelle une requete ia ( fonction abstract_AI(text) ) ou text est le contenu du latextext.
        #une fois récupéré la réponse, cette classe appelle le callback
        # Création de l'interface AbstractExoUI
        abstract_window = AbstractExoUI(
            parent=self,
            callback=self.load_model_by_AI,  # Le callback à appeler avec le résultat
            abstract_function=abstract_AI,  # La fonction IA d'abstraction
        )
        abstract_window.grab_set()  # Désactive la fenêtre parent jusqu'à la fermeture
        
    def load_model_by_AI(self,text,widget):
        print(text)
        widget.destroy()

        variables=text.split(r"%%")[0]
        enonce=text.split(r"%%")[1]
        solution_detaillee=text.split(r"%%")[2]
        version_qcm=text.split(r"%%")[3]
        reponse_courte=text.split(r"%%")[4]
        theme=text.split(r"%%")[5]
        try:
            html = text.split(r"%%")[6]
        except:
            html = ""
        self.reset_variables_defs()

        self.parse_var_from_AI(variables)
        self.insert_tab_content("Enoncé",enonce)
        self.insert_tab_content("Solution détaillée",solution_detaillee)
        self.insert_tab_content("Réponse courte",reponse_courte)
        self.insert_tab_content("Version QCM",version_qcm)
        self.insert_tab_content("Version html", html)
        self.insert_tab_content("Thème",theme)

    def parse_var_from_AI(self,variables:str):
        
        pattern = r"\\def\\([a-zA-Z0-9_]+)\{([^\}]+)\}"

        # Recherche des correspondances dans la chaîne
        matches = re.findall(pattern, variables)
        print(f"matches : {matches}")
        variable_list = []

        # Parcours des correspondances
        for var_name, var_value in matches:
            # Ajout dans la liste des variables sous forme de dictionnaire
            variable = {"name": var_name, "value": var_value}
            variable_list.append(variable)
            
            try:
                # Conversion de la valeur en int ou float
                if "." in var_value:  # Si la valeur contient un point, on suppose un float
                    var_value_num = float(var_value)
                    var_type = "float"
                else:
                    var_value_num = int(var_value)
                    var_type = "int"
            except ValueError:
                print(f"Erreur : La valeur de la variable '{var_name}' n'est pas un nombre valide : {var_value}")
                continue  # Ignore cette variable si la conversion échoue

            interval=f"0<=x<={var_value} x!=0 x!=1"
            # Définir l'intervalle en fonction du signe de la valeur
            if var_value_num < 0:
                interval = f"{var_value_num}<=x<={abs(var_value_num)}"
            else:
                interval = f"0<=x<={var_value_num}"

            # Combinaison des spécifications complètes
            full_spec = f"{interval} {var_type}"
            full_name = f"def\\{var_name[:-1]}"
            # Appel de la méthode pour traiter la variable
            self.add_variable(name=full_name, specs=full_spec)
    def create_tabview(self, widget):
        """
        Initialise le Tabview avec les onglets requis.
        """
        self.tab_states = {
            "Variables": False,
            "Enoncé": False,
            "Solution détaillée": False,
            "Réponse courte": False,
            "Version QCM": False,
            "Version html" : False,
            "Thème": False,
        }

        self.tabview = ctk.CTkTabview(widget)
        self.tabview.pack(expand=True, fill="both")

        for category in self.tab_states.keys():
            self.create_tab(category)

        self.current_letter_index = 0

    def create_tab(self, category_name):
        """Crée un onglet avec un contenu spécifique."""
        tab = self.tabview.add(category_name)
        if category_name=="Variables":
            print(f"{category_name} triggered.")
            self.create_variable_defs_tab(tab)
        else:
            #text_box = ctk.CTkTextbox(tab, width=700, height=400)#
            text_box = LatexText(parent=tab,master_widget=tab,height=400,color_cfg_path="modules/color_cfg.json")#, width=100
            text_box.pack(pady=10, padx=10)

    def create_variable_defs_tab(self, tab):
        """Crée un onglet pour les variables."""
        self.variable_frame = ctk.CTkScrollableFrame(tab)#, width=700, height=400
        self.variable_frame.pack(expand=True, fill="both", pady=10, padx=10)

        add_button = ctk.CTkButton(tab, text="Ajouter une variable", command=self.add_variable)
        add_button.pack(pady=10)

        self.variables = []

    def add_variable(self,options:str|None=None,specs:str|None="specs",name="newvar"):
        """Ajoute une nouvelle variable."""
        
        if self.current_letter_index >= len(string.ascii_lowercase):
            print("Limite des noms de variables atteinte.")
            return

        variable_name = f"\\{name}{string.ascii_lowercase[self.current_letter_index]}"
        self.current_letter_index += 1
        if options==None:
            options=f"{variable_name}{{{specs}}}"
        frame = ctk.CTkFrame(self.variable_frame)
        frame.pack(fill="x", pady=2, padx=5)

        entry = LatexText(parent=frame,master_widget=frame,height=6,color_cfg_path="modules/color_cfg.json")#ctk.CTkEntry(frame)#, width=550
        entry.insert("0.0", options.split("class=")[0])
        entry.pack(side="left", padx=5,fill="x")#,expand=True)

        generator_combobox = ctk.CTkComboBox(frame,values=self.exo_numbers_generators,command=lambda event, text_widget=entry: self.on_generator_combobox_selected(value=event,text_widget=text_widget))
        generator_combobox.pack(side="right", padx=5)
        try:
            gen_name=options.split("class=")[1]
        except:
            gen_name=self.exo_numbers_generators[0]
        generator_combobox.set(gen_name)

        delete_button = ctk.CTkButton(frame, text="Supprimer", command=lambda: frame.destroy())
        delete_button.pack(side="right", padx=5)

        self.variables.append(frame)

    def on_generator_combobox_selected(self,value,text_widget):
        text_widget.delete("0.0","end")
        defaults = self.generator_manager.get_class_defaults(type=f"{value.upper()}")
        def_text= self.generator_manager.generate_placeholders_number(number_class=value.upper(),input=defaults[value])
        text_widget.insert("0.0", def_text)
        pass
    def update_theme_combobox(self, selected_level):
        """Met à jour les thèmes en fonction du niveau sélectionné."""
        themes = self.get_folders(os.path.join("inputs", selected_level))
        self.theme_combobox.configure(values=themes)

    def get_folders(self, base_path):
        """Renvoie la liste des dossiers dans le chemin donné."""
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        return [name for name in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, name))]

    def add_new_folder(self):
        """Ajoute un nouveau dossier via une boîte de dialogue."""
        new_folder = filedialog.askdirectory(title="Sélectionnez ou créez un nouveau dossier")
        if new_folder:
            print(f"Nouveau dossier ajouté : {new_folder}")

    def export_exercise(self):
        """
        Exporte les informations dans un fichier .sty.
        Rassemble les données des onglets et les autres saisies.
        """
        # Récupération des informations nécessaires
        number_versions = self.num_versions.get()
        variable_defs,variable_list = self.get_variable_definitions()
        enonce = self.get_tab_content("Enoncé")
        enonce=enonce#.strip()
        #enonce=re.sub(r"\n","",enonce)
        solution_detaillee = self.get_tab_content("Solution détaillée")
        solution_detaillee=solution_detaillee#.strip()
        #solution_detaillee=re.sub(r"\n","",solution_detaillee)
        version_qcm = self.get_tab_content("Version QCM")
        #version_qcm=re.sub(r"\n","",version_qcm)
        reponse_courte = self.get_tab_content("Réponse courte")
        reponse_courte=reponse_courte.strip()
        html = self.get_tab_content("Version html")

        reponse_courte=re.sub(r"\n","",reponse_courte)
        theme = self.selected_theme.get()
        niveau = self.selected_level.get()
        title = self.file_name.get()

        if not (niveau and theme and title):
            print("Erreur : Niveau, Thème ou Nom de fichier manquants.")
            return

        # Création du contenu formaté
        content = f"""
{number_versions}
%%
{variable_defs}
%%
{enonce}
%%
{solution_detaillee}
%%
{version_qcm}
%%
{reponse_courte}
%%
{theme}
%%
{html}
"""

        # Chemin d'exportation
        export_dir = str(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "inputs", niveau, theme)).replace('\n','')
        os.makedirs(export_dir, exist_ok=True)
        export_filepath = os.path.join(export_dir, f"{title}.sty")

        # Écriture dans le fichier
        with open(export_filepath, 'w', encoding="utf-8") as file:
            file.write(content)

        print(f"Exercice exporté dans : {export_filepath}")#\n {content}
        export_json_path = f'{export_filepath.replace("inputs","json_productions").replace(".sty","")}.json'
        os.makedirs(os.path.dirname(export_json_path), exist_ok=True)
        print(f"""
make_json_UI(input_filepath={export_filepath},output_filepath={export_json_path},specs=spec_for_QF(num_versions={number_versions}))
""")
        dict=make_json_UI(input_filepath=export_filepath,output_filepath=export_json_path,specs=spec_for_QF(num_versions=number_versions))
        with open(export_json_path, 'w', encoding="utf-8") as file:
           json.dump(dict, file,indent=4,ensure_ascii=False)
        print(f"Exercice exporté dans : {export_json_path}")

    def get_variable_definitions(self):
        """
        Rassemble les définitions des variables ajoutées.
        """
        definitions = []
        for variable_frame in self.variables:
            #print("here the classes",[v.__class__.__name__ for v in variable_frame.winfo_children()])
            #entry = [v for v in variable_frame.winfo_children() if v.__class__.__name__ == "ScrollableFrame"][0]  # On récupère l'entrée texte
            f = variable_frame.winfo_children()[0]
            entry = [v for v in f.winfo_children() if v.__class__.__name__ == "LatexText"][0]
            definitions.append(re.sub("\n","",entry.get("0.0","end").strip()))
        return "\n".join(definitions),definitions

    def get_tab_content(self, tab_name):
        """
        Récupère le contenu texte d'un onglet donné.
        """
        tab = self.tabview.tab(tab_name)
        if tab.winfo_children():
            textbox = tab.winfo_children()[0]
            entry = [v for v in textbox.winfo_children() if v.__class__.__name__ == "LatexText"][0]
            return entry.get("1.0", "end")#.strip()
        return ""
    
    def insert_tab_content(self, tab_name,content):
        """
        Récupère le contenu texte d'un onglet donné.
        """
        tab = self.tabview.tab(tab_name)
        #print([f"{child.__class__.__name__}" for child in tab.winfo_children()])
        if tab.winfo_children():
            textbox = tab.winfo_children()[0]
            try:
                textbox.delete("1.0", "end")
                return textbox.insert("1.0", content)
            except:
                #print([f"{child.__class__.__name__}" for child in textbox.winfo_children()])
                for child in textbox.winfo_children():
                    if f"{child.__class__.__name__}" == "LatexText":
                        #print(f"{child.__class__.__name__}")
                        child.delete("1.0", "end")
                        return child.insert("1.0", content)
        return ""

if __name__ == "__main__":
    app = ExerciseEditor()
    app.mainloop()
