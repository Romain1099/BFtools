"""
Gestionnaire CSV avec support multi-sessions et multi-classes
"""

import os
import csv
import shutil
from datetime import datetime
from typing import List, Dict, Optional

class CSVManager:
    """Gère les fichiers CSV des classes avec historique des sessions"""

    def __init__(self, data_directory: str):
        """
        Initialise le gestionnaire CSV

        Args:
            data_directory: Chemin vers le dossier contenant les fichiers CSV
        """
        self.data_dir = data_directory
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Créer un dossier de backup
        self.backup_dir = os.path.join(self.data_dir, 'backups')
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def list_classes(self) -> List[str]:
        """
        Retourne la liste des classes disponibles (fichiers CSV)

        Returns:
            Liste des noms de classes (sans l'extension .csv)
        """
        classes = []
        for file in os.listdir(self.data_dir):
            if file.endswith('.csv') and not file.startswith('.'):
                classes.append(file[:-4])  # Enlever .csv
        return sorted(classes)

    def load_class(self, class_name: str) -> List[Dict]:
        """
        Charge les données d'une classe depuis son fichier CSV

        Args:
            class_name: Nom de la classe (sans .csv)

        Returns:
            Liste de dictionnaires représentant les étudiants et leurs scores
        """
        file_path = os.path.join(self.data_dir, f"{class_name}.csv")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Classe '{class_name}' introuvable")

        students = []

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                # Nettoyer les données vides
                student = {k: v if v else None for k, v in row.items()}

                # Ajouter le nom complet pour l'affichage
                if 'nom' in student and 'prenom' in student:
                    student['full_name'] = f"{student['prenom']} {student['nom']}"

                students.append(student)

        return students

    def save_class(self, class_name: str, students: List[Dict]):
        """
        Sauvegarde les données d'une classe dans son fichier CSV

        Args:
            class_name: Nom de la classe
            students: Liste des étudiants avec leurs données
        """
        file_path = os.path.join(self.data_dir, f"{class_name}.csv")

        # Backup avant modification
        self._backup_file(file_path)

        # Déterminer tous les champs (colonnes)
        all_fields = set()
        for student in students:
            all_fields.update(student.keys())

        # Ordonner les champs : nom, prénom en premier, puis dates triées
        base_fields = ['nom', 'prenom']
        date_fields = sorted([f for f in all_fields if self._is_date_field(f)])
        other_fields = sorted([f for f in all_fields if f not in base_fields + date_fields and f != 'full_name'])

        fieldnames = base_fields + date_fields + other_fields

        # Écrire le CSV
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()

            for student in students:
                # Filtrer les champs temporaires comme 'full_name'
                row = {k: v for k, v in student.items() if k != 'full_name'}
                writer.writerow(row)

    def update_student_score(self, class_name: str, student_name: str, date: str, score: int):
        """
        Met à jour le score d'un étudiant pour une date donnée

        Args:
            class_name: Nom de la classe
            student_name: Nom complet de l'étudiant (prénom nom)
            date: Date au format YYYY-MM-DD
            score: Score (0, 1, 2, ou 3)
        """
        students = self.load_class(class_name)

        # Ajouter la colonne date si elle n'existe pas
        for student in students:
            if date not in student:
                student[date] = None

        # Trouver et mettre à jour l'étudiant
        updated = False
        for student in students:
            if student.get('full_name') == student_name:
                student[date] = str(score)
                updated = True
                break

        if not updated:
            raise ValueError(f"Étudiant '{student_name}' non trouvé dans la classe '{class_name}'")

        # Sauvegarder
        self.save_class(class_name, students)

    def create_class(self, class_name: str, students: List[Dict]):
        """
        Crée une nouvelle classe avec une liste d'étudiants

        Args:
            class_name: Nom de la nouvelle classe
            students: Liste des étudiants (format: [{'nom': '...', 'prenom': '...'}, ...])
        """
        file_path = os.path.join(self.data_dir, f"{class_name}.csv")

        if os.path.exists(file_path):
            raise ValueError(f"La classe '{class_name}' existe déjà")

        # Ajouter la date du jour comme première colonne de session
        today = datetime.now().strftime('%Y-%m-%d')
        for student in students:
            student[today] = None

        self.save_class(class_name, students)

    def import_from_simple_csv(self, source_file: str, class_name: str):
        """
        Importe une classe depuis un CSV simple (format nom;prénom)

        Args:
            source_file: Chemin du fichier CSV source
            class_name: Nom de la classe à créer
        """
        students = []

        with open(source_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')

            for row in reader:
                if len(row) >= 2:
                    students.append({
                        'nom': row[0],
                        'prenom': row[1]
                    })

        self.create_class(class_name, students)

    def get_session_dates(self, class_name: str) -> List[str]:
        """
        Retourne la liste des dates de sessions pour une classe

        Args:
            class_name: Nom de la classe

        Returns:
            Liste des dates triées
        """
        students = self.load_class(class_name)

        if not students:
            return []

        # Récupérer toutes les colonnes qui sont des dates
        all_fields = set()
        for student in students:
            all_fields.update(student.keys())

        date_fields = sorted([f for f in all_fields if self._is_date_field(f)])
        return date_fields

    def get_student_history(self, class_name: str, student_name: str) -> Dict:
        """
        Retourne l'historique complet d'un étudiant

        Args:
            class_name: Nom de la classe
            student_name: Nom complet de l'étudiant

        Returns:
            Dictionnaire avec l'historique des scores par date
        """
        students = self.load_class(class_name)

        for student in students:
            if student.get('full_name') == student_name:
                # Extraire uniquement les scores (dates)
                history = {}
                for key, value in student.items():
                    if self._is_date_field(key) and value is not None:
                        history[key] = int(value)
                return history

        raise ValueError(f"Étudiant '{student_name}' non trouvé")

    def _is_date_field(self, field: str) -> bool:
        """
        Vérifie si un nom de champ est une date

        Args:
            field: Nom du champ

        Returns:
            True si c'est un format de date YYYY-MM-DD
        """
        try:
            datetime.strptime(field, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _backup_file(self, file_path: str):
        """
        Crée une copie de sauvegarde d'un fichier

        Args:
            file_path: Chemin du fichier à sauvegarder
        """
        if not os.path.exists(file_path):
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        backup_name = f"{filename[:-4]}_{timestamp}.csv"
        backup_path = os.path.join(self.backup_dir, backup_name)

        shutil.copy2(file_path, backup_path)

        # Nettoyer les vieux backups (garder les 5 derniers)
        self._cleanup_old_backups(filename[:-4])

    def _cleanup_old_backups(self, class_name: str, keep: int = 5):
        """
        Supprime les anciennes sauvegardes pour une classe

        Args:
            class_name: Nom de la classe
            keep: Nombre de sauvegardes à conserver
        """
        pattern = f"{class_name}_"
        backups = []

        for file in os.listdir(self.backup_dir):
            if file.startswith(pattern) and file.endswith('.csv'):
                file_path = os.path.join(self.backup_dir, file)
                backups.append((file_path, os.path.getctime(file_path)))

        # Trier par date de création
        backups.sort(key=lambda x: x[1], reverse=True)

        # Supprimer les plus anciens
        for file_path, _ in backups[keep:]:
            os.remove(file_path)