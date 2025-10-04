# QF Generator - Gestionnaire de Questions Flash

Application de génération et gestion de questions flash pour l'enseignement des mathématiques avec assistance IA.

## Prérequis

- Python 3.11.4 (ou version compatible)
- LuaLaTeX installé sur le système
- Clé API OpenAI ou Anthropic (Claude)

## Installation rapide (Windows)

### Méthode 1 : Avec les scripts automatiques

```bash
# 1. Initialisation (une seule fois)
init.bat

# 2. Lancer l'application
run.bat
```

Le script `init.bat` :
- Crée l'environnement virtuel Python
- Installe toutes les dépendances
- Configure le chemin TCL_LIBRARY

### Méthode 2 : Installation manuelle

```bash
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement
venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python main.py
```

## Configuration

### 1. Clés API

**Première installation :**
1. Copiez le fichier template : `qf_gen_config/api_key.txt.example` → `qf_gen_config/api_key.txt`
2. Éditez `qf_gen_config/api_key.txt` et remplacez les placeholders par vos vraies clés :

```
OPENAI_API_KEY="sk-proj-xxxxx..."
ANTHROPIC_API_KEY="sk-ant-api03-xxxxx..."
```

**Important** :
- Conservez les guillemets autour des clés
- Le fichier `api_key.txt` est ignoré par Git pour protéger vos clés

### 2. Choix du provider et du modèle IA

Par défaut, l'application utilise **Claude** (Anthropic).

Éditez `qf_gen_config/ai_provider.txt` pour configurer le provider et les modèles :

```
PROVIDER=claude
CLAUDE_MODEL=claude-sonnet-4-5-20250929
OPENAI_MODEL=gpt-5-2025-08-07
```

**Configuration :**
- Changez `PROVIDER=claude` en `PROVIDER=openai` pour basculer
- Modifiez `CLAUDE_MODEL` pour utiliser un autre modèle Claude
- Modifiez `OPENAI_MODEL` pour utiliser un autre modèle OpenAI

**Modèles recommandés :**
- Claude : `claude-sonnet-4-5-20250929` (excellent pour les mathématiques)
- OpenAI : `gpt-5-2025-08-07` (modèle frontière)

## Fonctionnalités principales

- ✨ **Génération assistée par IA** : Création automatique de questions, réponses et corrections
- 📝 **Éditeur LaTeX** : Coloration syntaxique et vérification en temps réel
- 💾 **Base de données** : Organisation par niveau, année et mois
- 📚 **Bibliothèque de questions** : Chargement de questions existantes comme modèles
- 📄 **Compilation automatique** : Génération PDF avec LuaLaTeX
- 🎲 **Évaluations** : Création d'évaluations par sélection aléatoire sur période

## Structure des dossiers

```
NEW_QF_generator/
├── databases/          # Bases de données JSON par niveau
├── generated/          # Fichiers TEX et PDF générés
│   ├── tex/           # Sources LaTeX
│   ├── pdf/           # PDF compilés
│   ├── eval_tex/      # Évaluations LaTeX
│   └── eval_pdf/      # Évaluations PDF
├── qf_gen_config/      # Configuration (clés API, prompts)
├── latexhighlighter/   # Coloration syntaxique
└── UI_question_loader/ # Interface de chargement
```

## Documentation

Une documentation complète au format PDF est disponible dans `QFgen_doc/`.

Pour la compiler :
```bash
cd QFgen_doc
lualatex QFgen_doc.tex
```

## Tutoriels vidéo

Des tutoriels vidéo sont disponibles dans : `C:\Users\Utilisateur\Videos\Tutos`

## Support

Pour toute question ou problème, consultez la documentation ou les tutoriels vidéo.

## Modèles

- `modele_QF.tex` : Modèle pour les questions flash quotidiennes
- `Modele_QF_eval.tex` : Modèle pour les évaluations

Ces modèles peuvent être personnalisés selon vos besoins.

## Git et versionnement

### Fichiers ignorés par Git (.gitignore)

Le `.gitignore` protège automatiquement :

**Fichiers sensibles :**
- `qf_gen_config/api_key.txt` - Vos clés API (utilisez le template `.example`)
- `qf_gen_config/tcl_path.txt` - Chemin TCL spécifique à votre machine

**Fichiers de compilation LaTeX :**
- Tous les fichiers auxiliaires (`.aux`, `.log`, `.out`, `.toc`, etc.)
- Fichiers temporaires et de cache
- Fichiers spécifiques profCollege/bfcours (`.comp`, `.voc`, `.bfpoints`)

**Environnement Python :**
- `venv/` - Environnement virtuel
- `__pycache__/` - Fichiers Python compilés

**Fichiers générés :**
- Les PDFs et TEX dans `generated/` sont versionnés par défaut
- Décommentez les lignes dans `.gitignore` si vous ne voulez pas les versionner

### Premiers pas avec Git

```bash
# Initialiser le dépôt
git init

# Configurer vos clés (AVANT le premier commit)
cp qf_gen_config/api_key.txt.example qf_gen_config/api_key.txt
# Puis éditez api_key.txt avec vos vraies clés

# Premier commit
git add .
git commit -m "Initial commit: QF Generator"
```