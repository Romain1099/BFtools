#!/usr/bin/env python3
"""
Script de test pour Lottery Sessions
Vérifie que tous les modules fonctionnent correctement
"""

import os
import sys
import csv
from datetime import datetime

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test des imports des modules"""
    print("🧪 Test des imports...")

    try:
        from backend.csv_manager import CSVManager
        from backend.session_tracker import SessionTracker
        print("✅ Imports backend OK")
    except ImportError as e:
        print(f"❌ Erreur import backend: {e}")
        return False

    try:
        import flask
        from flask_cors import CORS
        print("✅ Imports Flask OK")
    except ImportError as e:
        print(f"❌ Erreur import Flask: {e}")
        return False

    return True

def test_csv_manager():
    """Test du gestionnaire CSV"""
    print("\n🧪 Test du CSVManager...")

    # Créer un dossier de test
    test_dir = "test_data"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    try:
        from backend.csv_manager import CSVManager

        manager = CSVManager(test_dir)

        # Test création de classe
        test_students = [
            {"nom": "Test", "prenom": "Élève1"},
            {"nom": "Test", "prenom": "Élève2"}
        ]

        manager.create_class("test_classe", test_students)
        print("✅ Création de classe OK")

        # Test lecture
        students = manager.load_class("test_classe")
        assert len(students) == 2
        print("✅ Lecture de classe OK")

        # Test mise à jour score
        manager.update_student_score("test_classe", "Élève1 Test",
                                   datetime.now().strftime('%Y-%m-%d'), 2)
        print("✅ Mise à jour score OK")

        # Nettoyer
        import shutil
        shutil.rmtree(test_dir)

        return True

    except Exception as e:
        print(f"❌ Erreur CSVManager: {e}")
        return False

def test_session_tracker():
    """Test du tracker de sessions"""
    print("\n🧪 Test du SessionTracker...")

    try:
        from backend.session_tracker import SessionTracker

        tracker = SessionTracker()

        # Test mode historique
        tracker.set_history_mode(True)
        assert tracker.is_history_mode() == True
        print("✅ Mode historique OK")

        # Test avec des données fictives
        test_students = [
            {"nom": "Test1", "prenom": "A", "full_name": "A Test1", "2024-01-15": "2"},
            {"nom": "Test2", "prenom": "B", "full_name": "B Test2"}
        ]

        stats = tracker.get_session_statistics(test_students, "2024-01-15")
        assert stats['questioned'] == 1
        print("✅ Statistiques OK")

        return True

    except Exception as e:
        print(f"❌ Erreur SessionTracker: {e}")
        return False

def test_flask_app():
    """Test de l'application Flask"""
    print("\n🧪 Test de l'application Flask...")

    try:
        # Import du module principal
        import lottery_sessions

        # Vérifier que l'app Flask existe
        assert hasattr(lottery_sessions, 'app')
        print("✅ Application Flask OK")

        # Tester la route principale
        with lottery_sessions.app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            print("✅ Route principale OK")

        return True

    except Exception as e:
        print(f"❌ Erreur Flask: {e}")
        return False

def test_files_structure():
    """Test de la structure des fichiers"""
    print("\n🧪 Test de la structure...")

    required_files = [
        "lottery_sessions.py",
        "backend/csv_manager.py",
        "backend/session_tracker.py",
        "templates/index.html",
        "static/styles.css",
        "static/app.js",
        "static/animations.js",
        "requirements.txt",
        "lottery_sessions.spec",
        "build.bat"
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)

    if missing:
        print(f"❌ Fichiers manquants: {missing}")
        return False
    else:
        print("✅ Structure des fichiers OK")
        return True

def main():
    """Fonction principale de test"""
    print("🚀 Tests Lottery Sessions")
    print("=" * 40)

    tests = [
        ("Structure des fichiers", test_files_structure),
        ("Imports", test_imports),
        ("CSVManager", test_csv_manager),
        ("SessionTracker", test_session_tracker),
        ("Application Flask", test_flask_app),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erreur test {name}: {e}")
            results.append((name, False))

    print("\n" + "=" * 40)
    print("📊 Résultats des tests:")

    success_count = 0
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        if result:
            success_count += 1

    print(f"\n📈 Score: {success_count}/{len(results)} tests réussis")

    if success_count == len(results):
        print("🎉 Tous les tests sont passés ! L'application est prête.")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")

    return success_count == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)