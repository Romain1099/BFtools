from numbers_def import create_random_variable
from enum import Enum,StrEnum
import random
import json
from pathlib import Path
from tkinter.filedialog import askopenfilename
class QuestionType(StrEnum):
    SHORT = "short"
    HELP = "help"
    FULL = "full"
    QCM = "qcm"


def create_questions(text:str)->dict:
    """
    Renvoie un dictionnaire contenant les listes des questions dans leurs versions.
        "short":questions_short,
        "help": réponses à compléter dans le document,
        "full": réponses à écrire,
        "qcm": réponses en qcm,
        "answer": réponse courte attendue,
        "theme": thème de la question,
        "answer_long": réponse détaillée simple
    """

    number_questions,variable_defs,short,help,qcm,answer,theme,*html = text.split(r"%%")
    questions_short = []
    questions_help = []
    questions_full= []
    questions_qcm = []
    questions_html = []
    #questions_answer = []
    answer_simple = []
    answer_long = []
    question_theme = theme
    for index in range(1,int(number_questions.strip())+1):
        variables = create_random_variable(variable_defs=variable_defs)
        questions_short.append(f"%version {index} - Court\n\t{variables}\n\t{short}")
        questions_help.append(f"%version {index} - A compléter\n\t{variables}\n\t{short}\n\t{help}")
        answer_long.append(f"%version {index} - solutions\n\t{variables}\n\t{help}")
        questions_full.append(f"%version {index} - A écrire\n\t{variables}\n\t{short}\n\t\\begin{{crep}}{help}\\end{{crep}}")
        questions_qcm.append(f"%version {index} - QCM\n\t{variables}\n\t{qcm}")
        questions_html.append(html)
        answer_simple.append(f"{variables}{answer}".replace('\n', '').strip())
    questions = []
    questions.extend(questions_short)
    questions.extend(questions_help)
    questions.extend(questions_full)
    questions.extend(questions_qcm)
    questions.extend(questions_html)
    return {
        "short":questions_short,
        "help":questions_help,
        "full":questions_full,
        "qcm":questions_qcm,
        "answer":answer_simple,
        "theme":question_theme,
        "answer_long":answer_long,
        "html" :questions_html
    }


chapitre_want = True
def get_questions_text(question_dict:dict,specs:list[QuestionType],chapitre=None)-> str:
    global chapitre_want
    """
    Renvoie le contenu TeX des questions respectant les particularités donnés dans specs
    """
    output=[]
    for index,_ in enumerate(question_dict["short"]):
        if not chapitre:
            chapitre = r"""
\newpage
\chapitre[
    $\mathbf{6^{\text{ème}}}$% : $\mathbf{6^{\text{ème}}}$,$\mathbf{5^{\text{ème}}}$,$\mathbf{4^{\text{ème}}}$,$\mathbf{3^{\text{ème}}}$,$\mathbf{2^{\text{nde}}}$,$\mathbf{1^{\text{ère}}}$,$\mathbf{T^{\text{Le}}}$,
    ]{
    Exercice aléatoire% : ,
    }{
    Collège% : Collège,Lycée
    }{
    %Amadis Jamyn% : Amadis Jamyn,Eugène Belgrand
    }{
    % : ,\tableauPresenteEvalSixieme{}{10},\tableofcontents
    }{
    Version %%%%%%% % : ,
    }
"""
        if chapitre_want:
            output.append(f"{chapitre.replace(r'%%%%%%%',str(index+1))}\n%{specs[index]}\n {question_dict[specs[index]][index]}")
        else:
            output.append(f"%{specs[index]}\n {question_dict[specs[index]][index]}")
    return '\n'.join(output)
def make_json_versions_from_tex(question_dict):
    output=[]
    for index,_ in enumerate(question_dict["help"]):
        output.append({
        "enonce": question_dict["short"][index],
        "reponse": question_dict["answer"][index],
        "details": question_dict["answer_long"][index],
        "theme": question_dict["theme"],
        "prompt": "Depuis la bibliothèque aléatoire"
        })
    return output

import random
from pathlib import Path
from tkinter.filedialog import askopenfilename

def make_versions_file_from_tex(input_filepath=None, specs=None) -> str:
    """
    Génère des versions de questions à partir d'un fichier LaTeX fourni par l'utilisateur et selon des spécifications données.

    Parameters:
        input_filepath (str, optional): Chemin du fichier d'entrée. Si non fourni, une fenêtre de sélection de fichier s'ouvre.
        specs (list of str, optional): Liste des spécifications pour les versions de questions. 
                                       Exemples : ["short", "help", "full", "qcm"].

    Returns:
        str: Chemin du fichier de sortie contenant les versions générées ou un message d'erreur.
    """
    try:
        # Si le chemin du fichier n'est pas fourni, ouvrir une boîte de dialogue pour le sélectionner.
        if not input_filepath:
            input_filepath = askopenfilename(initialdir=Path(__file__).parent / 'inputs', 
                                             filetypes=[("Fichiers LaTeX", "*.tex"),("Fichiers LaTeX", "*.cls"),("Fichiers LaTeX", "*.sty"), ("Tous les fichiers", "*.*")])

        if not input_filepath:
            return "Aucun fichier sélectionné. Veuillez sélectionner un fichier pour générer les versions."
        name_of_input_file = input_filepath.split('/')[-1:][0]
        input_filepath = Path(input_filepath)
        if not input_filepath.exists():
            return f"Le fichier spécifié n'existe pas : {input_filepath}"

        # Lecture du contenu du fichier LaTeX
        with open(input_filepath, 'r', encoding='utf-8') as file:
            text = file.read()

        # Création des questions à partir du texte
        question_dict = create_questions(text)
        number_questions = len(question_dict.get("short", []))

        if number_questions == 0:
            return "Aucune question détectée dans le fichier LaTeX fourni."

        # Si les specs ne sont pas fournies, les générer aléatoirement
        if not specs:
            specs = [random.choice(["short", "help", "full", "qcm"]) for _ in range(number_questions)]
        elif len(specs) != number_questions:
            return f"Le nombre de spécifications ({len(specs)}) ne correspond pas au nombre de questions détectées ({number_questions})."

        # Génération des questions avec les spécifications
        output = get_questions_text(question_dict=question_dict, specs=specs)

        # Création du chemin de sortie
        output_dir = Path(__file__).parent / "productions"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"output_{name_of_input_file.replace('.cls','').replace('.sty','').replace('.tex','')}.tex"

        # Écriture des versions dans le fichier de sortie
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(output)

        print(f"{len(specs)} versions générées et enregistrées dans le fichier : {output_path}")
        return str(output_path)

    except Exception as e:
        return f"Une erreur s'est produite : {str(e)}"

def make_json(input_filepath=None, specs=None) -> str:
    """
    Génère des versions de questions à partir d'un fichier LaTeX fourni par l'utilisateur et selon des spécifications données.

    Parameters:
        input_filepath (str, optional): Chemin du fichier d'entrée. Si non fourni, une fenêtre de sélection de fichier s'ouvre.
        specs (list of str, optional): Liste des spécifications pour les versions de questions. 
                                       Exemples : ["short", "help", "full", "qcm"].

    Returns:
        str: Chemin du fichier json de sortie contenant les versions générées ou un message d'erreur.
    """
    try:
        # Si le chemin du fichier n'est pas fourni, ouvrir une boîte de dialogue pour le sélectionner.
        if not input_filepath:
            input_filepath = askopenfilename(initialdir=Path(__file__).parent / 'inputs', 
                                             filetypes=[("Fichiers LaTeX", "*.tex"),("Fichiers LaTeX", "*.cls"),("Fichiers LaTeX", "*.sty"), ("Tous les fichiers", "*.*")])

        if not input_filepath:
            return "Aucun fichier sélectionné. Veuillez sélectionner un fichier pour générer les versions."
        name_of_input_file = input_filepath.split('/')[-1:][0]
        input_filepath = Path(input_filepath)
        if not input_filepath.exists():
            return f"Le fichier spécifié n'existe pas : {input_filepath}"

        # Lecture du contenu du fichier LaTeX
        with open(input_filepath, 'r', encoding='utf-8') as file:
            text = file.read()

        # Création des questions à partir du texte
        question_dict = create_questions(text)
        number_questions = len(question_dict.get("short", []))

        if number_questions == 0:
            return "Aucune question détectée dans le fichier LaTeX fourni."

        # Si les specs ne sont pas fournies, les générer aléatoirement
        if not specs:
            specs = [random.choice(["short", "help", "full", "qcm"]) for _ in range(number_questions)]
        elif len(specs) != number_questions:
            return f"Le nombre de spécifications ({len(specs)}) ne correspond pas au nombre de questions détectées ({number_questions})."
        # Création du chemin de sortie
        output_dir = Path(__file__).parent / "json_productions"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{name_of_input_file.replace('.cls','').replace('.sty','').replace('.tex','')}.json"

        return_dict = make_json_versions_from_tex(question_dict)
        # Écriture des versions dans le fichier de sortie au format JSON
        with open(output_path, 'w', encoding='utf-8') as file:
            # Utilisation de json.dump pour écrire la liste de dictionnaires dans le fichier
            json.dump(return_dict, file, ensure_ascii=False, indent=4)

        print(f"{len(return_dict)} versions générées et enregistrées dans le fichier : {output_path}")
        return str(output_path)

    except Exception as e:
        return f"Une erreur s'est produite dans make_json : {str(e)}"
    
def make_json_UI(input_filepath,output_filepath,specs):
    try:
        # Si le chemin du fichier n'est pas fourni, ouvrir une boîte de dialogue pour le sélectionner.
        if not input_filepath:
            input_filepath = askopenfilename(initialdir=Path(__file__).parent / 'inputs', 
                                             filetypes=[("Fichiers LaTeX", "*.tex"),("Fichiers LaTeX", "*.cls"),("Fichiers LaTeX", "*.sty"), ("Tous les fichiers", "*.*")])

        if not input_filepath:
            return "Aucun fichier sélectionné. Veuillez sélectionner un fichier pour générer les versions."
        # Lecture du contenu du fichier LaTeX
        with open(input_filepath, 'r', encoding='utf-8') as file:
            text = file.read()

        # Création des questions à partir du texte
        question_dict = create_questions(text)
        number_questions = len(question_dict.get("short", []))

        if number_questions == 0:
            return "Aucune question détectée dans le fichier LaTeX fourni."
        return_dict = make_json_versions_from_tex(question_dict)
        # Si les specs ne sont pas fournies, les générer aléatoirement
        if not specs:
            specs = [random.choice(["short", "help", "full", "qcm"]) for _ in range(number_questions)]
        elif len(specs) != number_questions:
            return f"Le nombre de spécifications ({len(specs)}) ne correspond pas au nombre de questions détectées ({number_questions})."
        

        print(f"{len(return_dict)} versions générées et enregistrées dans le fichier : {output_filepath}")
        return return_dict
    except Exception as e:
        return f"Une erreur s'est produite dans make_json_UI : {str(e)}"
def spec_for_QF(num_versions:int=30):
    return ["help" for _ in range(0,num_versions)]

def test_functionnalities():
    tests = []
    question_dict = create_questions(text)

if __name__ == "__main__":
    text = r"""
    25
    %%
    \def\n{2<=x<20 int}
    \def\d{2<=x<20 int}
    \def\nb{2<=x<20 int}
    \def\db{2<=x<20 int}
    %%
    %court
    Effectuer le calcul suivant : $\dfrac{\n}{\d} + \dfrac{\nb}{\db}$
    %%
    %help

    % Définitions des macros
    \def\decnum{\Decomposition[Longue]{\fpeval{\n * \db + \nb * \d}}}
    \def\decden{\Decomposition[Longue]{\fpeval{\d * \db}}}

    \begin{align*}
        \dfrac{\n}{\d} + \dfrac{\nb}{\db} 
        &=~ \repsim[4cm]{\dfrac{\n \times \db}{\d \times \db}} 
        + \repsim[4cm]{\dfrac{\nb \times \d}{\db \times \d}}\\
        &=~ \repsim[8.1cm]{\dfrac{\fpeval{\n * \db + \nb * \d}}{\fpeval{\d * \db}}}\\
        &=~ \repsim[8.1cm]{\dfrac{\decnum}{\decden}}\\
        &=~ \repsim[8.1cm]{\Simplification{\fpeval{\n * \db + \nb * \d}}{\fpeval{\d * \db}}}.
    \end{align*}
    %%
    %qcm
    \def\nresa{\fpeval{\n + \nb}}
    \def\nresb{\fpeval{\n * \db + \nb * \d}}
    \def\nresc{\fpeval{\n + \nb * \d / \db}}
    \def\nresd{\fpeval{\n * \db + \nb * \d}}
    \def\dresa{\fpeval{\d + \db}}
    \def\dresb{\fpeval{\d * \db}}
    \def\dresc{\fpeval{\d}}
    \def\dresd{\fpeval{\d + \db}}
    \textbf{Cocher} la ou les réponses correctes : \\
    $\dfrac{\n}{\d} + \dfrac{\nb}{\db} = ... $\\
    \begin{center} 
        \listnode{\cb}{$\dfrac{\nresa}{\dresa}$} 
        \listnode{\ccb}{$\dfrac{\nresb}{\dresb}$} 
        \listnode{\ccb}{$\Simplification{\nresb}{\dresb}$} 
        \listnode{\cb}{$\Simplification{\nresd}{\dresd}$} 
    \end{center}
    """

    questions_spec = spec_for_QF()
    chapitre_want = False

    #usecase 1 
    #output = get_questions_text(question_dict=question_dict,specs=questions_spec)

    #usecase 2
    #output_path = make_versions_file_from_tex(specs=questions_spec)#input_filepath="implementer_enonce/inputs/test.tex")

    #usecase 3
    output_path = make_json(specs=questions_spec)
    
