## Installation du projet

### Méthode automatique (recommandée)

1. **Initialisation** (une seule fois) :
   ```bash
   init.bat
   ```
   Ce script détecte automatiquement la version Python avec TCL/TK, crée l'environnement virtuel et installe les dépendances.

2. **Configuration des clés API** :
   Créer et remplir les fichiers suivants avec vos clés si besoin :
   - `modules/abstractor/claude_api_key.txt` : Votre clé API Claude
   - `modules/abstractor/openai_api_key.txt` : Votre clé API OpenAI

3. **Lancement** :
   ```bash
   run.bat
   ```

### Méthode manuelle

1. **Prérequis** : Python 64 bits avec TCL/TK

2. **Créer l'environnement virtuel** :
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configuration des clés API** (voir ci-dessus)
   Créer et remplir les fichiers suivants avec vos clés si besoin :
   - `modules/abstractor/claude_api_key.txt` : Votre clé API Claude
   - `modules/abstractor/openai_api_key.txt` : Votre clé API OpenAI
4. **Lancer l'application** :
   ```bash
   python modules/UI_v2.py
   ```