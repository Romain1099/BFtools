import os
import json
import random
from datetime import datetime

def parse_date_from_key(key):
    """
    Extrait une date d'une clé au format QF_jj_mm_aaaa.
    Retourne un objet datetime ou None si le format est incorrect.
    """
    try:
        _, day, month, year = key.split("_")
        return datetime(int(year), int(month), int(day))
    except ValueError:
        return None

def load_json_files_in_date_range(folder, classe, date_min, date_max):
    """
    Charge les fichiers JSON dans une plage de dates spécifiée.
    """
    matching_files = []
    
    # Conversion des dates en objets datetime pour comparaison
    date_min = datetime.strptime(date_min, "%d_%m_%Y")
    date_max = datetime.strptime(date_max, "%d_%m_%Y")

    class_folder = os.path.join(folder, f"database_{classe}")
    print(class_folder)
    if not os.path.exists(class_folder):
        print(f"Le dossier {class_folder} n'existe pas.")
        return []

    for file in os.listdir(class_folder):
        if file.endswith(".json"):
            # Analyse du nom de fichier pour extraire l'année et éventuellement le mois
            parts = file.replace("database_", "").replace(".json", "").split("_")

            try:
                if len(parts) == 1:
                    # Fichier couvrant toute l'année
                    year = int(parts[0])
                    if date_min.year <= year <= date_max.year:
                        matching_files.append(os.path.join(class_folder, file))
                elif len(parts) == 2:
                    year = int(parts[0])
                    month = int(parts[1])  # Peut être écrit sous forme 1 ou 01
                    file_date = datetime(year, month, 1)
                    # Vérifie si la date du fichier est dans la plage spécifiée
                    if date_min <= file_date <= date_max:
                        matching_files.append(os.path.join(class_folder, file))
            except ValueError:
                print(f"Erreur de format dans le nom du fichier : {file}")

    return matching_files

def extract_questions_by_date(json_files, date_min, date_max, number_question):
    """
    Extrait les questions ayant une clé QF_jj_mm_aaaa avec une date comprise dans la plage donnée.
    """
    date_min = datetime.strptime(date_min, "%d_%m_%Y")
    date_max = datetime.strptime(date_max, "%d_%m_%Y")
    selected_questions = []

    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for key, value in data.items():
                if key.startswith("QF_"):
                    question_date = parse_date_from_key(key)
                    if question_date and date_min <= question_date <= date_max:
                        score=0
                        for i in range(1,3):
                            for v in ['enonce','reponse','details','theme']:
                                if value['questions'][f'question{i}'][v].strip() != "":
                                    score+=1
                                else: 
                                    print(f"valeur incorrecte ( vide ? ) pour {v}: {value['questions'][f'question{i}'][v].strip()}")
                        print(f" score : {score}")
                        if score >= 8:
                            selected_questions.append(value)
        except Exception as e:
            print(f"Erreur lors du traitement du fichier {file} : {e}")

    # Sélection aléatoire des questions
    if number_question > len(selected_questions):
        number_question = len(selected_questions)

    return random.sample(selected_questions, number_question)