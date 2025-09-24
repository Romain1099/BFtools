"""
Gestionnaire de sessions et de l'historique
"""

from datetime import datetime
from typing import List, Dict, Optional

class SessionTracker:
    """Gère le suivi des sessions et le mode historique"""

    def __init__(self):
        """Initialise le tracker de sessions"""
        self.history_mode = True  # Par défaut, on tient compte de l'historique
        self.current_session = datetime.now().strftime('%Y-%m-%d')
        self.session_data = {}

    def set_history_mode(self, enabled: bool):
        """
        Active ou désactive le mode historique

        Args:
            enabled: True pour tenir compte de l'historique, False sinon
        """
        self.history_mode = enabled

    def is_history_mode(self) -> bool:
        """
        Vérifie si le mode historique est actif

        Returns:
            True si le mode historique est actif
        """
        return self.history_mode

    def filter_students_by_history(self, students: List[Dict], date: Optional[str] = None) -> List[Dict]:
        """
        Filtre les étudiants en fonction du mode historique par cycles complets

        Args:
            students: Liste complète des étudiants
            date: Date à vérifier (par défaut aujourd'hui)

        Returns:
            Liste des étudiants filtrés selon le mode
        """
        if not self.history_mode:
            # Mode sans historique : tous les étudiants sont disponibles
            return students

        # Mode avec historique : exclure ceux déjà interrogés DEPUIS LE DÉBUT du cycle
        filtered = []

        for student in students:
            # Vérifier si l'étudiant a été interrogé dans TOUTES les sessions du cycle
            has_been_questioned_in_cycle = False

            # Parcourir toutes les colonnes de dates pour voir s'il a déjà été interrogé
            for key in student.keys():
                if self._is_date_field(key) and student[key] is not None:
                    has_been_questioned_in_cycle = True
                    break

            # Si pas encore interrogé dans ce cycle, il est disponible
            if not has_been_questioned_in_cycle:
                filtered.append(student)

        return filtered

    def get_available_students(self, students: List[Dict], consider_previous_dates: bool = False) -> List[Dict]:
        """
        Retourne la liste des étudiants disponibles pour le tirage

        Args:
            students: Liste complète des étudiants
            consider_previous_dates: Si True, exclut aussi les étudiants interrogés les jours précédents

        Returns:
            Liste des étudiants disponibles
        """
        available = []

        for student in students:
            if consider_previous_dates and self.history_mode:
                # Vérifier toutes les dates précédentes
                has_been_questioned = False

                for key in student.keys():
                    if self._is_date_field(key) and student[key] is not None:
                        # Comparer les dates
                        try:
                            question_date = datetime.strptime(key, '%Y-%m-%d')
                            current_date = datetime.strptime(self.current_session, '%Y-%m-%d')

                            if question_date <= current_date:
                                has_been_questioned = True
                                break
                        except ValueError:
                            continue

                if not has_been_questioned:
                    available.append(student)
            else:
                # Mode simple : juste vérifier la date actuelle
                if self.current_session not in student or student[self.current_session] is None:
                    available.append(student)

        return available

    def get_session_statistics(self, students: List[Dict], date: Optional[str] = None) -> Dict:
        """
        Calcule les statistiques pour une session

        Args:
            students: Liste des étudiants
            date: Date de la session (par défaut aujourd'hui)

        Returns:
            Dictionnaire avec les statistiques
        """
        target_date = date or self.current_session
        stats = {
            'total_students': len(students),
            'questioned': 0,
            'not_questioned': 0,
            'scores': {
                '0': 0,  # Réponse erronée / refus
                '1': 0,  # Réponse partielle
                '2': 0,  # Réponse correcte
                '3': 0   # Bonus
            },
            'average_score': 0
        }

        total_score = 0
        scored_students = 0

        for student in students:
            if target_date in student and student[target_date] is not None:
                stats['questioned'] += 1
                score = str(student[target_date])

                if score in stats['scores']:
                    stats['scores'][score] += 1

                try:
                    total_score += int(score)
                    scored_students += 1
                except ValueError:
                    pass
            else:
                stats['not_questioned'] += 1

        # Calculer la moyenne
        if scored_students > 0:
            stats['average_score'] = round(total_score / scored_students, 2)

        return stats

    def get_student_performance(self, student: Dict) -> Dict:
        """
        Calcule les performances d'un étudiant sur toutes les sessions

        Args:
            student: Données de l'étudiant

        Returns:
            Dictionnaire avec les métriques de performance
        """
        performance = {
            'total_sessions': 0,
            'total_score': 0,
            'average_score': 0,
            'sessions': []
        }

        for key in student.keys():
            if self._is_date_field(key) and student[key] is not None:
                try:
                    score = int(student[key])
                    performance['total_sessions'] += 1
                    performance['total_score'] += score
                    performance['sessions'].append({
                        'date': key,
                        'score': score
                    })
                except ValueError:
                    pass

        # Calculer la moyenne
        if performance['total_sessions'] > 0:
            performance['average_score'] = round(
                performance['total_score'] / performance['total_sessions'], 2
            )

        # Trier les sessions par date
        performance['sessions'].sort(key=lambda x: x['date'])

        return performance

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

    def suggest_next_students(self, students: List[Dict], count: int = 5) -> List[Dict]:
        """
        Suggère les prochains étudiants à interroger basé sur leur historique

        Args:
            students: Liste des étudiants
            count: Nombre d'étudiants à suggérer

        Returns:
            Liste des étudiants suggérés
        """
        # Calculer un score de priorité pour chaque étudiant
        student_priorities = []

        for student in students:
            priority = 0
            last_questioned = None
            total_questions = 0

            for key in student.keys():
                if self._is_date_field(key) and student[key] is not None:
                    total_questions += 1
                    try:
                        date = datetime.strptime(key, '%Y-%m-%d')
                        if last_questioned is None or date > last_questioned:
                            last_questioned = date
                    except ValueError:
                        pass

            # Calculer la priorité (moins interrogé = plus prioritaire)
            priority = -total_questions * 1000  # Poids fort sur le nombre de fois interrogé

            if last_questioned:
                # Ajouter les jours depuis la dernière interrogation
                days_since = (datetime.now() - last_questioned).days
                priority += days_since

            student_priorities.append({
                'student': student,
                'priority': priority
            })

        # Trier par priorité décroissante
        student_priorities.sort(key=lambda x: x['priority'], reverse=True)

        # Retourner les N premiers
        return [sp['student'] for sp in student_priorities[:count]]

    def is_cycle_complete(self, students: List[Dict]) -> bool:
        """
        Vérifie si tous les étudiants ont été interrogés (cycle complet)

        Args:
            students: Liste des étudiants

        Returns:
            True si tous les étudiants ont été interrogés au moins une fois
        """
        for student in students:
            has_been_questioned = False

            # Vérifier s'il a été interrogé dans au moins une session
            for key in student.keys():
                if self._is_date_field(key) and student[key] is not None:
                    has_been_questioned = True
                    break

            # Si au moins un étudiant n'a jamais été interrogé, le cycle n'est pas complet
            if not has_been_questioned:
                return False

        return True

    def get_cycle_progress(self, students: List[Dict]) -> Dict:
        """
        Retourne les statistiques de progression du cycle

        Args:
            students: Liste des étudiants

        Returns:
            Dictionnaire avec les stats du cycle
        """
        total_students = len(students)
        questioned_students = 0

        for student in students:
            # Vérifier s'il a été interrogé dans au moins une session
            for key in student.keys():
                if self._is_date_field(key) and student[key] is not None:
                    questioned_students += 1
                    break

        return {
            'total': total_students,
            'questioned': questioned_students,
            'remaining': total_students - questioned_students,
            'progress_percent': round((questioned_students / total_students) * 100, 1) if total_students > 0 else 0,
            'is_complete': questioned_students == total_students
        }

    def reset_cycle(self, students: List[Dict]) -> List[Dict]:
        """
        Remet à zéro le cycle (tous les étudiants redeviennent disponibles)
        Ne supprime pas l'historique, juste remet tout le monde à disposition

        Args:
            students: Liste des étudiants

        Returns:
            Liste des étudiants avec le cycle remis à zéro (pour affichage)
        """
        # Cette méthode ne modifie pas réellement les données CSV
        # Elle est utilisée pour l'affichage côté client
        # Le vrai reset se fait en créant une nouvelle colonne de date

        reset_students = []
        for student in students.copy():
            # Copier l'étudiant sans les données de dates (pour affichage)
            reset_student = {
                'nom': student.get('nom', ''),
                'prenom': student.get('prenom', ''),
                'full_name': student.get('full_name', '')
            }

            # Conserver l'historique mais marquer comme disponible pour le nouveau cycle
            for key, value in student.items():
                if self._is_date_field(key):
                    reset_student[key] = value

            reset_students.append(reset_student)

        return reset_students