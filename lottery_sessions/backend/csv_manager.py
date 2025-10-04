"""
Gestionnaire CSV avec support multi-sessions et multi-classes
"""

import os
import csv
import shutil
import threading
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

        # Créer un dossier pour les cycles archivés
        self.cycles_dir = os.path.join(self.data_dir, 'cycles')
        if not os.path.exists(self.cycles_dir):
            os.makedirs(self.cycles_dir)

        # Verrous pour protéger l'accès concurrent aux fichiers
        self._file_locks = {}
        self._locks_lock = threading.Lock()

    def _get_file_lock(self, class_name: str) -> threading.Lock:
        """
        Obtient ou crée un verrou pour un fichier de classe

        Args:
            class_name: Nom de la classe

        Returns:
            Verrou thread-safe pour ce fichier
        """
        with self._locks_lock:
            if class_name not in self._file_locks:
                self._file_locks[class_name] = threading.Lock()
            return self._file_locks[class_name]

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

    def list_classes_with_variants(self) -> Dict[str, List[str]]:
        """
        Retourne les classes groupées par classe de base avec leurs variantes

        Format de nom attendu:
        - classe_<nom>.csv → classe de base
        - classe_<nom>_<type>.csv → variante

        Returns:
            Dict avec structure:
            {
                'classe_1ere-TC_QF': {
                    'base': 'classe_1ere-TC_QF',
                    'variants': ['classe_1ere-TC_QF_groupe1', 'classe_1ere-TC_QF_groupe2']
                }
            }
        """
        all_classes = self.list_classes()
        grouped = {}

        for class_name in all_classes:
            # Déterminer la classe de base
            # Si contient un underscore après "classe_", c'est peut-être une variante
            parts = class_name.split('_')

            if len(parts) >= 3:  # Ex: classe_1ere-TC_QF_groupe1
                # Reconstruire la base (tout sauf le dernier élément)
                base_name = '_'.join(parts[:-1])
            else:  # Ex: classe_1ere-TC_QF
                base_name = class_name

            # Initialiser le groupe si nécessaire
            if base_name not in grouped:
                grouped[base_name] = {
                    'base': base_name,
                    'variants': []
                }

            # Ajouter comme variante si ce n'est pas la base
            if class_name != base_name:
                grouped[base_name]['variants'].append(class_name)

        return grouped

    def create_variant(self, base_class: str, variant_type: str) -> str:
        """
        Crée une variante d'une classe en copiant les colonnes nom;prenom
        Si la classe de base n'existe pas, elle est créée à partir d'une variante existante

        Args:
            base_class: Nom de la classe de base (ex: classe_1ere-TC_QF)
            variant_type: Type de variante (ex: groupe1)

        Returns:
            Nom de la variante créée

        Raises:
            ValueError: Si aucune classe/variante n'existe ou si la variante existe déjà
        """
        base_path = os.path.join(self.data_dir, f"{base_class}.csv")

        # Si la classe de base n'existe pas, essayer de la créer depuis une variante existante
        if not os.path.exists(base_path):
            # Chercher une variante existante
            all_classes = self.list_classes()
            existing_variant = None

            for class_name in all_classes:
                if class_name.startswith(f"{base_class}_"):
                    existing_variant = class_name
                    break

            if not existing_variant:
                raise ValueError(f"Aucune classe ou variante trouvée pour '{base_class}'")

            # Créer la classe de base à partir de la variante
            variant_students = self.load_class(existing_variant)
            base_students = []
            for student in variant_students:
                base_student = {
                    'nom': student.get('nom', ''),
                    'prenom': student.get('prenom', ''),
                    'full_name': student.get('full_name', '')
                }
                base_students.append(base_student)

            # Sauvegarder la classe de base
            self.save_class(base_class, base_students)

        # Créer le nom de la variante
        variant_name = f"{base_class}_{variant_type}"
        variant_path = os.path.join(self.data_dir, f"{variant_name}.csv")

        # Vérifier que la variante n'existe pas déjà
        if os.path.exists(variant_path):
            raise ValueError(f"La variante '{variant_name}' existe déjà")

        # Charger la classe de base (qui existe maintenant)
        base_students = self.load_class(base_class)

        # Extraire seulement nom, prenom, full_name
        variant_students = []
        for student in base_students:
            variant_student = {
                'nom': student.get('nom', ''),
                'prenom': student.get('prenom', ''),
                'full_name': student.get('full_name', '')
            }
            variant_students.append(variant_student)

        # Sauvegarder la variante
        self.save_class(variant_name, variant_students)

        return variant_name

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
        lock = self._get_file_lock(class_name)

        with lock:
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f, delimiter=';')

                    # Vérifier que les colonnes requises sont présentes
                    if reader.fieldnames is None:
                        raise ValueError(f"Le fichier CSV '{class_name}.csv' est vide ou mal formaté")

                    if 'nom' not in reader.fieldnames or 'prenom' not in reader.fieldnames:
                        raise ValueError(
                            f"Le fichier CSV '{class_name}.csv' doit contenir les colonnes 'nom' et 'prenom' séparées par ';'\n"
                            f"Colonnes trouvées: {', '.join(reader.fieldnames)}"
                        )

                    for row in reader:
                        # Nettoyer les données vides
                        student = {k: v if v else None for k, v in row.items()}

                        # Ajouter le nom complet pour l'affichage
                        if 'nom' in student and 'prenom' in student:
                            student['full_name'] = f"{student['prenom']} {student['nom']}"

                        students.append(student)

            except UnicodeDecodeError as e:
                raise ValueError(f"Erreur d'encodage du fichier '{class_name}.csv'. Assurez-vous qu'il est encodé en UTF-8.")
            except csv.Error as e:
                raise ValueError(f"Erreur de format CSV dans '{class_name}.csv': {str(e)}")

        return students

    def save_class(self, class_name: str, students: List[Dict]):
        """
        Sauvegarde les données d'une classe dans son fichier CSV
        Préserve l'ordre des colonnes existantes

        Args:
            class_name: Nom de la classe
            students: Liste des étudiants avec leurs données
        """
        file_path = os.path.join(self.data_dir, f"{class_name}.csv")
        lock = self._get_file_lock(class_name)

        with lock:
            try:
                # Backup avant modification
                self._backup_file(file_path)

                # Récupérer l'ordre des colonnes existantes
                existing_order = []
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        reader = csv.DictReader(f, delimiter=';')
                        if reader.fieldnames:
                            existing_order = [field for field in reader.fieldnames if field]

                # Déterminer tous les champs (colonnes)
                all_fields = set()
                for student in students:
                    all_fields.update(student.keys())
                all_fields.discard('full_name')  # Exclure les champs temporaires

                # Construire l'ordre final des colonnes
                base_fields = ['nom', 'prenom']

                # Séparer les champs en catégories
                new_dates = []
                new_cycles = []
                other_fields = []

                for field in all_fields:
                    if field not in base_fields:
                        if self._is_date_field(field):
                            new_dates.append(field)
                        elif field == 'NEW_CYCLE':
                            new_cycles.append(field)
                        else:
                            other_fields.append(field)

                # Construire fieldnames en préservant l'ordre existant
                fieldnames = base_fields.copy()

                # Ajouter les colonnes existantes dans leur ordre d'origine
                for field in existing_order:
                    if field in base_fields:
                        continue
                    if field in all_fields:
                        fieldnames.append(field)
                        # Retirer des nouvelles listes pour éviter les doublons
                        if field in new_dates:
                            new_dates.remove(field)
                        if field in new_cycles:
                            new_cycles.remove(field)
                        if field in other_fields:
                            other_fields.remove(field)

                # Ajouter les nouvelles colonnes (NEW_CYCLE en premier, puis dates triées)
                if new_cycles:
                    fieldnames.extend(new_cycles)
                if new_dates:
                    fieldnames.extend(sorted(new_dates))
                if other_fields:
                    fieldnames.extend(sorted(other_fields))

                # Écrire le CSV dans un fichier temporaire d'abord
                temp_path = file_path + '.tmp'
                with open(temp_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
                    writer.writeheader()

                    for student in students:
                        # Filtrer les champs temporaires comme 'full_name'
                        row = {k: v for k, v in student.items() if k != 'full_name'}
                        writer.writerow(row)

                # Remplacer l'ancien fichier par le nouveau (opération atomique)
                if os.path.exists(file_path):
                    os.remove(file_path)
                os.rename(temp_path, file_path)

            except Exception as e:
                # Nettoyer le fichier temporaire en cas d'erreur
                temp_path = file_path + '.tmp'
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise ValueError(f"Erreur lors de la sauvegarde de '{class_name}.csv': {str(e)}")

    def update_student_score(self, class_name: str, student_name: str, date: str, score):
        """
        Met à jour le score d'un étudiant pour une date donnée

        Args:
            class_name: Nom de la classe
            student_name: Nom complet de l'étudiant (prénom nom)
            date: Date au format YYYY-MM-DD
            score: Score (0, 1, 2, 3, ou "ABS" pour absent)
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

    def validate_csv_format(self, file_path: str) -> tuple[bool, str]:
        """
        Valide le format d'un fichier CSV avant import

        Args:
            file_path: Chemin du fichier à valider

        Returns:
            Tuple (est_valide, message_erreur)
        """
        # Vérifier l'extension
        if not file_path.lower().endswith('.csv'):
            return False, "Le fichier doit avoir l'extension .csv"

        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            return False, f"Le fichier '{file_path}' n'existe pas"

        try:
            # Lire et vérifier le contenu
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')

                # Vérifier les en-têtes
                if reader.fieldnames is None or len(reader.fieldnames) == 0:
                    return False, "Le fichier est vide ou mal formaté"

                # Nettoyer les espaces dans les noms de colonnes
                fieldnames = [field.strip().lower() for field in reader.fieldnames]

                if 'nom' not in fieldnames or 'prenom' not in fieldnames:
                    return False, (
                        "Le fichier CSV doit contenir les colonnes 'nom' et 'prenom' (séparées par ';')\n\n"
                        "Format attendu:\n"
                        "nom;prenom\n"
                        "Dupont;Jean\n"
                        "Martin;Marie\n\n"
                        f"Colonnes trouvées dans votre fichier: {', '.join(reader.fieldnames)}"
                    )

                # Vérifier qu'il y a au moins une ligne de données
                rows = list(reader)
                if len(rows) == 0:
                    return False, "Le fichier ne contient aucun étudiant (aucune ligne après les en-têtes)"

                # Vérifier que les lignes ont bien nom et prénom non vides
                empty_count = 0
                for i, row in enumerate(rows, start=2):
                    nom = row.get('nom', '').strip()
                    prenom = row.get('prenom', '').strip()
                    if not nom or not prenom:
                        empty_count += 1

                if empty_count == len(rows):
                    return False, "Toutes les lignes du fichier sont vides"

                if empty_count > 0:
                    return True, f"Attention: {empty_count} ligne(s) vide(s) seront ignorées"

            return True, "Format valide"

        except UnicodeDecodeError:
            return False, (
                "Erreur d'encodage du fichier.\n\n"
                "Le fichier doit être encodé en UTF-8.\n"
                "Pour corriger:\n"
                "1. Ouvrez le fichier dans Excel ou un éditeur de texte\n"
                "2. Enregistrez-le avec l'encodage UTF-8\n"
                "3. Réessayez l'import"
            )
        except Exception as e:
            return False, f"Erreur lors de la lecture du fichier: {str(e)}"

    def import_from_content(self, file_content: str, class_name: str) -> tuple[bool, str]:
        """
        Importe une classe depuis le contenu d'un CSV

        Args:
            file_content: Contenu du fichier CSV
            class_name: Nom de la classe à créer

        Returns:
            Tuple (succès, message)
        """
        try:
            # Normaliser le nom de classe
            if not class_name.startswith('classe_'):
                class_name = 'classe_' + class_name

            # Vérifier si la classe existe déjà
            if class_name in self.list_classes():
                return False, f"La classe '{class_name}' existe déjà"

            # Parser le CSV depuis le contenu
            lines = file_content.strip().split('\n')
            if len(lines) < 2:
                return False, "Le fichier CSV doit contenir au moins une ligne d'en-tête et une ligne de données"

            # Lire les en-têtes
            header = lines[0].strip()
            fieldnames = [field.strip().lower() for field in header.split(';')]

            if 'nom' not in fieldnames or 'prenom' not in fieldnames:
                return False, (
                    "Le fichier CSV doit contenir les colonnes 'nom' et 'prenom' (séparées par ';')\n\n"
                    "Format attendu:\n"
                    "nom;prenom\n"
                    "Dupont;Jean\n"
                    "Martin;Marie\n\n"
                    f"Colonnes trouvées dans votre fichier: {', '.join(fieldnames)}"
                )

            # Lire les étudiants
            students = []
            empty_count = 0

            for i, line in enumerate(lines[1:], start=2):
                if not line.strip():
                    continue

                parts = line.split(';')
                if len(parts) < 2:
                    continue

                nom = parts[fieldnames.index('nom')].strip()
                prenom = parts[fieldnames.index('prenom')].strip()

                if nom and prenom:
                    students.append({
                        'nom': nom,
                        'prenom': prenom
                    })
                else:
                    empty_count += 1

            if len(students) == 0:
                return False, "Aucun étudiant valide trouvé dans le fichier"

            # Créer la classe
            self.create_class(class_name, students)

            if empty_count > 0:
                return True, f"Import réussi ! {len(students)} étudiant(s) importé(s) ({empty_count} ligne(s) vide(s) ignorée(s))"
            else:
                return True, f"Import réussi ! {len(students)} étudiant(s) importé(s)"

        except Exception as e:
            return False, f"Erreur lors de l'import: {str(e)}"

    def import_from_simple_csv(self, source_file: str, class_name: str):
        """
        Importe une classe depuis un CSV simple (format nom;prénom)

        Args:
            source_file: Chemin du fichier CSV source
            class_name: Nom de la classe à créer

        Raises:
            ValueError: Si le format du fichier est invalide
        """
        # Valider le format d'abord
        is_valid, message = self.validate_csv_format(source_file)
        if not is_valid:
            raise ValueError(message)

        students = []

        try:
            with open(source_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f, delimiter=';')

                for row in reader:
                    nom = row.get('nom', '').strip()
                    prenom = row.get('prenom', '').strip()

                    # Ignorer les lignes vides
                    if nom and prenom:
                        students.append({
                            'nom': nom,
                            'prenom': prenom
                        })

            if len(students) == 0:
                raise ValueError("Aucun étudiant valide trouvé dans le fichier")

            self.create_class(class_name, students)

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Erreur lors de l'import du fichier CSV: {str(e)}")

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

    def get_current_cycle_dates(self, class_name: str) -> List[str]:
        """
        Retourne toutes les dates du CSV actuel (cycle en cours)

        Args:
            class_name: Nom de la classe

        Returns:
            Liste des dates du cycle actuel
        """
        students = self.load_class(class_name)
        if not students:
            return []

        all_fields = list(students[0].keys())

        # Retourner simplement toutes les dates (plus de logique NEW_CYCLE)
        return sorted([f for f in all_fields if self._is_date_field(f)])

    def archive_cycle(self, class_name: str) -> str:
        """
        Archive le cycle actuel dans un fichier séparé et nettoie le CSV

        Args:
            class_name: Nom de la classe

        Returns:
            Nom du fichier archivé
        """
        students = self.load_class(class_name)

        # Récupérer TOUTES les dates du CSV actuel
        all_fields = list(students[0].keys()) if students else []
        all_dates = sorted([f for f in all_fields if self._is_date_field(f)])

        if not all_dates:
            raise ValueError("Aucune date à archiver")

        # Créer le nom du fichier d'archive
        first_date = min(all_dates)
        last_date = max(all_dates)

        # Format: jj-mm
        first_formatted = datetime.strptime(first_date, '%Y-%m-%d').strftime('%d-%m')
        last_formatted = datetime.strptime(last_date, '%Y-%m-%d').strftime('%d-%m')

        archive_name = f"{class_name}_{first_formatted}_{last_formatted}.csv"
        archive_path = os.path.join(self.cycles_dir, archive_name)

        # Copier le fichier actuel vers l'archive
        current_path = os.path.join(self.data_dir, f"{class_name}.csv")
        shutil.copy2(current_path, archive_path)

        # NETTOYER le CSV actuel : garder seulement nom, prenom, full_name
        cleaned_students = []
        for student in students:
            cleaned_student = {
                'nom': student.get('nom', ''),
                'prenom': student.get('prenom', ''),
                'full_name': student.get('full_name', '')
            }
            cleaned_students.append(cleaned_student)

        self.save_class(class_name, cleaned_students)

        return archive_name

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