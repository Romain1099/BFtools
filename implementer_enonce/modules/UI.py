import customtkinter as ctk
import string
import os

class ExerciseEditor(ctk.CTk):#Toplevel
    def __init__(self):
        super().__init__()

        self.title("Éditeur d'Exercices")
        self.geometry("800x600")
    
    def init_widgets(self):
        """
        fabrique l'interface permettant d'avoir un menubar à gauche et un tab à droite dans des proportions 15/85. 
        le menu bar est créé via une fonction dédiée
        le tabview est créé via create_tabview(widget parent)

        """

    def create_menubar():
        """
        on veut voir sélectionner en colonne les éléments suivants : 
        niveau (combobox)
        thème (combobox)
        nom du fichier (entrytext)
        nombre de versions (sélecteur d'entier par défaut à 1)
        

        les combobox sont pourvus par lecture des dossiers situés dans inputs
        on peut y écrire donc on gère comme ça la création de nouveaux répertoires. 
        """
    def create_tabview(self,widget):
        
        # Initialisation de l'état des onglets
        self.tab_states = {
            "Nombre de versions": False,
            "Variables": False,
            "Enoncé": False,
            "Solution détaillée": False,
            "Version QCM": False,
            "Réponse courte": False,
            "Thème": False,
        }

        # Création des onglets
        self.tabview = ctk.CTkTabview(widget)
        self.tabview.pack(expand=True, fill="both")

        for category in self.tab_states.keys():
            self.create_tab(category)

        # Liste des lettres utilisées pour les noms
        self.current_letter_index = 0

    def create_tab(self, category_name):
        """Crée un onglet avec une zone modifiable et configure les widgets associés."""
        tab = self.tabview.add(category_name)

        if category_name == "Variables":
            self.create_variable_defs_tab(tab)
        else:
            # Zone de texte pour les autres catégories
            text_box = ctk.CTkTextbox(tab, width=700, height=400)
            text_box.pack(pady=10, padx=10)

    def create_variable_defs_tab(self, tab):
        """Crée un onglet spécifique pour la gestion des définitions de variables."""
        self.variable_frame = ctk.CTkFrame(tab)
        self.variable_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Ajout d'une scrollbar pour le cadre si la liste devient grande
        self.scrollable_frame = ctk.CTkScrollableFrame(self.variable_frame, width=700, height=300)
        self.scrollable_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Bouton pour ajouter une variable
        add_button = ctk.CTkButton(tab, text="Ajouter une variable", command=self.add_variable)
        add_button.pack(pady=10)

        # Gestion des variables
        self.variables = []  # Liste des variables ajoutées

    def add_variable(self):
        """Ajoute une nouvelle ligne de variable avec un nom LaTeX valide."""
        if self.current_letter_index >= len(string.ascii_lowercase):
            # Limite atteinte (26 variables), message d'erreur
            print("Limite des noms de variables atteinte.")
            return

        variable_name = f"\\newvar{string.ascii_lowercase[self.current_letter_index]}"
        self.current_letter_index += 1

        # Créer un cadre pour la variable
        variable_frame = ctk.CTkFrame(self.scrollable_frame)
        variable_frame.pack(fill="x", padx=5, pady=2)

        # Entrée modifiable
        entry = ctk.CTkEntry(variable_frame, width=550)
        entry.insert(0, f"{variable_name}{{specs}}")
        entry.pack(side="left", padx=5)

        # Bouton pour supprimer la variable
        delete_button = ctk.CTkButton(variable_frame, text="Supprimer", command=lambda: self.remove_variable(variable_frame))
        delete_button.pack(side="right", padx=5)

        # Ajouter la variable à la liste
        self.variables.append(variable_frame)

    def remove_variable(self, variable_frame):
        """Supprime une variable spécifique."""
        variable_frame.destroy()
        self.variables.remove(variable_frame)

    def export_exercise(self):
        number_versions=""
        variable_defs=""
        short=""
        mhelp=""
        answer_short=""
        theme=""
        niveau=""
        title=""
        content = f"""
{number_versions}

%%

{variable_defs}

%%

{short}

%%

{mhelp}

%%

{answer_short}

%%

{theme}
""" 
        
        export_filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)),niveau,theme,title)
        print(f"{export_filepath}.sty")
        with open(f"{export_filepath}.sty",'w',encoding="utf-8") as file:
            file.write(content)
            
if __name__ == "__main__":
    app = ExerciseEditor()
    app.mainloop()
