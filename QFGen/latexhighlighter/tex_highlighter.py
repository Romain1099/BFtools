import tkinter as tk
import customtkinter as ctk
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.token import Token, _TokenType
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import os
import subprocess
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import re
import time
import sys
try:
    # Version actuelle (préférée si vous exécutez le script dans le contexte du package)
    from latexcompiler import LaTeXCompiler, CompilationError
    #from question_abstractor import ExoAbstractor
    from latexhighlighter.latex_modifier import LaTeXModifier
    from .color_manager import ColorManager
except ImportError:
    # Ajout dynamique du chemin vers la racine du projet
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
    if project_root not in sys.path:
        sys.path.append(project_root)

    # Imports absolus
    #from QF_generator.question_abstractor import ExoAbstractor
    from QF_generator.latexcompiler import LaTeXCompiler, CompilationError
    from .color_manager import ColorManager


class LatexText(ScrolledText):
    def __init__(self, parent=None, compiler=None, pdf_viewer=None,fancy_page_parameters=None,fancy_page_option=True,empty_document=None,header_filepath=None,final_document=None,output_directory=None,master_widget=None,topmost_option=False,color_cfg_path=None, **kwargs):
        super().__init__(master=parent, **kwargs)
        if not empty_document:
            self.empty_document="empty_document.tex"
        else:
            self.empty_document=empty_document
        if not header_filepath:
            self.header_filepath="entete.tex"
        else:
            self.header_filepath=header_filepath
        if not self.load_header():
            print("L'en-tete du document tex n'a pas été trouvée.")
        if not final_document:
            self.output_document="document.tex"
        else:
            self.output_document=final_document
        
        self.master_widget=master_widget
        self.topmost_option=topmost_option
        self.compiler = compiler
        self.pdf_viewer = pdf_viewer
        self.output_directory=output_directory
        self.fancy_page=fancy_page_parameters
        self.fancy_page_option=fancy_page_option
        self.fontsize=14
        self.bind("<Control-MouseWheel>", self.on_ctrl_mouse_wheel)

        self.bind("<KeyRelease>", self.on_key_release)
        self.bind("<Return>", self.on_return_key)
        self.bind("<Tab>", self.on_tab_key)
        self.bind("<Button 3>",self.on_right_click)
        #chargement des couleurs
        if not color_cfg_path:
            color_cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"qf_gen_config/color_cfg.json")
        self.init_colors(color_cfg_path=color_cfg_path)
        
        #self.setup_tags() #Important pour retrouver la version de base.
        self.open_environments = []
        self.open_commands = []  # Liste des commandes non fermées
        self.placeholders = []
        self.already_inserted_dictionnary={}
        self.inactivity_delay = 10000  # 10 seconds
        self.inactivity_callback = None

    def init_colors(self,color_cfg_path):
        cfg_path=color_cfg_path
        self.color_manager = ColorManager(config_path=cfg_path,widget=self,fontsize=14) #config_path=None pour aller récupérer le fichier de couleurs de qf_gen_config.
        self.color_manager.init_widget()
        self.color_manager.apply_tag_colors()
        '''self.configure(
            #font=("Fira Code", self.fontsize), 
            undo=True, 
            wrap='word',
            background='#2e2e2e',  # Couleur de fond gris sombre
            foreground='#ffffff',  # Couleur du texte blanc
            insertbackground='white',  # Couleur du curseur blanc
            selectbackground='#4a4a4a',  # Couleur de sélection gris foncé
            selectforeground='#ffffff'  # Couleur du texte sélectionné blanc
        )'''

    def on_ctrl_mouse_wheel(self, event):
        """Augmente ou diminue la taille de la police avec Ctrl + Molette"""
        # Récupérer les dimensions actuelles du widget
        current_width = self.winfo_width()
        current_height = self.winfo_height()

        # Ajuster la taille de la police
        if event.delta > 0:  # Molette vers le haut
            self.fontsize += 1
        elif event.delta < 0:  # Molette vers le bas
            self.fontsize -= 1
        '''self.configure(
            #font=("Fira Code", self.fontsize), 
            undo=True, 
            wrap='word',
            background='#2e2e2e',  # Couleur de fond gris sombre
            foreground='#ffffff',  # Couleur du texte blanc
            insertbackground='white',  # Couleur du curseur blanc
            selectbackground='#4a4a4a',  # Couleur de sélection gris foncé
            selectforeground='#ffffff'  # Couleur du texte sélectionné blanc
        )'''

        self.highlight_syntax()
 
    def on_right_click(self,event):
        try:
            selected_text = self.selection_get()
            print(selected_text)
            if selected_text:
                #self.attributes("-topmost", False)
                self.show_options_window(selected_text)
        except Exception as _:
            pass
    def show_options_window(self, selected_text):
        self.options_window = LaTeXModifier(parent = self, texte = selected_text,master_widget=self.master_widget,topmost_option = self.topmost_option)

    def load_header(self):
        try:
            with open(self.header_filepath,'r',encoding='utf-8') as file:
                header=file.read()
            self.header_content=header
            return True
        except:
            return False

    def setup_tags(self):
        coloration_dictionnary = {
            "Blue pastel": "#61afef",
            "Red pastel": "#e06c75",
            "Green pastel": "#98c379",
            "Grey pastel": "#5c6370",
            "Orange pastel": "#d19a66",
            "Purple pastel": "#c678dd",
            "Dark grey pastel": "#4b5263",
            "Cyan pastel": "#56b6c2",
            "Red light":"#FFCCCC"
        }
        
        # Dictionnaire de configuration des tags
        '''tag_configurations = {
            str(Token.Keyword): {"foreground": coloration_dictionnary["Blue pastel"], "font": ("Fira Code", self.fontsize, "bold")},  # Blue pastel
            str(Token.Name): {"foreground": coloration_dictionnary["Red pastel"], "font": ("Fira Code", self.fontsize, "bold")},  # Red pastel
            str(Token.String): {"foreground": coloration_dictionnary["Green pastel"], "font": ("Fira Code", self.fontsize, "bold")},  # Green pastel
            str(Token.Comment): {"foreground": coloration_dictionnary["Grey pastel"], "font": ("Fira Code", self.fontsize, "italic")},  # Grey pastel
            str(Token.Number): {"foreground": coloration_dictionnary["Orange pastel"], "font": ("Fira Code", self.fontsize, "bold")},  # Orange pastel
            "math": {"foreground": coloration_dictionnary["Purple pastel"], "font": ("Fira Code", self.fontsize, "bold")},  # Purple pastel
            "placeholder": {"foreground": coloration_dictionnary["Dark grey pastel"], "font": ("Fira Code", self.fontsize, "italic")},  # Dark grey pastel
            "text_command": {"foreground": coloration_dictionnary["Cyan pastel"], "font": ("Fira Code", self.fontsize, "bold")},  # Cyan pastel
            "textbf_command": {"foreground": coloration_dictionnary["Cyan pastel"], "font": ("Fira Code", self.fontsize, "bold")},  # Cyan pastel
            "unclosed_env": {"background":coloration_dictionnary["Red light"], "font": ("Fira Code", self.fontsize, "bold")},# Red light
        }'''
        tag_configurations = {
            str(Token.Keyword): {
                "foreground": "#569CD6",  # Bleu pour les mots-clés (VSCode)
                "font": ("Fira Code", self.fontsize, "bold")
            },
            str(Token.Name): {
                "foreground": "#DCDCAA",  # Jaune pour les noms (variables, fonctions)
                "font": ("Fira Code", self.fontsize, "normal")
            },
            str(Token.String): {
                "foreground": "#CE9178",  # Rouge orangé pour les chaînes de caractères
                "font": ("Fira Code", self.fontsize, "normal")
            },
            str(Token.Comment): {
                "foreground": "#6A9955",  # Vert pour les commentaires
                "font": ("Fira Code", self.fontsize, "italic")
            },
            str(Token.Number): {
                "foreground": "#B5CEA8",  # Vert clair pour les nombres
                "font": ("Fira Code", self.fontsize, "normal")
            },
            "math": {
                "foreground": "#B5CEA8",#"#C586C0",  # Violet clair pour les éléments mathématiques
                "font": ("Fira Code", self.fontsize, "normal")
            },
            "placeholder": {
                "foreground": "#808080",  # Gris pour les placeholders
                "font": ("Fira Code", self.fontsize, "italic")
            },
            "command": {
                "foreground": "#9CDCFE",  # Cyan pour les commandes de texte
                "font": ("Fira Code", self.fontsize, "normal")
            },
            "textbf_command": {
                "foreground": "#9CDCFE",  # Cyan clair pour les commandes en gras
                "font": ("Fira Code", self.fontsize, "bold")
            },
            "unclosed_env": {
                "background": "#F44747",  # Rouge vif pour les environnements non fermés
                "font": ("Fira Code", self.fontsize, "bold"),
                "foreground": "#FFFFFF"  # Texte en blanc pour contraste
            },
        }
        # Configuration des tags
        for tag, config in tag_configurations.items():
            self.tag_configure(tag, **config)
        #self.tag_configure("textbf_command", foreground="#4FC1FF", font=("Fira Code", self.fontsize, "bold"))
        #self.tag_configure("text_command", foreground="#9CDCFE", font=("Fira Code", self.fontsize, "normal"))
        #self.tag_configure("math", foreground="#C586C0", font=("Fira Code", self.fontsize, "bold"))  # Violet pour les délimiteurs
        #self.tag_configure("math_content", foreground="#B5CEA8", font=("Fira Code", self.fontsize, "normal"))  # Vert pour le contenu

    def on_key_release(self, event=None):
        #self.highlight_syntax() #un peu trop régulier
        #self.check_unclosed_environments()
        #self.print_unclosed_environments()
        if self.inactivity_callback:
            self.after_cancel(self.inactivity_callback)
        #self.inactivity_callback = self.after(self.inactivity_delay, self.auto_compile)

    def on_return_key(self, event=None):
        current_line = self.get("insert linestart", "insert")
        indent_level = len(current_line) - len(current_line.lstrip(' '))
        self.insert("insert", '\t') # * indent_level "\n" + 
        self.check_unclosed_environments()
        #self.print_unclosed_environments()
        self.check_unclosed_commands()
        #self.print_unclosed_commands()
        self.highlight_syntax()
        return #"break"

    def on_tab_key(self, event=None):
        # Detecter 
        # Close the currently open environment
        if self.open_environments:
            last_open = self.open_environments.pop()
            self.replace_placeholder(last_open)
        return "break"

    def replace_placeholder(self, closing_tag):
        # Replace the placeholder with the actual closing tag
        for placeholder in self.placeholders:
            start, end = placeholder
            if self.get(start, end).strip() == f"{closing_tag}":
                self.delete(start, end)
                self.insert(start, closing_tag)
                self.tag_remove("placeholder", start, end)
                break
    def should_wait(self, after_env_content):
        """
        Détermine si le contenu contient des { ou des [ qui ne sont pas refermés.
        Si c'est le cas, on retourne True, sinon False.
        """
        stack = []

        for char in after_env_content:
            if char in "{[":
                stack.append(char)
            elif char in "]}":
                if not stack:
                    return True  # Si on trouve une fermeture sans ouverture correspondante
                open_char = stack.pop()
                if (open_char == "{" and char != "}") or (open_char == "[" and char != "]"):
                    return True  # Si les caractères ne correspondent pas

        # Si la pile n'est pas vide, il y a des ouvertures non fermées
        return len(stack) != 0
    def check_unclosed_environments(self):
        content = self.get("1.0", tk.END)
        open_envs = []
        lines = content.split('\n')

        begin_pattern = re.compile(r'\\begin\{([^\}]+)\}(?:\[[^\]]*\])?(?:\{[^\}]*\})?\s')
        braces_pattern = re.compile(r'\{?')
        for line in lines:
            begin_matches = begin_pattern.finditer(line)
            #alternative_pattern
            for match in begin_matches:
                env_name = match.group(1)
                after_env_content = line[match.end():].strip()
                #if not self.should_wait(after_env_content):
                open_envs.append(env_name)

            if "\\end{" in line:
                env_name = line.split("\\end{")[1].split("}")[0]
                if env_name in open_envs:
                    open_envs.remove(env_name)

        self.open_environments = [f"\\end{{{env}}}" for env in open_envs]

        for placeholder in self.placeholders:
            self.tag_remove("placeholder", placeholder[0], placeholder[1])

        self.placeholders = []
        if open_envs:
            current_line_index = self.index("insert linestart")
            current_line_content = self.get(current_line_index, "insert lineend")
            if current_line_content.strip():
                current_indent = len(current_line_content) - len(current_line_content.lstrip())
            else:
                current_indent = 0

        for env in open_envs:
            placeholder_text = f"\n{' ' * (current_indent + 4)}%cursor here\n{' ' * current_indent}\\end{{{env}}}"
            current_line_index = self.index("insert linestart")
            if placeholder_text not in self.get(current_line_index, "insert lineend"):
                already_closed = self.already_inserted_dictionnary.get(placeholder_text)
                if not already_closed:
                    self.insert("insert", placeholder_text)
                    start_index = self.index(f"insert - {len(placeholder_text)}c")
                    end_index = self.index(f"{start_index} + {len(placeholder_text)}c")
                    self.placeholders.append((start_index, end_index))
                    self.tag_add("placeholder", start_index, end_index)
                    self.already_inserted_dictionnary[placeholder_text] = True

        cursor_position = self.search("%cursor here", "1.0", tk.END)
        if cursor_position:
            self.mark_set("insert", cursor_position)
            self.delete(cursor_position, f"{cursor_position} + {len('%cursor here')}c")

        for env in open_envs:
            start_index = self.search(f"\\begin{{{env}}}", "1.0", tk.END)
            end_index = self.index(f"{start_index} lineend")
            self.tag_add("unclosed_env", start_index, end_index)

    def check_unclosed_environments_demi(self):
        content = self.get("1.0", tk.END)
        open_envs = []
        lines = content.split('\n')
        
        for line in lines:
            if "\\begin{" in line:
                env_name = line.split("\\begin{")[1].split("}")[0]
                try:
                    after_env_content=line.split("\\begin{")[1].split("}")[1].strip("")
                    if not self.should_wait(after_env_content):
                        open_envs.append(env_name)
                except Exception as e:
                    print(f"Erreur dans check_unclosed_environments_demi : {e}")
            if "\\end{" in line:
                env_name = line.split("\\end{")[1].split("}")[0]
                if env_name in open_envs:
                    open_envs.remove(env_name)
        
        self.open_environments = [f"\\end{{{env}}}" for env in open_envs]

        for placeholder in self.placeholders:
            self.tag_remove("placeholder", placeholder[0], placeholder[1])

        self.placeholders = []
        if open_envs:
            current_line_index = self.index("insert linestart")
            current_line_content = self.get(current_line_index, "insert lineend")
            if current_line_content.strip():
                current_indent = len(current_line_content) - len(current_line_content.lstrip())
            else:
                current_indent = 0

        for env in open_envs:
            placeholder_text = f"\n{' ' * (current_indent + 4)}%cursor here\n{' ' * current_indent}\\end{{{env}}}"
            current_line_index = self.index("insert linestart")
            if placeholder_text not in self.get(current_line_index, "insert lineend"):
                already_closed=self.already_inserted_dictionnary.get(placeholder_text)
                if not already_closed:
                    self.insert("insert", placeholder_text)
                    start_index = self.index(f"insert - {len(placeholder_text)}c")
                    end_index = self.index(f"{start_index} + {len(placeholder_text)}c")
                    self.placeholders.append((start_index, end_index))
                    self.tag_add("placeholder", start_index, end_index)
                    self.already_inserted_dictionnary[placeholder_text]=True

        cursor_position = self.search("%cursor here", "1.0", tk.END)
        if cursor_position:
            self.mark_set("insert", cursor_position)
            self.delete(cursor_position, f"{cursor_position} + {len('%cursor here')}c")

        for env in open_envs:
            start_index = self.search(f"\\begin{{{env}}}", "1.0", tk.END)
            end_index = self.index(f"{start_index} lineend")
            self.tag_add("unclosed_env", start_index, end_index)

    def check_unclosed_environments_old(self):
        content = self.get("1.0", tk.END)
        open_envs = []
        lines = content.split('\n')
        
        for line in lines:
            if "\\begin{" in line:
                env_name = line.split("\\begin{")[1].split("}")[0]
                open_envs.append(env_name)
            if "\\end{" in line:
                env_name = line.split("\\end{")[1].split("}")[0]
                if env_name in open_envs:
                    open_envs.remove(env_name)
        
        self.open_environments = [f"\\end{{{env}}}" for env in open_envs]

        # Clear previous placeholders
        for placeholder in self.placeholders:
            self.tag_remove("placeholder", placeholder[0], placeholder[1])

        # Add new placeholders only if they are not already present
        self.placeholders = []
        if open_envs:
            current_line_index = self.index("insert linestart")
            current_line_content = self.get(current_line_index, "insert lineend")
            if current_line_content.strip():
                current_indent = len(current_line_content) - len(current_line_content.lstrip())
            else:
                current_indent = 0

        for env in open_envs:
            placeholder_text = f"\n{' ' * (current_indent + 4)}%cursor here\n{' ' * current_indent}\\end{{{env}}}"
            current_line_index = self.index("insert linestart")
            if placeholder_text not in self.get(current_line_index, "insert lineend"):
                self.insert("insert", placeholder_text)
                start_index = self.index(f"insert - {len(placeholder_text)}c")
                end_index = self.index(f"{start_index} + {len(placeholder_text)}c")
                self.placeholders.append((start_index, end_index))
                self.tag_add("placeholder", start_index, end_index)

        # Find the position of '%cursor here' and place the cursor there
        cursor_position = self.search("%cursor here", "1.0", tk.END)
        if cursor_position:
            self.mark_set("insert", cursor_position)
            self.delete(cursor_position, f"{cursor_position} + {len('%cursor here')}c")

    def check_unclosed_commands(self):
        content = self.get("1.0", tk.END)
        open_cmds = []
        lines = content.split('\n')

        for line in lines:
            #compter et lister les occurences de '{' avec leurs positions, idem pour les '}' et comparer les nombres. 
            #si différence alors on ferme l'accolade avec l'insert et autoindentation
            if "\\" in line and "{" in line and "}" not in line:
                cmd_name = line.split("\\")[1].split("{")[0].strip()
                open_cmds.append(cmd_name)

        self.open_commands = open_cmds
        previous_line = self.get("insert -1line linestart", "insert -1line lineend")

        # Check if we need to insert a placeholder for commands
        if self.open_commands:
            last_open = self.open_commands[-1]
            if last_open and not previous_line.strip().endswith('}'):
                placeholder_text = f"\n{' ' * 4}%cursor here\n"+"}"
                self.insert("insert", placeholder_text)
                self.open_commands.pop()
                self.tag_add("placeholder", f"insert - 1c", "insert")
        # Find the position of '%cursor here' and place the cursor there
        cursor_position = self.search("%cursor here", "1.0", tk.END)
        if cursor_position:
            self.mark_set("insert", cursor_position)
            self.delete(cursor_position, f"{cursor_position} + {len('%cursor here')}c")
        

    def print_unclosed_elements(self):
        print("Environnements non fermés:", self.open_environments)
        print("Commandes non fermées:", self.open_commands)

    def highlight_syntax_old(self):
        content = self.get("1.0", tk.END)
        lexer = get_lexer_by_name("latex")
        tokens = lexer.get_tokens(content)

        self.mark_set("range_start", "1.0")
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", tk.END)

        for ttype, value in tokens:
            start_index = self.index("range_start")
            end_index = f"{start_index}+{len(value)}c"
            self.mark_set("range_end", end_index)
            self.tag_add(str(ttype), "range_start", "range_end")
            
            if ttype in Token.Name.Function:
                self.tag_add(str(Token.Keyword), "range_start", "range_end")
            if "$" in value or "\\" in value:
                self.tag_add("math", "range_start", "range_end")
                if ttype in Token.Keyword or ttype in Token.Name:
                    self.tag_add(str(Token.Keyword), "range_start", "range_end")

            self.mark_set("range_start", "range_end")
            if value.startswith(r'\text{'):
                self.tag_add("text_command", start_index, end_index)
            elif value.startswith(r'\textbf{'):
                self.tag_add("textbf_command", start_index, end_index)

        self.check_unclosed_environments()
        #self.abstract()  #tentative non encore fonctionnelle d'utilisation de l'abstraction. Il manque de diversité de commandes pour endre l'ensemble vraiment pertinent.

    def highlight_syntax_semi_adaptative(self):
        content = self.get("1.0", tk.END)
        lexer = get_lexer_by_name("latex")
        tokens = lexer.get_tokens(content)

        # Réinitialiser les tags
        self.mark_set("range_start", "1.0")
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", tk.END)
        self.tag_configure("default", font=("Fira Code", self.fontsize))
        self.tag_add("default", "1.0", tk.END)  # Réapplique à tout le texte existant
        # Expressions régulières pour accolades {} et crochets []
        braces_pattern = re.compile(r'\{([^}]*)\}')      # Accolades { ... }
        brackets_pattern = re.compile(r'\[([^\]]*)\]')  # Crochets [ ... ]
        brackets_number_pattern = re.compile(r'\[[^\]]*?\b\d+(\.\d+)?\b[^\]]*?\]')  # Nombres entre []

        # Pattern pour détecter tous les nombres
        number_pattern = re.compile(r'\b\d+(\.\d+)?\b')  # Entiers et décimaux
        # Patterns pour détecter les nombres dans {} et []
        braces_number_pattern = re.compile(r'\{[^}]*?\b\d+(\.\d+)?\b[^}]*?\}')  # Nombres entre {}
        brackets_number_pattern = re.compile(r'\[[^\]]*?\b\d+(\.\d+)?\b[^\]]*?\]')  # Nombres entre []

        # 1. Première passe : appliquer les tags de base avec le lexer
        for ttype, value in tokens:
            start_index = self.index("range_start")
            end_index = f"{start_index}+{len(value)}c"
            self.mark_set("range_end", end_index)

            # Appliquer les styles de base
            if ttype in Token.Keyword:
                self.tag_add("Token.Keyword", "range_start", "range_end")
            elif ttype in Token.Comment:
                self.tag_add("Token.Comment", "range_start", "range_end")
            elif ttype in Token.String:
                self.tag_add("Token.String", "range_start", "range_end")
            elif ttype in Token.Number:
                self.tag_add("Token.Number", "range_start", "range_end")
            elif ttype in Token.Name or ttype in Token.Operator:
                self.tag_add("command", "range_start", "range_end")

            # Avancer dans le texte
            self.mark_set("range_start", "range_end")

        # 2. Deuxième passe : détection manuelle des blocs { ... } et [ ... ]
        for line_num in range(1, int(self.index("end-1c").split(".")[0]) + 1):
            line_start = f"{line_num}.0"
            line_end = f"{line_num}.end"
            line_text = self.get(line_start, line_end)

            # Appliquer les tags pour accolades { ... }
            for match in braces_pattern.finditer(line_text):
                start = self.index(f"{line_start}+{match.start(0)}c")
                end = self.index(f"{line_start}+{match.end(0)}c")
                self.tag_add("braces", start, end)

            # Appliquer les tags pour crochets [ ... ]
            for match in brackets_pattern.finditer(line_text):
                start = self.index(f"{line_start}+{match.start(0)}c")
                end = self.index(f"{line_start}+{match.end(0)}c")
                self.tag_add("brackets", start, end)
            # Rechercher et appliquer le tag pour chaque nombre
            for match in number_pattern.finditer(line_text):
                num_start = self.index(f"{line_start}+{match.start()}c")
                num_end = self.index(f"{line_start}+{match.end()}c")
                self.tag_add("Token.Number", num_start, num_end)
            # Nombres dans {}
            for match in braces_number_pattern.finditer(line_text):
                for number in number_pattern.finditer(match.group(0)):
                    num_start = self.index(f"{line_start}+{match.start(0)+number.start()}c")
                    num_end = self.index(f"{line_start}+{match.start(0)+number.end()}c")
                    self.tag_add("number_braces", num_start, num_end)

            # Nombres dans []
            for match in brackets_number_pattern.finditer(line_text):
                for number in number_pattern.finditer(match.group(0)):
                    num_start = self.index(f"{line_start}+{match.start(0)+number.start()}c")
                    num_end = self.index(f"{line_start}+{match.start(0)+number.end()}c")
                    self.tag_add("number_brackets", num_start, num_end)

        # 3. Configuration des tags (styles)
        '''self.tag_configure("Token.Keyword", foreground="#569CD6", font=("Fira Code", self.fontsize, "bold"))  # Bleu mots-clés
        self.tag_configure("Token.Comment", foreground="#808080", font=("Fira Code", self.fontsize, "italic"))  # Gris standard pour commentaires
        self.tag_configure("Token.String", foreground="#CE9178", font=("Fira Code", self.fontsize, "normal"))  # Rouge chaînes
        self.tag_configure("Token.Number", foreground="#B5CEA8", font=("Fira Code", self.fontsize, "normal"))  # Vert clair nombres
        self.tag_configure("braces", foreground="#E6C200", font=("Fira Code", self.fontsize, "normal"))  # Jaune atténué pour {}   
        self.tag_configure("brackets", foreground="#C586C0", font=("Fira Code", self.fontsize, "normal"))  # Orange atténué pour []
        self.tag_configure("number_braces", foreground="#B5CEA8", font=("Fira Code", self.fontsize, "bold"))  # Vert clair pour nombres {}
        self.tag_configure("number_brackets", foreground="#A5B8C8", font=("Fira Code", self.fontsize, "bold"))  # Bleu-gris pour nombres []
        self.tag_configure("math", foreground="#B5CEA8", font=("Fira Code", self.fontsize, "bold"))  # Vert clair mathématiques
        self.tag_configure("command", foreground="#569CD6", font=("Fira Code", self.fontsize, "normal"))  # Bleu commandes'''
        self.color_manager.apply_tag_colors()
        self.check_unclosed_environments()
    def highlight_syntax(self):
        content = self.get("1.0", tk.END)
        lexer = get_lexer_by_name("latex")
        tokens = lexer.get_tokens(content)

        # Réinitialiser les tags
        self.mark_set("range_start", "1.0")
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", tk.END)
        self.tag_configure("default", font=("Fira Code", self.fontsize))
        self.tag_add("default", "1.0", tk.END)  # Réapplique à tout le texte existant

        # Expressions régulières
        braces_pattern = re.compile(r'\\[a-zA-Z]+\{([^}]*)\}')  # Commandes avec contenu {}
        inline_math_pattern = re.compile(r'\$(.*?)\$')         # Mode mathématique $...$
        number_pattern = re.compile(r'\b\d+(\.\d+)?\b')        # Nombres simples
        brackets_pattern = re.compile(r'\[([^\]]*)\]')  # Crochets [ ... ]
        brackets_number_pattern = re.compile(r'\[[^\]]*?\b\d+(\.\d+)?\b[^\]]*?\]')  # Nombres entre []
        # 1. Première passe : lexer pour les bases
        for ttype, value in tokens:
            start_index = self.index("range_start")
            end_index = f"{start_index}+{len(value)}c"
            self.mark_set("range_end", end_index)

            if ttype in Token.Keyword:
                self.tag_add("Token.Keyword", "range_start", "range_end")
            elif ttype in Token.Comment:
                self.tag_add("Token.Comment", "range_start", "range_end")
            elif ttype in Token.String:
                self.tag_add("Token.String", "range_start", "range_end")
            elif ttype in Token.Number:
                self.tag_add("Token.Number", "range_start", "range_end")
            elif ttype in Token.Name or ttype in Token.Operator:
                self.tag_add("command", "range_start", "range_end")

            self.mark_set("range_start", "range_end")
        # 2. Deuxième passe : détection récursive des commandes avec contenu {}
        for match in braces_pattern.finditer(content):
            start, end = match.span()
            command_start = self.index(f"1.0+{start}c")
            command_end = self.index(f"1.0+{end}c")

            # Taguer la commande elle-même
            command_name_end = self.index(f"{command_start}+{content[start:].find('{')}c")
            self.tag_add("command", command_start, command_name_end)

            # Taguer le contenu à l'intérieur des {}
            param_content = match.group(1)
            param_start = self.index(f"{command_name_end}+1c")  # Après l'accolade ouvrante
            param_end = self.index(f"{command_name_end}+{len(param_content)+1}c")
            self.tag_add("braces", param_start, param_end)

            # Vérifier les nombres dans le paramètre
            for num_match in number_pattern.finditer(param_content):
                num_start = self.index(f"{param_start}+{num_match.start()}c")
                num_end = self.index(f"{param_start}+{num_match.end()}c")
                self.tag_add("number_braces", num_start, num_end)
        # 2. Deuxième passe : détection récursive des commandes avec contenu {}
        for match in brackets_pattern.finditer(content):
            start, end = match.span()
            command_start = self.index(f"1.0+{start}c")
            command_end = self.index(f"1.0+{end}c")

            # Taguer la commande elle-même
            command_name_end = self.index(f"{command_start}+{content[start:].find('[')}c")
            self.tag_add("command", command_start, command_name_end)

            # Taguer le contenu à l'intérieur des {}
            param_content = match.group(1)
            param_start = self.index(f"{command_name_end}+1c")  # Après l'accolade ouvrante
            param_end = self.index(f"{command_name_end}+{len(param_content)+1}c")
            self.tag_add("brackets", param_start, param_end)

            # Vérifier les nombres dans le paramètre
            for num_match in number_pattern.finditer(param_content):
                num_start = self.index(f"{param_start}+{num_match.start()}c")
                num_end = self.index(f"{param_start}+{num_match.end()}c")
                self.tag_add("number_brackets", num_start, num_end)
        # 3. Troisième passe : mode mathématique inline ($...$)
        for match in inline_math_pattern.finditer(content):
            start, end = match.span()
            math_start = self.index(f"1.0+{start}c")
            math_end = self.index(f"1.0+{end}c")
            self.tag_add("math", math_start, math_end)

            # Vérifier les nombres dans le mode math
            math_content = match.group(1)
            for num_match in number_pattern.finditer(math_content):
                num_start = self.index(f"{math_start}+{1+num_match.start()}c")
                num_end = self.index(f"{math_start}+{1+num_match.end()}c")
                self.tag_add("Token.Number", num_start, num_end)

        # Appliquer les styles des tags
        self.color_manager.apply_tag_colors()

    def insert(self, index, chars, *args):
        super().insert(index, chars, *args)
        self.highlight_syntax()
        return 
    def insert_without_highlight(self, index, chars, *args):
        return super().insert(index, chars, *args)
         
    def abstract(self):
        content = self.get("1.0", tk.END)
        abstractor = [] #ExoAbstractor() # suppression utilisation cause import circulaire avec exoabstractor
        todolist = [
            ""#(abstractor.abstract_numbers,content)
        ]
        result = ""#abstractor.abstract_pipe(todolist)
        #result = "\n".join(result)
        #self.delete("1.0", tk.END)
        #self.insert("1.0",result)
        return "\n".join(result)
    
    def auto_compile(self):
        print("Auto-compilation triggered.")
        tex_content = self.get("1.0", tk.END)
        
        with open(self.empty_document,'r',encoding="utf-8")as f:
            model_content=f.read()
        tex_content=model_content.replace("% tex content here",tex_content)
        if self.fancy_page_option:
            tex_content=tex_content.replace("% I want a fancy page",self.fancy_page)
        tex_content=tex_content.replace("% put header here",self.header_content)
        
        with open(self.output_document,'w',encoding="utf-8") as file:
            file.write(tex_content)
        try:
            pdf_path = self.compiler.compile_and_return_pdf_path(self.output_document,output_directory=self.output_directory)
            if pdf_path:
                count=0
                while self.pdf_viewer.display_pdf(pdf_path)==False and count<3:
                    time.sleep(2)
                    count+=1
                print(count)

            else:
                print("Compilation Error", "Erreur lors de la compilation.")
                raise CompilationError(self.compiler.error_code)
        except CompilationError as e:
            print("Compilation Error", str(e))
        except subprocess.CalledProcessError as e:
            print("Compilation Error", f"Erreur lors de la compilation : {e}")



class PdfViewer(ctk.CTkFrame):
    def __init__(self, master = None, **kwargs):
        super().__init__(master, **kwargs)
        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Lier la molette de la souris
        self.canvas.bind("<Double-1>", self.toggle_fullscreen)  # Lier le double-clic

        self.pdf_image = None

    def toggle_fullscreen(self, event=None):
        """A implémenter"""
        print("toggle_fullscreen du pdfviewer déclenché")

    
    def _on_mousewheel(self, event):
        """Fait défiler le canevas lorsque la molette de la souris est utilisée."""
        if self.canvas:
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
    def display_pdf(self, pdf_path):
        is_open=False
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self.pdf_image = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.pdf_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            is_open=True
        except Exception as e:
            print(f"depuis diplay_pdf : Impossible d'ouvrir {pdf_path}")
        finally:
            return is_open

def display_pdf(pdf_path):
    if os.path.exists(pdf_path):
        pdf_viewer.display_pdf(pdf_path)

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x600")

    left_frame = ctk.CTkFrame(root, width=800, height=600)
    left_frame.pack(side="left", fill="both", expand=True)

    right_frame = ctk.CTkFrame(root, width=400, height=600)
    right_frame.pack(side="right", fill="both", expand=True)

    environnement="Environnement de cours"
    content_type="Presentation"
    etab="Collège"
    etab_name="Les Jacobins"
    supplement="%Reste du contenu à afficher au début du document."

    fancy_page_parameters=f"""
    \\chapitre[$\\mathbf{{6^{{\\text{{ème}}}}}}$]{{
    {environnement}%Environnement de cours
    }}{{
    {etab}%Collège
    }}{{
    {etab_name}%Les Jacobins
    }}{{
    {supplement}%Reste du contenu à afficher au début du document.
    }}{{
    {content_type}%Presentation
    }}
    """
    latex_compiler = LaTeXCompiler("document.tex")
    pdf_viewer = PdfViewer(right_frame)
    pdf_viewer.pack(pady=20, padx=10, fill='both', expand=True)


    text_widget = LatexText(left_frame, compiler=latex_compiler, pdf_viewer=pdf_viewer,fancy_page_parameters=fancy_page_parameters, width=80, height=20)
    text_widget.pack(pady=20, padx=20, expand=True, fill='both')

    compile_button = ctk.CTkButton(right_frame, text="Compiler", command=text_widget.auto_compile)
    compile_button.pack(pady=20)

    root.mainloop()