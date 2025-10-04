import re
import tkinter as tk
from tkinter import messagebox

class LatexSyntaxError(Exception):
    """Exception levée pour des erreurs syntaxiques LaTeX."""
    pass

def precheck_latex_syntax(latex_code: str) -> None:
    """
    Analyse syntaxique basique du code LaTeX pour détecter des erreurs potentielles.
    Lève une exception en cas de problème.

    Args:
        latex_code (str): Le code LaTeX à vérifier.

    Raises:
        LatexSyntaxError: Si des erreurs sont détectées.
    """
    errors = []

    # Vérifier les environnements \begin{} et \end{}
    begin_end_pattern = r"\\(begin|end)\{([a-zA-Z*]+)\}"
    env_stack = []
    
    for match in re.finditer(begin_end_pattern, latex_code):
        command, env_name = match.groups()
        if command == "begin":
            env_stack.append(env_name)
        elif command == "end":
            if not env_stack or env_stack[-1] != env_name:
                errors.append(f"Environnement non apparié : \\end{{{env_name}}} sans \\begin{{{env_name}}}")
            else:
                env_stack.pop()

    if env_stack:
        errors.extend([f"Environnement non fermé : \\begin{{{env}}}" for env in env_stack])

    # Vérifier les accolades ouvertes/fermées (en ignorant celles précédées d'un \)
    unescaped_open_braces = len(re.findall(r"(?<!\\)\{", latex_code))
    unescaped_close_braces = len(re.findall(r"(?<!\\)\}", latex_code))
    if unescaped_open_braces != unescaped_close_braces:
        errors.append(
            f"Nombre d'accolades déséquilibré : {unescaped_open_braces} ouvertures et {unescaped_close_braces} fermetures."
        )

    # Vérifier les crochets ouverts/fermés
    open_brackets = latex_code.count("[")
    close_brackets = latex_code.count("]")
    if open_brackets != close_brackets:
        errors.append(f"Nombre de crochets déséquilibré : {open_brackets} ouvertures et {close_brackets} fermetures.")

    # Lever une exception si des erreurs sont détectées
    if errors:
        raise LatexSyntaxError("\n".join(errors))




def check_latex_code(latex_code: str) -> bool:
    """
    Vérifie le code LaTeX et affiche une boîte de dialogue en cas d'erreur.

    Args:
        latex_code (str): Le code LaTeX à vérifier.
    """
    is_compilable = False
    try:
        precheck_latex_syntax(latex_code)
        #messagebox.showinfo("Résultat de la vérification", "Aucune erreur détectée. Le code semble valide.")
        is_compilable = True
        print("tout va bien")
        message = ""
    except LatexSyntaxError as e:
        #messagebox.showerror("Erreur LaTeX détectée", f"Erreurs trouvées :\n\n{e}")
        is_compilable = False
        message = f"Erreurs trouvées :\n\n{e}"
        print(message)
    return is_compilable, message


# Exemple d'utilisation avec tkinter
if __name__ == "__main__":
    # Code LaTeX à tester
    code_latex = r"""
\begin{tikzpicture}[]
    \SequenceItem{Introduction ($30$ min)}{%Rappels de calculs littéral :
        \begin{itemize}[label=$\bullet$]
            \item Plan.
            \item Comment fonctionne \LaTeX.
            \item Téléchargement des logiciels \voc{MikTeX} et \voc{VSCode}.
        \end{itemize}
    }{\`A faire : \begin{itemize}[label=$\bullet$]
        \item Se connecter à un point d'accès mobile. 
        \item Télécharger les logiciels
    \end{itemize}
    }
    \SequenceItem[below = 1.7cm of desc1.south west]{Activité}{
        \begin{itemize}[label=$\bullet$,itemsep=0em]
            \item Setup des logiciels.
            \item Point théorique sur la structure d'un document \LaTeX.
            \item Le fameux \frquote{Hello World !}
        \end{itemize}
    }{
        \`A faire : \begin{itemize}[label=$\bullet$]
            \item Télécharger l'extension \voc{LaTeX Workshop} et \voc{PDF Viewer} sur VSCode.
            \item Télécharger le fichier \frquote{setup\_vscode.json}.
            \item Construire son premier document \LaTeX.
        \end{itemize}
    }
    \SequenceItem[below = 1.7cm of desc2.south west]{BFcours}{%Nature d'une égalité
    \begin{itemize}[label=$\bullet$,itemsep=0em]
        \item Une pause s'impose ! 
        \item Point théorique sur le package \voc{BFcours}.
        \item Premier document avec \acc{BFcours}.
    \end{itemize}
    }{
        \`A faire : \begin{itemize}[label=$\bullet$]
            \item Téléchargement du package \acc{BFcours}.
            \item Compiler un premier document avec le package \bfcours.
        \end{itemize}
    }
    \SequenceItem[below = 1.7cm of desc3.south west]{Point théorique}{%Les bouteilles :\\
    \begin{itemize}%[label=$\bullet$,itemsep=0em]
        \item[] \bclampe Formattage du% \textbf{te}\Large{x}\scriptsize{te}.
        \item[$\bullet$] \voc{Commandes} et \voc{Environnements}
        \item[$\bullet$] \voc{CTAN} et \voc{LaTeX Stack Exchange}
    \end{itemize}
    }{
        \`A faire :
        \begin{itemize}[label=$\bullet$,itemsep=0em]
            \item Se familiariser avec les commandes basiques.
            \item Savoir où \voc{se documenter}.
        \end{itemize}
    }
    \SequenceItem[below = 1.7cm of desc4.south west]{Cours\\\large{$+$}\\Atelier }{%Distributivité
    \begin{itemize}[label=$\bullet$,itemsep=0em]
        \item 
    \end{itemize}
    }{
        \`A faire : \begin{itemize}[label=$\bullet$]
            \item 
        \end{itemize}
    }
    \SequenceItem[below = 1.7cm of desc5.south west]{Cours\\\large{$+$}\\Exercices}{%Réduire et factoriser
    \begin{itemize}[label=$\bullet$,itemsep=0em]
        \item 
    \end{itemize}
    }{
        \`A faire : \begin{itemize}[label=$\bullet$]
            \item 
        \end{itemize}
    }
    \SequenceItem{Cours\\\large{$+$}\\\'Eval \no 2}{%Distributivité double %[below = 1.7cm of desc6.south west]
    \begin{itemize}[label=$\bullet$,itemsep=0em]
        \item 
    \end{itemize}
    }{
        \`A faire : \begin{itemize}[label=$\bullet$]
            \item 
        \end{itemize}
    }
\SequenceItem[below = 1.7cm of desc1.south west]{\'Evaluation\\\textbf{ou}\\Exercices}{
    \begin{itemize}[label=$\bullet$,itemsep=0em]
        \item \textbf{\'Evaluation \no 3 :} \\Ensemble du chapitre
    \end{itemize}
    }{
        %Selon l'avancée de la classe, il est possible de rajouter une séance d'exercices.
    }
\end{tikzpicture}

\tableaurecapsequence{
    \recapHeures%

    \enteteContenu%

    \competence{Connaître le vocabulaire lié au calcul littéral}
}
    """

    # Initialiser une fenêtre Tkinter
    root = tk.Tk()
    root.withdraw()  # Masquer la fenêtre principale

    # Lancer la vérification
    check_latex_code(code_latex)
