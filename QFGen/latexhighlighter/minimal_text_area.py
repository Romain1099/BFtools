import tkinter as tk
import customtkinter as ctk
from pygments.lexers import get_lexer_by_name
from pygments.token import Token
from tkinter.scrolledtext import ScrolledText


import re




class MinimalLaTeXtext(ScrolledText):
    def __init__(self,parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind("<KeyRelease>", self.on_key_release)
        self.bind("<Return>", self.on_return_key)
        self.bind("<Tab>", self.on_tab_key)
        self.configure(
            font=("Fira Code", 12), 
            undo=True, 
            wrap='word',
            background='#2e2e2e',  # Couleur de fond gris sombre
            foreground='#ffffff',  # Couleur du texte blanc
            insertbackground='white',  # Couleur du curseur blanc
            selectbackground='#4a4a4a',  # Couleur de sélection gris foncé
            selectforeground='#ffffff'  # Couleur du texte sélectionné blanc
        )
        self.setup_tags()
        self.open_environments = []
        self.open_commands = []  # Liste des commandes non fermées
        self.placeholders = []
        self.already_inserted_dictionnary={}
        self.inactivity_delay = 10000  # 10 seconds
        self.inactivity_callback = None
        
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
        tag_configurations = {
            str(Token.Keyword): {"foreground": coloration_dictionnary["Blue pastel"], "font": ("Fira Code", 12, "bold")},  # Blue pastel
            str(Token.Name): {"foreground": coloration_dictionnary["Red pastel"], "font": ("Fira Code", 12, "bold")},  # Red pastel
            str(Token.String): {"foreground": coloration_dictionnary["Green pastel"], "font": ("Fira Code", 12, "bold")},  # Green pastel
            str(Token.Comment): {"foreground": coloration_dictionnary["Grey pastel"], "font": ("Fira Code", 12, "italic")},  # Grey pastel
            str(Token.Number): {"foreground": coloration_dictionnary["Orange pastel"], "font": ("Fira Code", 12, "bold")},  # Orange pastel
            "math": {"foreground": coloration_dictionnary["Purple pastel"], "font": ("Fira Code", 12, "bold")},  # Purple pastel
            "placeholder": {"foreground": coloration_dictionnary["Dark grey pastel"], "font": ("Fira Code", 12, "italic")},  # Dark grey pastel
            "text_command": {"foreground": coloration_dictionnary["Cyan pastel"], "font": ("Fira Code", 12, "bold")},  # Cyan pastel
            "textbf_command": {"foreground": coloration_dictionnary["Cyan pastel"], "font": ("Fira Code", 12, "bold")},  # Cyan pastel
            "unclosed_env": {"background":coloration_dictionnary["Red light"], "font": ("Fira Code", 12, "bold")},# Red light
        }
        # Configuration des tags
        for tag, config in tag_configurations.items():
            self.tag_configure(tag, **config)

    def on_key_release(self, event=None):
        self.highlight_syntax()
        #self.check_unclosed_environments()
        #self.print_unclosed_environments()
        if self.inactivity_callback:
            self.after_cancel(self.inactivity_callback)
        #self.inactivity_callback = self.after(self.inactivity_delay, self.auto_compile)

    def on_return_key(self, event=None):
        current_line = self.get("insert linestart", "insert")
        indent_level = len(current_line) - len(current_line.lstrip(' '))
        self.insert("insert", "\n" + ' ' * indent_level) #"\n" + 
        self.check_unclosed_environments()
        #self.print_unclosed_environments()
        self.check_unclosed_commands()
        #self.print_unclosed_commands()
        '''new_line=self.get("insert linestart", "insert")
        if new_line==current_line:
            self.insert("insert", "\n")# + ' ' * indent_level)'''
        return "break"

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

    def highlight_syntax(self):
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