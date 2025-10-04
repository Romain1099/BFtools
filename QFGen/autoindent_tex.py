import re


def clean_and_indent_latex_file(input_file, output_file, indent_size=4):
    """
    Nettoie et indente correctement un fichier LaTeX.

    :param input_file: Chemin du fichier LaTeX d'entrée
    :param output_file: Chemin du fichier LaTeX de sortie
    :param indent_size: Nombre d'espaces par niveau d'indentation (par défaut 4)
    """
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remove existing indentation
    content = re.sub(r'^[ \t]+', '', content, flags=re.MULTILINE)

    # Split content into lines for processing
    lines = content.split('\n')

    indent_level = 0
    indent = ' ' * indent_size
    indented_lines = []
    inside_environment = False
    open_braces = 0
    open_brackets = 0
    pending_indent_increase = False

    for line in lines:
        stripped_line = line.strip()

        # Check for \begin{...} and increase indent level
        if re.match(r'\\begin\{.*\}', stripped_line):
            #print(f"begin_triggered : {stripped_line}")
            indented_lines.append(indent * indent_level + stripped_line)
            indent_level += 1
        # Check for \end{...} and decrease indent level
        elif re.match(r'\\end\{.*\}', stripped_line):
            indent_level -= 1
            indented_lines.append(indent * indent_level + stripped_line)
        # Check for closing braces or brackets on their own line
        elif stripped_line == '}' or stripped_line == ']':
            indent_level -= 1
            indented_lines.append(indent * indent_level + stripped_line)
        else:
            # Update count of open braces and brackets
            opening_braces = stripped_line.count('{')
            closing_braces = stripped_line.count('}')
            opening_brackets = stripped_line.count('[')
            closing_brackets = stripped_line.count(']')

            # Adjust indent level before appending the line if there are unmatched closing braces or brackets
            if closing_braces > opening_braces:
                indent_level -= (closing_braces - opening_braces)
            if closing_brackets > opening_brackets:
                indent_level -= (closing_brackets - opening_brackets)

            indented_lines.append(indent * indent_level + stripped_line)

            # Adjust indent level after appending the line if there are unmatched opening braces or brackets
            if opening_braces > closing_braces:
                indent_level += (opening_braces - closing_braces)
            if opening_brackets > closing_brackets:
                indent_level += (opening_brackets - closing_brackets)

    # Join the indented lines
    #formatted_content = '\n'.join(indented_lines)

    # Join the lines back into a single string
    indented_content = '\n'.join(indented_lines)

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(indented_content)

def clean_and_indent_latex_text(input_tex, indent_size=4):
    """
    Nettoie et indente correctement un fichier LaTeX.
    """
    # Remove existing indentation
    content = re.sub(r'^[ \t]+', '', input_tex, flags=re.MULTILINE)

    # Split content into lines for processing
    lines = content.split('\n')

    indent_level = 0
    indent = ' ' * indent_size
    indented_lines = []
    inside_environment = False
    open_braces = 0
    open_brackets = 0
    pending_indent_increase = False
    already_section = False #indicateur du niveau d'indentation par section
    already_subsection = False
    already_subsubsection = False
    for line in lines:
        stripped_line = line.strip()

        '''# Check for \begin{...} and increase indent level
        if re.match(r'\\begin\{.*\}', stripped_line):
            indented_lines.append(indent * indent_level + stripped_line)
            indent_level += 1
        # Check for \end{...} and decrease indent level
        elif re.match(r'\\end\{.*\}', stripped_line):
            if re.match(r'\\end\{document\}', stripped_line):
                indent_level = 0
            else:
                indent_level -= 1
            indented_lines.append(indent * indent_level + stripped_line)'''
        # Vérifier si un environnement commence sur cette ligne
        begin_match = re.search(r'\\begin\{([a-zA-Z]+)\}', stripped_line)
        end_match = re.search(r'\\end\{([a-zA-Z]+)\}', stripped_line)

        if begin_match and not end_match:
            # L'environnement commence mais ne se termine pas sur cette ligne
            indented_lines.append(indent * indent_level + stripped_line)
            indent_level += 1

        elif end_match and not begin_match:
            # L'environnement se termine mais ne commence pas sur cette ligne
            if re.search(r'\\end\{document\}', stripped_line):
                indent_level = 0
            else:
                indent_level -= 1
            indented_lines.append(indent * indent_level + stripped_line)

        elif begin_match and end_match:
            # Les deux \begin et \end sont sur la même ligne
            indented_lines.append(indent * indent_level + stripped_line)
        # Check for closing braces or brackets on their own line
        elif stripped_line == '}' or stripped_line == ']':
            indent_level -= 1
            indented_lines.append(indent * indent_level + stripped_line)
        elif stripped_line.startswith(r'\section'):
            if already_section:
                indent_level-=1
                if already_subsubsection:
                    indent_level -= 1
                    already_subsubsection = False
                if already_subsection:
                    indent_level-=1
                    already_subsection = False
                indented_lines.append(indent * indent_level + stripped_line)
                indent_level += 1
            else:
                indented_lines.append(indent * indent_level + stripped_line)
                indent_level += 1
                already_section = True
        elif stripped_line.startswith(r'\subsection'):
            if already_subsection:
                indent_level-=1
                if already_subsubsection:
                    indent_level -= 1
                    already_subsubsection = False
                indented_lines.append(indent * indent_level + stripped_line)
                indent_level += 1
            else:
                indented_lines.append(indent * indent_level + stripped_line)
                indent_level += 1
                already_subsection = True
        elif stripped_line.startswith(r'\subsubsection'):
            if already_subsubsection:
                indent_level-=1
                indented_lines.append(indent * indent_level + stripped_line)
                indent_level += 1
            else:
                indented_lines.append(indent * indent_level + stripped_line)
                indent_level += 1
                already_subsubsection = True
        else:
            # Update count of open braces and brackets
            opening_braces = stripped_line.count('{')
            closing_braces = stripped_line.count('}')
            opening_brackets = stripped_line.count('[')
            closing_brackets = stripped_line.count(']')

            # Adjust indent level before appending the line if there are unmatched closing braces or brackets
            
            

            # Adjust indent level after appending the line if there are unmatched opening braces or brackets
            if opening_braces > closing_braces:
                indented_lines.append(indent * indent_level + stripped_line)
                indent_level += (opening_braces - closing_braces)
            elif closing_braces > opening_braces:
                if stripped_line[-1] == "}":
                    #print("triggered")
                    content_before_closing_brace = stripped_line[:-1]
                    if content_before_closing_brace.strip():
                        # Ajouter la ligne avant l'accolade fermante
                        indented_lines.append(indent * indent_level + content_before_closing_brace)
                        # Ajouter l'accolade fermante sur une nouvelle ligne
                        indent_level -= 1
                        indented_lines.append(indent * (indent_level) + "}")
                    else:
                        indented_lines.append(indent * indent_level + stripped_line)
                indent_level -= (closing_braces - opening_braces -1)
                
            if opening_brackets > closing_brackets:
                indented_lines.append(indent * indent_level + stripped_line)
                indent_level += (opening_brackets - closing_brackets)
            elif closing_brackets > opening_brackets:
                if stripped_line[-1] == "]":
                    content_before_closing_brace = stripped_line[:-1]
                    if content_before_closing_brace.strip():
                        # Ajouter la ligne avant l'accolade fermante
                        indented_lines.append(indent * indent_level + content_before_closing_brace)
                        # Ajouter l'accolade fermante sur une nouvelle ligne
                        indent_level -= 1
                        indented_lines.append(indent * (indent_level) + "]")
                    else:
                        indented_lines.append(indent * indent_level + stripped_line)
                indent_level -= (closing_brackets - opening_brackets - 1)

            if opening_braces == closing_braces and closing_brackets == opening_brackets:
                indented_lines.append(indent * indent_level + stripped_line)

    # Join the indented lines
    #formatted_content = '\n'.join(indented_lines)

    # Join the lines back into a single string
    indented_content = '\n'.join(indented_lines)

    return indented_content

def use_case_one():
    # Exemple d'utilisation
    input_file = 'input.tex'
    output_file = 'output.tex'
    clean_and_indent_latex_file(input_file, output_file)
def use_case_two():
    # Exemple d'utilisation :
    latex_code = r"""
    \begin{document}
    \section{Introduction}
    % Un commentaire ici
    
    \subsection{un truc}
    Ce document est un test.
    \subsection{test de boite}
    \boite{Titre}{
    un autre texte avec un \textbf{piège}
    du texte}
    et là ?
    \section{liste}
    \begin{itemize}
    \item Élément 1
    \item Élément 2
    \end{itemize}
    \end{document}
    """
    modified_text=clean_and_indent_latex_text(latex_code)
    print(modified_text)

if __name__=="__main__":
    use_case_two()
