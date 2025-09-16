from data_manager import load_people_data, generate_people_checkboxes
from html_generator import generate_html_structure, save_html_file

def create_html(data):
    """
    Crée le contenu HTML complet à partir des données.
    
    Args:
        data (list): Liste des données personnes [Nom, Prénom]
        
    Returns:
        str: HTML complet
    """
    people_checkboxes = generate_people_checkboxes(data)
    return generate_html_structure(people_checkboxes)

def main():
    """
    Fonction principale - orchestration de la génération HTML.
    """
    try:
        data = load_people_data('liste.csv')
    except FileNotFoundError as e:
        print(str(e))
        return

    html_output = create_html(data)
    save_html_file(html_output, 'index.html')

if __name__ == "__main__":
    main()