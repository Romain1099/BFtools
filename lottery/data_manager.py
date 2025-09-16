import csv

def load_people_data(filename='liste.csv'):
    """
    Charge les données des personnes depuis un fichier CSV.
    
    Args:
        filename (str): Nom du fichier CSV à charger
        
    Returns:
        list: Liste des lignes du CSV (format: [Nom, Prénom])
        
    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            data = list(reader)
            
        # Filtrer les lignes vides
        data = [row for row in data if row]
        return data
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier {filename} est introuvable.")

def generate_people_checkboxes(data):
    """
    Génère le HTML pour les checkboxes des personnes.
    
    Args:
        data (list): Liste des données personnes [Nom, Prénom]
        
    Returns:
        str: HTML des checkboxes
    """
    checkboxes = ""
    for row in data:
        print(row)
        full_name = f"{row[1]} {row[0]}"
        checkboxes += f'<label class="person-checkbox"><input type="checkbox" value="{full_name}" checked><span>{full_name}</span></label>'
    return checkboxes

def get_people_js_array(data):
    """
    Convertit les données en tableau JavaScript.
    
    Args:
        data (list): Liste des données personnes [Nom, Prénom]
        
    Returns:
        list: Liste des noms complets
    """
    return [f"{row[1]} {row[0]}" for row in data]