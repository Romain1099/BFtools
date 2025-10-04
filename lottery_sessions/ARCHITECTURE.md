# Architecture Modulaire - Lottery Sessions

## 📋 Vue d'ensemble

L'application a été refactorisée pour suivre une **architecture modulaire par responsabilité**. Chaque module gère une partie spécifique de l'application, facilitant la maintenance, les tests et l'évolution du code.

## 🏗️ Structure du projet

```
lottery_sessions/
├── backend/                    # Backend Python
│   ├── csv_manager.py         # Gestion des fichiers CSV
│   └── session_tracker.py     # Suivi des sessions
├── static/                     # Frontend JavaScript
│   ├── modules/               # Modules ES6
│   │   ├── state.js          # État global + localStorage
│   │   ├── api.js            # Client API REST
│   │   ├── ui.js             # Manipulation DOM
│   │   ├── utils.js          # Utilitaires
│   │   ├── students.js       # Logique étudiants
│   │   ├── classes.js        # Logique classes
│   │   ├── cycles.js         # Logique cycles
│   │   ├── scoring.js        # Logique notation
│   │   └── draw.js           # Logique tirage
│   ├── main.js               # Point d'entrée
│   ├── animations.js         # Animations (legacy)
│   └── styles.css            # Styles CSS
├── templates/
│   └── index.html            # Template HTML
└── lottery_sessions.py       # Serveur Flask
```

## 📦 Description des modules

### 1. **state.js** - Gestion de l'état
- **Responsabilité** : État global de l'application
- **Exports** :
  - `CONFIG` : Configuration runtime (classe, étudiants, modes...)
  - `state` : État du tirage (isDrawing, gameState...)
  - `Storage` : Gestion du localStorage

**Exemple** :
```javascript
import { CONFIG, Storage } from './modules/state.js';

CONFIG.currentClass = 'classe_6A';
Storage.saveLastClass('classe_6A');
```

### 2. **api.js** - Client API
- **Responsabilité** : Communication avec le backend Flask
- **Méthodes** :
  - `getClasses()`, `createClass()`, `importClass()`
  - `getStudents()`, `updateScore()`
  - `getCycleProgress()`, `resetCycle()`
  - `recordDraw()`, `shutdown()`

**Exemple** :
```javascript
import { API } from './modules/api.js';

const data = await API.getStudents('classe_6A');
await API.updateScore('classe_6A', 'Dupont Jean', 2, '2025-10-03');
```

### 3. **ui.js** - Interface utilisateur
- **Responsabilité** : Manipulation du DOM et affichage
- **Méthodes** :
  - `showLoading()`, `showError()`, `showNotification()`
  - `showModal()`, `hideModal()`
  - `updateSessionStats()`, `updateCycleProgress()`
  - `showScoringPanel()`, `toggleSidebar()`

**Exemple** :
```javascript
import { UI } from './modules/ui.js';

UI.showLoading(true);
UI.showNotification('Cycle terminé !');
UI.updateSessionStats(15, 25, 2.3);
```

### 4. **utils.js** - Utilitaires
- **Responsabilité** : Fonctions réutilisables
- **Fonctions** :
  - `formatDate()` : Formate une date
  - `getRandomPosition()` : Position aléatoire pour les badges
  - `isDateField()` : Vérifie si un champ est une date
  - `getCurrentCycleFields()` : Récupère les dates du cycle actuel
  - `hasBeenQuestionedInCycle()` : Vérifie si un élève a été interrogé

### 5. **students.js** - Gestion des étudiants
- **Responsabilité** : Logique métier des étudiants
- **Méthodes** :
  - `load()` : Charge les étudiants depuis l'API
  - `display()` : Affiche la liste dans la sidebar
  - `updateStats()` : Calcule les statistiques
  - `getChecked()` : Retourne les étudiants cochés
  - `selectAll()`, `deselectAll()`

### 6. **classes.js** - Gestion des classes
- **Responsabilité** : CRUD des classes
- **Méthodes** :
  - `load()` : Charge toutes les classes
  - `select()` : Sélectionne une classe
  - `create()` : Crée une nouvelle classe
  - `import()` : Importe depuis CSV
  - `display()` : Affiche le sélecteur

### 7. **cycles.js** - Gestion des cycles
- **Responsabilité** : Logique des cycles d'interrogation
- **Méthodes** :
  - `updateProgress()` : Met à jour la progression
  - `reset()` : Démarre un nouveau cycle

### 8. **scoring.js** - Notation
- **Responsabilité** : Noter les étudiants après tirage
- **Méthodes** :
  - `handleScore()` : Enregistre une note
  - `skip()` : Passe la notation
  - `showPanel()`, `hidePanel()`

### 9. **draw.js** - Tirage au sort
- **Responsabilité** : Logique de tirage et affichage badges
- **Exports** :
  - `Display` : Gestion des badges visuels
    - `updateTags()` : Met à jour l'affichage
    - `checkDrawButton()` : État du bouton
  - `Draw` : Logique de tirage
    - `perform()` : Lance le tirage
    - `selectWinners()` : Sélectionne les gagnants

### 10. **main.js** - Point d'entrée
- **Responsabilité** : Initialisation et orchestration
- **Fonctions** :
  - `initializeApp()` : Démarre l'application
  - `setupEventListeners()` : Configure tous les listeners
  - Event handlers globaux

## 🔄 Flux de données

### Chargement initial
```
main.js
  ↓
initializeApp()
  ↓
Classes.load() → API.getClasses()
  ↓
Classes.select() → Students.load() → API.getStudents()
  ↓
Display.updateTags() + Cycles.updateProgress()
```

### Tirage au sort
```
Draw.perform()
  ↓
startShuffleAnimation() (animations.js)
  ↓
Draw.selectWinners()
  ↓
API.recordDraw() + animateWinners()
  ↓
Cycles.updateProgress()
  ↓
Scoring.showPanel()
```

### Notation
```
Scoring.handleScore()
  ↓
API.updateScore()
  ↓
Students.load() + Cycles.updateProgress()
  ↓
Display.updateTags()
```

## 🔌 Events personnalisés

L'application utilise des events pour la communication inter-modules :

```javascript
// Déclenché quand les checkboxes changent
window.dispatchEvent(new CustomEvent('students-checked-changed'));

// Déclenché quand une classe est sélectionnée
window.dispatchEvent(new CustomEvent('class-selected'));
```

## 💾 LocalStorage

Gestion centralisée dans `state.js` :

```javascript
Storage.saveLastClass('classe_6A');        // Sauvegarde la classe
Storage.getLastClass();                     // Récupère la classe
Storage.saveHistoryMode(true);              // Mode historique
Storage.getHistoryMode();                   // Récupère le mode
```

## 🎯 Avantages de cette architecture

1. **Séparation des responsabilités** : Chaque module a un rôle clair
2. **Réutilisabilité** : Les modules sont indépendants et réutilisables
3. **Testabilité** : Facile de tester chaque module isolément
4. **Maintenabilité** : Modifications localisées, pas d'effet de bord
5. **Évolutivité** : Ajout de fonctionnalités sans casser l'existant
6. **Lisibilité** : Code organisé et facile à comprendre

## 🚀 Migration depuis l'ancienne version

### Avant (app.js monolithique)
```javascript
// Tout dans un seul fichier
async function loadStudents() { /* ... */ }
async function performDraw() { /* ... */ }
function updateDisplay() { /* ... */ }
// 1000+ lignes...
```

### Après (modulaire)
```javascript
// Modules séparés
import { Students } from './modules/students.js';
import { Draw } from './modules/draw.js';

await Students.load(className);
await Draw.perform();
```

## 📝 Bonnes pratiques

1. **Imports explicites** : Toujours importer ce dont on a besoin
2. **Pas de variables globales** : Utiliser les exports de modules
3. **Async/Await** : Pour toutes les opérations asynchrones
4. **Error handling** : Try/catch dans chaque module
5. **Events** : Pour la communication inter-modules

## 🔧 Développement

### Ajouter un nouveau module

1. Créer le fichier dans `static/modules/`
2. Définir les exports
3. L'importer dans `main.js` ou autre module
4. Mettre à jour cette documentation

### Déboguer

- Ouvrir la console du navigateur
- Les modules sont sourcemappés
- Logs explicites dans chaque module

## 🐛 Fix du bug de rechargement

**Problème** : "Impossible de charger les étudiants" au reload

**Solution** : localStorage + auto-sélection
```javascript
// Dans Classes.load()
const lastClass = Storage.getLastClass();
if (lastClass && data.classes.includes(lastClass)) {
    await this.select(lastClass);
}
```

La classe sélectionnée est maintenant **persistée** entre les rechargements.
