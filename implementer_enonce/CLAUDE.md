# Implementer Enonce - Documentation pour Claude

## Vue d'ensemble
Application Python avec interface graphique (CustomTkinter) pour générer et gérer des exercices mathématiques en LaTeX avec variations automatiques et abstraction d'exercices via IA.

## Architecture principale

### Point d'entrée
- `modules/UI_v2.py` : Interface graphique principale avec classe `ExerciseEditor`
- `main.py` : Fichier de lancement alternatif qui appelle UI_v2.py

### Modules principaux

#### `modules/UI_v2.py`
Classe `ExerciseEditor` (hérite de ctk.CTk) qui :
- Gère l'interface avec menubar (15%) et tabview (85%)
- Onglets : Variables, Énoncé, Solution détaillée, Réponse courte, Version QCM, Version html, Thème
- Charge/sauvegarde les modèles d'exercices (format .sty avec séparateurs %%)
- Intègre l'abstraction IA via `AbstractExoUI`
- Export en formats .sty et .json

#### `modules/version_maker.py`
- `create_questions()` : Parse le format %% et génère les variations
- `make_json_UI()` : Export JSON pour QF_generator
- Types de questions : SHORT, HELP, FULL, QCM
- Gère la création de multiples versions avec variables aléatoires

#### `modules/numbers_def.py`
- `create_random_variable()` : Génère des valeurs aléatoires selon contraintes
- Parse les définitions LaTeX : `\def\n{2<=x<20 int}`
- Support types : int, float, frac, listes [option1,option2,...]
- Gestion des exclusions (x!=6) et décimales (decimalesD7)

#### `modules/number_generators_manager.py`
- `NumberGeneratorManager` : Gestionnaire centralisé des générateurs
- Chargement dynamique depuis `modules/number_generators/`
- Types : EXONUMBER, ARITHMETICNUMBER (extensible)
- Génération avec contraintes complexes

#### Modules d'abstraction
- `abstractor/abstract_exo_ui.py` : Interface pour abstraire un exercice
- `abstractor/question_abstractor.py` : Appel IA (GPT-4) pour l'abstraction

#### Modules externes intégrés
- `QF_generator/latexhighlighter/` : Coloration syntaxique LaTeX
- Widget `LatexText` pour édition avec coloration

## Format des fichiers .sty

Structure avec séparateurs `%%` :
```
nombre_versions
%%
variables_definitions
%%
enonce
%%
solution_detaillee
%%
version_qcm
%%
reponse_courte
%%
theme
%%
html (optionnel)
```

## Workflow principal

1. **Création/Chargement** :
   - Charger modèle existant (.sty) ou créer nouveau
   - Abstraire via IA un exercice collé

2. **Édition** :
   - Définir variables avec contraintes
   - Éditer énoncé, solutions, QCM
   - Prévisualisation avec coloration LaTeX

3. **Export** :
   - Génération N versions avec valeurs aléatoires
   - Export .sty dans `inputs/niveau/theme/`
   - Export .json dans `json_productions/`

## Syntaxe des variables

```latex
\def\n{2<=x<20 int}              # Entier entre 2 et 19
\def\d{1<=x<=5 float decimalesD2} # Float avec 2 décimales
\def\frac{1<x<=10 x!=0 frac}     # Fraction
\def\list[option1,option2,option3] # Liste de choix
ArithmeticNumber(...)             # Générateur personnalisé
```

## Structure des dossiers
- `inputs/` : Modèles organisés par niveau/thème
- `productions/` : Fichiers LaTeX générés
- `json_productions/` : Exports JSON pour QF
- `modules/` : Code source principal
- `modules/number_generators/` : Générateurs de nombres
- `abstractor/` : Module d'abstraction IA

## Installation
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement
```bash
python modules/UI_v2.py
```

## Dépendances principales
- `customtkinter` : Interface graphique moderne
- `openai` : API GPT-4 pour abstraction (dans enonce_implementator.py)
- Python 64 bits avec tkinter
- TCL/TK configuré (ligne 6 de UI_v2.py)

## Notes importantes
- Le système génère des exercices paramétrables multi-versions
- Format .sty personnalisé avec séparateurs %%
- Support LaTeX avec commandes ProfCollege
- Abstraction IA pour transformer exercices bruts en modèles
- Générateurs de nombres extensibles dynamiquement