
import random
import re
from exo_number import ExoNumber,numberType

from number_generators_manager import NumberGeneratorManager,NumberGeneratorType


def parse_match_conditions(conditions: str):
    """Analyse les conditions entre accolades."""
    parts = conditions.split(" ")  # Diviser par espace
    value_min = float("-100")
    value_max = float("100")
    exclude = []
    number_type = numberType.INT
    #print(parts)
    nombre_decimalesD = 0
    nombre_decimalesG = 0
    for part in parts:
        if "<=" in part or ">=" in part or "<" in part or ">" in part:
            value_min = part.split("x")[0].replace("=","").replace(">","").replace("<","")
            value_max = part.split("x")[1].replace("=","").replace(">","").replace("<","")
            if value_min == "":
                value_min = 0
            if value_max == "":
                value_max = 100
        elif "!=" in part:
            # Gestion des exclusions
            exclude.append(float(part.split("!=")[1]))
        elif part.lower() in ("int", "float", "frac"):
            # Gestion du type
            number_type = getattr(numberType, part.upper(), numberType.INT)
        if "decimalesD" in part:
            nombre_decimalesD=int(part.split("decimalesD")[1].strip())
            #print(f"décimalesD détectées : {nombre_decimalesD}")
        if "decimalesG" in part:
            nombre_decimalesG=int(part.split("decimalesG")[1].strip())
            #print(f"décimalesG détectées : {nombre_decimalesG}")


    return number_type, value_min, value_max, exclude,nombre_decimalesD, nombre_decimalesG

def replace_numbers_placeholders(match):
    """Remplace chaque placeholder par une valeur générée."""
    conditions = match.group(1)
    number_type, value_min, value_max, exclude,nombre_decimalesD, nombre_decimalesG = parse_match_conditions(conditions)
    #print(f"number_type : {number_type}, value_min : {value_min}, value_max : {value_max}, exclude {exclude}")
    exo_number = ExoNumber(number_type=number_type, value_min=value_min, value_max=value_max, exclude=exclude,nombre_decimalesD=nombre_decimalesD,nombre_decimalesG=nombre_decimalesG)
    return f"{{{exo_number}}}"

def replace_list_placeholders(list_match):
    """
    Gère le remplacement pour une liste de mots (e.g., [va, float, vodoo]).
    """
    # Extraction des éléments de la liste
    elements = list_match.group(1).split(",")
    elements = [element.strip() for element in elements]  # Supprime les espaces inutiles

    # Choisir un élément au hasard parmi les options
    chosen_element = random.choice(elements)
    return f"{{{chosen_element}}}"
def find_class_number_to_generate(nums)->list[list[str],str]:
    patterns = [f"{number_class.value.__name__}\\((.*?)\\)" for number_class in NumberGeneratorType]
    print(f"Patterns pour les générateurs : {patterns}")
    elements = []
    for pattern in patterns:
        matches = re.finditer(pattern, nums, re.DOTALL)
        for match in matches:
            # Ajoute tout le bloc correspondant, pas uniquement les groupes
            match_content = match.group(0)
            elements.append(match_content)
            nums = re.sub(re.escape(match_content), "", nums, count=1)  # Supprime la correspondance actuelle

    return [elements,nums]
def create_random_variable(variable_defs:str)->str:
    r"""
    Génère des expressions aléatoires partir d'une expression du type : 

    \def\nb{4<x<12 x!=6 int}
    \def\nd{1<=x<=5 float decimales2}
    \def\frac{1<x<=10 x!=0 frac}
    \def\nb{4<x}
    \def\ndb{12.89<=x<=51.222 float decimalesD7}
    \def\frac{1<x<=10 x!=0 frac}

    renvoie par exemple : 
    \def\nb{4}
    \def\nd{3.675}
    \def\frac{\dfrac{2}{5}}
    \def\nb{20}
    \def\nd{43.3220896}
    \def\frac{\dfrac{3}{5}}
    """
    # Remplacement de chaque placeholder
    number_generator=NumberGeneratorManager()
    numbers_found,nums = find_class_number_to_generate(variable_defs)
    #print(f"numbers_found : {numbers_found}")
    generated=[number_generator.generate_number(n).to_latex() for n in numbers_found]
    #print(f"generated : {generated}")
    nums = re.sub(r"\{([^{}]+)\}", replace_numbers_placeholders, nums)
    nums = re.sub(r"\[([^\]]+)\]", replace_list_placeholders, nums)
    nums = nums + '\n'.join(generated)
    return nums

if __name__ == "__main__":
    nums = r"""
    \def\nb{4<x<12 x!=6 int}
    \def\nbb{4<x<10000 x!=6 int decimalesG3}
    \def\nd{1<=x<=5 float decimalesD2}
    \def\frac{1<x<=10 x!=0 frac}
    ArithmeticNumber(
        allowed_generators=[2, 3, 5, 7, 11, 13, 17, 19],
        prime_length=[2, 4],
        inf=1,
        sup=1000,
        name="mbba"
    )
    \def\nb{4<x}
    \def\nd{12.89<=x<=251.222 float decimalesD7 decimalesG3}
    \def\frac{1<x<=10 x!=0 frac}
    \def\list[va,vodoo,jimi,Daevid Allen]
    """
    print(create_random_variable(nums))
    #TODO : Ajouter la possibilité d'inclure du code python qui prendra effet sur l'une ou plusieurs parties du document. 
    #TODO : Ajouter la connaissance des noms de variables de sorte à pouvoir donner des instructions du type : x!=\nb 
    # si par exemple on a déjà défini \nb le programme devra reconnnaitre qu'on cherche à générer un nombre différent 
    # de celui déjà obtenu pour la variable \nb.
    #TODO : Ajouter la gestion des phrases pour les listes ( si c'est pas déjà le cas avec notre syntaxe.)
    
