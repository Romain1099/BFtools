import re

class LatexSyntaxError(Exception):
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
    lines = latex_code.splitlines()

    # Vérification des environnements \begin{} et \end{}
    begin_end_pattern = r"\\(begin|end)\{([a-zA-Z*]+)\}"
    env_stack = []

    for match in re.finditer(begin_end_pattern, latex_code):
        command, env_name = match.groups()
        line_number = latex_code[:match.start()].count('\n') + 1
        context = lines[line_number - 1].strip()

        if command == "begin":
            env_stack.append((env_name, line_number, context))
        elif command == "end":
            if not env_stack or env_stack[-1][0] != env_name:
                errors.append(
                    f"Environnement non apparié : \\end{{{env_name}}} trouvé à la ligne {line_number} ({context})."
                )
            else:
                env_stack.pop()

    if env_stack:
        errors.extend(
            [f"Environnement non fermé : \\begin{{{env}}} à la ligne {line} ({context})."
             for env, line, context in env_stack]
        )

    # Vérification des accolades ouvertes/fermées
    brace_stack = []
    for i, line in enumerate(lines, start=1):
        for match in re.finditer(r"(?<!\\)[{}]", line):
            char = match.group()
            pos = match.start()
            if char == '{':
                brace_stack.append((i, pos, line.strip()))
            elif char == '}':
                if not brace_stack:
                    errors.append(f"Accolade fermante '}}' non appariée à la ligne {i}, position {pos} ({line.strip()}).")
                else:
                    brace_stack.pop()

    if brace_stack:
        last_line, last_pos, context = brace_stack[-1]
        errors.append(
            f"Accolade ouvrante '{{' non fermée détectée à la ligne {last_line}, position {last_pos} ({context})."
        )

    # Vérification des crochets ouverts/fermés
    bracket_stack = []
    for i, line in enumerate(lines, start=1):
        for match in re.finditer(r"[\[\]]", line):
            char = match.group()
            pos = match.start()
            if char == '[':
                bracket_stack.append((i, pos, line.strip()))
            elif char == ']':
                if not bracket_stack:
                    errors.append(f"Crochet fermant ']' non apparié à la ligne {i}, position {pos} ({line.strip()}).")
                else:
                    bracket_stack.pop()

    if bracket_stack:
        last_line, last_pos, context = bracket_stack[-1]
        errors.append(
            f"Crochet ouvrant '[' non fermé détecté à la ligne {last_line}, position {last_pos} ({context})."
        )

    # Lever une exception si des erreurs sont détectées
    if errors:
        raise LatexSyntaxError("\n".join(errors))


def check_latex_code(latex_code: str) -> bool:
    """
    Vérifie le code LaTeX et affiche les erreurs en cas de problème.

    Args:
        latex_code (str): Le code LaTeX à vérifier.

    Returns:
        tuple: (bool, str) - True si le code est valide, sinon False avec un message d'erreur.
    """
    is_compilable = False
    try:
        precheck_latex_syntax(latex_code)
        print("Tout va bien")
        is_compilable = True
        message = "Aucune erreur détectée."
    except LatexSyntaxError as e:
        is_compilable = False
        message = f"Erreurs trouvées :\n\n{e}"
        print(message)
    return is_compilable, message

if __name__=='__main__':
    # Exemple d'utilisation
    latex_code_example = r"""
            \ifthenelse{\equal{\calculation}{\rounded}}
            {Nouveau Prix $= \num{\rounded}$\\ } % Si égaux
            {Nouveau Prix $= \num{\calculation} \approx \num{\rounded}$\\On donne l'arrondi au \textbf{centième} près car il s'agit d'un prix en euros.} 
    """
    check_latex_code(latex_code_example)
