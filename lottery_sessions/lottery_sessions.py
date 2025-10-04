#!/usr/bin/env python3
"""
Lottery Sessions - Application de tirage au sort avec suivi de sessions
Version standalone avec Flask embarqué pour compilation PyInstaller
"""

import os
import sys
import webbrowser
import threading
import socket
import time
import json
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
import signal

# Import des modules backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.csv_manager import CSVManager
from backend.session_tracker import SessionTracker

# Configuration Flask
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)

# Instances globales
csv_manager = None
session_tracker = None
server_thread = None
shutdown_flag = False
config = None

def get_free_port():
    """Trouve un port libre pour le serveur Flask"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def load_config():
    """Charge la configuration depuis data/config.json"""
    global config

    # Déterminer le bon chemin pour le dossier data
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    data_dir = os.path.join(base_dir, 'data')
    config_path = os.path.join(data_dir, 'config.json')

    # Configuration par défaut complète (sans heartbeat)
    default_config = {
        "animation": {
            "shuffle": {
                "maxShuffles": 6,
                "angleIncrement": 25,
                "angleOffset": 35,
                "baseRadius": 6,
                "radiusVariation": 8,
                "radiusFrequency": 0.15,
                "offsetMultiplier": 0.25,
                "movementDuration": 800,
                "delayMin": 450,
                "delayVariation": 100,
                "pulseProbability": 0.1,
                "pulseDuration": 500
            },
            "highlight": {
                "maxRounds": 4,
                "delayMin": 400,
                "delayVariation": 200
            },
            "general": {
                "initialDisplayDelay": 50,
                "transitionDisableDuration": 250
            }
        }
    }

    # Créer le dossier data s'il n'existe pas
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"📁 Dossier data créé : {data_dir}")

    # Charger la config depuis le fichier si elle existe
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                print(f"✅ Configuration complète chargée depuis {config_path}")
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement de la config: {e}")
            config = default_config
    else:
        # Créer le fichier de config par défaut dans data/
        try:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            config = default_config
            print(f"✅ Fichier de configuration créé : {config_path}")
        except Exception as e:
            print(f"⚠️ Impossible de créer le fichier de config: {e}")
            config = default_config
            print("ℹ️ Utilisation de la configuration par défaut")

    return config

def initialize_managers():
    """Initialise les gestionnaires CSV et de sessions"""
    global csv_manager, session_tracker

    # Déterminer le bon chemin pour le dossier data
    if getattr(sys, 'frozen', False):
        # Si on est dans l'executable compilé
        # Le dossier data doit être à côté du .exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # Mode développement
        base_dir = os.path.dirname(os.path.abspath(__file__))

    data_dir = os.path.join(base_dir, 'data')

    # Créer le dossier data s'il n'existe pas
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"📁 Dossier data créé : {data_dir}")
    else:
        print(f"📁 Dossier data trouvé : {data_dir}")

    csv_manager = CSVManager(data_dir)
    session_tracker = SessionTracker()

# Routes API
@app.route('/')
def index():
    """Page principale de l'application"""
    return render_template('index.html')

@app.route('/api/classes')
def get_classes():
    """Retourne la liste des fichiers CSV disponibles"""
    try:
        classes = csv_manager.list_classes()
        return jsonify({'success': True, 'classes': classes})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/classes_with_variants')
def get_classes_with_variants():
    """Retourne les classes groupées avec leurs variantes"""
    try:
        grouped = csv_manager.list_classes_with_variants()
        return jsonify({'success': True, 'grouped': grouped})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/create_variant', methods=['POST'])
def create_variant():
    """Crée une variante d'une classe"""
    try:
        data = request.json
        base_class = data['base_class']
        variant_type = data['variant_type']

        variant_name = csv_manager.create_variant(base_class, variant_type)

        return jsonify({
            'success': True,
            'variant_name': variant_name,
            'message': f'Variante "{variant_type}" créée avec succès'
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e), 'error_type': 'validation'}), 400
    except Exception as e:
        print(f"Erreur lors de la création de la variante: {e}")
        return jsonify({'success': False, 'error': str(e), 'error_type': 'server'}), 500

@app.route('/api/students/<class_name>')
def get_students(class_name):
    """Retourne la liste des étudiants d'une classe avec leur historique"""
    try:
        students = csv_manager.load_class(class_name)
        today = datetime.now().strftime('%Y-%m-%d')

        # Ajouter le statut pour aujourd'hui
        for student in students:
            student['checked'] = student.get(today) is None
            student['today_score'] = student.get(today)

        return jsonify({
            'success': True,
            'students': students,
            'date': today
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/draw', methods=['POST'])
def record_draw():
    """Enregistre un tirage au sort - NE fait rien, juste pour tracking côté client"""
    try:
        # On ne fait RIEN ici
        # L'étudiant ne sera marqué comme interrogé QUE s'il reçoit une note via /api/score
        # Cela permet de "Passer" sans marquer l'étudiant
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/score', methods=['POST'])
def update_score():
    """Met à jour le score d'un étudiant"""
    try:
        data = request.json
        class_name = data['class_name']
        student_name = data['student_name']
        score = data['score']  # 0, 1, 2, 3, ou "ABS"
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Valider le score (doit être 0-3 ou "ABS")
        if score != 'ABS' and (not isinstance(score, int) or score < 0 or score > 3):
            return jsonify({
                'success': False,
                'error': 'Le score doit être entre 0 et 3, ou "ABS" pour absent',
                'error_type': 'validation'
            }), 400

        csv_manager.update_student_score(class_name, student_name, date, score)

        return jsonify({'success': True})
    except ValueError as e:
        # Erreur de validation ou de format
        return jsonify({'success': False, 'error': str(e), 'error_type': 'validation'}), 400
    except FileNotFoundError as e:
        # Fichier de classe introuvable
        return jsonify({'success': False, 'error': str(e), 'error_type': 'not_found'}), 404
    except Exception as e:
        # Erreur inattendue
        print(f"Erreur lors de la mise à jour du score: {e}")
        return jsonify({
            'success': False,
            'error': f"Erreur lors de l'enregistrement du score: {str(e)}\n\nVérifiez que le fichier CSV est bien formaté et accessible.",
            'error_type': 'server'
        }), 500

@app.route('/api/sessions/<class_name>')
def get_sessions(class_name):
    """Retourne l'historique des sessions pour une classe"""
    try:
        sessions = csv_manager.get_session_dates(class_name)
        return jsonify({'success': True, 'sessions': sessions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/create_class', methods=['POST'])
def create_class():
    """Crée une nouvelle classe à partir d'un template ou vide"""
    try:
        data = request.json
        class_name = data['class_name']
        students = data.get('students', [])

        csv_manager.create_class(class_name, students)

        return jsonify({'success': True})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e), 'error_type': 'validation'}), 400
    except Exception as e:
        print(f"Erreur lors de la création de la classe: {e}")
        return jsonify({'success': False, 'error': str(e), 'error_type': 'server'}), 500

@app.route('/api/import_class', methods=['POST'])
def import_class():
    """Importe une classe depuis un fichier CSV"""
    try:
        data = request.json
        file_content = data['file_content']
        class_name = data['class_name']

        # Normaliser le nom de classe
        if not class_name.startswith('classe_'):
            class_name = 'classe_' + class_name

        # Importer depuis le contenu
        is_valid, message = csv_manager.import_from_content(file_content, class_name)

        if is_valid:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message, 'error_type': 'validation'}), 400

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e), 'error_type': 'validation'}), 400
    except Exception as e:
        print(f"Erreur lors de l'import de la classe: {e}")
        return jsonify({'success': False, 'error': str(e), 'error_type': 'server'}), 500

@app.route('/api/history_mode', methods=['POST'])
def set_history_mode():
    """Active/désactive le mode historique"""
    try:
        data = request.json
        enabled = data['enabled']
        session_tracker.set_history_mode(enabled)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/cycle_progress/<class_name>')
def get_cycle_progress(class_name):
    """Retourne la progression du cycle pour une classe"""
    try:
        students = csv_manager.load_class(class_name)
        progress = session_tracker.get_cycle_progress(students)
        is_complete = session_tracker.is_cycle_complete(students)

        return jsonify({
            'success': True,
            'progress': progress,
            'is_complete': is_complete
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reset_cycle/<class_name>', methods=['POST'])
def reset_cycle(class_name):
    """Démarre un nouveau cycle - archive le cycle actuel et tous les étudiants redeviennent disponibles"""
    try:
        # Archiver le cycle actuel
        archive_name = csv_manager.archive_cycle(class_name)

        return jsonify({
            'success': True,
            'message': f'Cycle archivé ({archive_name}). Nouveau cycle démarré - tous les étudiants sont à nouveau disponibles'
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e), 'error_type': 'validation'}), 400
    except Exception as e:
        print(f"Erreur lors du reset du cycle: {e}")
        return jsonify({'success': False, 'error': str(e), 'error_type': 'server'}), 500


@app.route('/api/config')
def get_config():
    """Retourne la configuration du serveur"""
    return jsonify({'success': True, 'config': config})

@app.route('/api/shutdown', methods=['POST'])
def shutdown_server():
    """Arrête proprement le serveur"""
    def shutdown():
        time.sleep(1)
        os._exit(0)

    thread = threading.Thread(target=shutdown)
    thread.daemon = True
    thread.start()

    return jsonify({'success': True, 'message': 'Serveur en cours d\'arrêt...'})

def open_browser(port):
    """Ouvre automatiquement le navigateur après un délai"""
    def _open():
        import time
        time.sleep(1.5)  # Attendre que le serveur démarre
        webbrowser.open(f'http://localhost:{port}')

    thread = threading.Thread(target=_open)
    thread.daemon = True
    thread.start()

def signal_handler(sig, frame):
    """Gestion propre de l'arrêt du serveur"""
    global shutdown_flag
    shutdown_flag = True
    print("\nArrêt du serveur...")
    sys.exit(0)

def main():
    """Fonction principale"""
    global config

    # Charger la configuration
    config = load_config()

    print("""
    ╔═══════════════════════════════════════╗
    ║     LOTTERY SESSIONS - v2.0           ║
    ║     Tirage au sort avec historique    ║
    ╚═══════════════════════════════════════╝
    """)

    # Initialisation
    initialize_managers()

    # Trouver un port libre
    port = get_free_port()
    print(f"🚀 Démarrage du serveur sur le port {port}...")
    print(f"ℹ️  Utilisez le bouton 'Quitter l'application' pour arrêter le serveur proprement.")
    print(f"ℹ️  Ou utilisez Ctrl+C dans cette fenêtre.")

    # Gestion du signal d'arrêt
    signal.signal(signal.SIGINT, signal_handler)

    # Ouvrir le navigateur
    open_browser(port)

    # Démarrer Flask
    try:
        app.run(
            host='127.0.0.1',
            port=port,
            debug=False,
            use_reloader=False
        )
    except Exception as e:
        print(f"Erreur lors du démarrage du serveur: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Pour PyInstaller
    if getattr(sys, 'frozen', False):
        # Si on est dans l'executable compilé
        template_dir = os.path.join(sys._MEIPASS, 'templates')
        static_dir = os.path.join(sys._MEIPASS, 'static')
        app.template_folder = template_dir
        app.static_folder = static_dir

    main()