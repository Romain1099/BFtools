import tkinter as tk
import customtkinter as ctk

import string
import sys
import os
import re
# Ajouter dynamiquement le chemin vers la racine
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../.."))
print(project_root)
if project_root not in sys.path:
    sys.path.append(project_root)

# Importer le widget LatexText
from QF_generator.latexhighlighter.tex_highlighter import LatexText
from QF_generator.latexhighlighter.color_manager import ColorManager
import asyncio
import tracemalloc
tracemalloc.start()

class CTkMessageBox(ctk.CTkToplevel):
    def __init__(self, title, message):
        super().__init__()
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)

        # Message Label
        self.label = ctk.CTkLabel(self, text=message, wraplength=350)
        self.label.pack(pady=20, padx=20)

        # OK Button
        self.ok_button = ctk.CTkButton(self, text="OK", command=self.close)
        self.ok_button.pack(pady=10)

    def close(self):
        self.destroy()


class AbstractExoUI(ctk.CTkToplevel):
        def __init__(self, parent, callback, abstract_function):
            super().__init__(parent)
            self.callback = callback
            self.abstract_function = abstract_function

            self.title("Abstraction de contenu LaTeX")
            self.geometry("600x400")

            # Champ texte pour coller le code LaTeX
            self.latex_text = LatexText(self, wrap="word", width=80, height=20)
            self.latex_text.pack(fill="both", expand=True, padx=10, pady=10)

            # Bouton "Abstraire"
            self.abstract_button = ctk.CTkButton(
                self, text="Abstraire", command=self.abstract_content
            )
            self.abstract_button.pack(pady=10)

        def abstract_content(self):
            """Appelle la fonction d'abstraction et transmet le résultat via le callback."""
            content = self.latex_text.get("1.0", "end").strip()
            if not content:
                CTkMessageBox(
                    title="Erreur", message="Veuillez entrer du contenu LaTeX."
                )
                return

            # Appelle la fonction abstraite asynchrone
            self.abstract_button.configure(state="disabled", text="En cours...")
            asyncio.run(self.run_abstract_function(content))

        async def run_abstract_function(self, content):
            try:
                # Appel de la fonction d'abstraction IA
                result = await self.abstract_function(content)
                self.callback(text=result,widget=self)
                CTkMessageBox(
                    title="Succès", message="Abstraction réussie."
                )
            except Exception as e:
                CTkMessageBox(
                    title="Erreur", message=f"Une erreur est survenue : {str(e)}"
                )
                self.abstract_button.configure(state="normal", text="Abstraire")