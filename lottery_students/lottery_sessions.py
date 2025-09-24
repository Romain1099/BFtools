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
last_heartbeat = None
heartbeat_monitor_thread = None
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

    # Configuration par défaut complète
    default_config = {
        "heartbeat": {
            "intervalMs": 5000,
            "timeoutMs": 10000,
            "checkIntervalMs": 2000
        },
        "server": {
            "autoShutdown": True,
            "shutdownOnClose": True
        },
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
    """Enregistre un tirage au sort"""
    try:
        data = request.json
        class_name = data['class_name']
        student_name = data['student_name']
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Marquer comme interrogé (score 0 par défaut)
        csv_manager.update_student_score(class_name, student_name, date, 0)

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
        score = data['score']  # 0, 1, 2, ou 3
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

        csv_manager.update_student_score(class_name, student_name, date, score)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
    """Démarre un nouveau cycle - tous les étudiants redeviennent disponibles"""
    try:
        # Le reset se fait en créant implicitement une nouvelle colonne de date
        # lors du prochain tirage. Ici on retourne juste la confirmation

        students = csv_manager.load_class(class_name)

        return jsonify({
            'success': True,
            'message': 'Nouveau cycle démarré - tous les étudiants sont à nouveau disponibles'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/heartbeat', methods=['POST'])
def heartbeat():
    """Reçoit un heartbeat du client pour maintenir le serveur actif"""
    global last_heartbeat
    last_heartbeat = time.time()
    return jsonify({'success': True, 'timestamp': last_heartbeat})

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

def monitor_heartbeat():
    """Surveille le heartbeat et arrête le serveur si pas de signal"""
    global last_heartbeat, shutdown_flag, config

    if not config['server'].get('autoShutdown', True):
        print("ℹ️ Auto-shutdown désactivé")
        return

    # Attendre un peu que le client se connecte
    time.sleep(10)

    timeout_seconds = config['heartbeat']['timeoutMs'] / 1000
    check_interval_seconds = config['heartbeat']['checkIntervalMs'] / 1000

    while not shutdown_flag:
        if last_heartbeat:
            # Vérifier si le dernier heartbeat date de plus du timeout configuré
            if time.time() - last_heartbeat > timeout_seconds:
                print(f"\n⚠️ Aucun heartbeat reçu depuis {timeout_seconds} secondes. Arrêt du serveur...")
                os._exit(0)  # Arrêt forcé du processus
        time.sleep(check_interval_seconds)  # Vérifier selon l'intervalle configuré

def signal_handler(sig, frame):
    """Gestion propre de l'arrêt du serveur"""
    global shutdown_flag
    shutdown_flag = True
    print("\nArrêt du serveur...")
    sys.exit(0)

def main():
    """Fonction principale"""
    global heartbeat_monitor_thread, last_heartbeat, config

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
    if config['server'].get('autoShutdown', True):
        timeout_s = config['heartbeat']['timeoutMs'] / 1000
        print(f"ℹ️  Le serveur s'arrêtera automatiquement {timeout_s}s après la fermeture de la page.")
    else:
        print(f"ℹ️  Auto-shutdown désactivé. Utilisez le bouton Quitter ou Ctrl+C pour arrêter.")

    # Initialiser le heartbeat
    last_heartbeat = time.time()

    # Démarrer le moniteur de heartbeat
    heartbeat_monitor_thread = threading.Thread(target=monitor_heartbeat)
    heartbeat_monitor_thread.daemon = True
    heartbeat_monitor_thread.start()

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