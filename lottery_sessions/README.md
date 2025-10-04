# 🎲 Lottery Sessions - Tirage au sort avec historique

Application de tirage au sort pour la sélection d'étudiants avec suivi des sessions et notation intégrée.

## ✨ Fonctionnalités

### 🎯 Tirage au sort avancé
- **Multi-classes avec variantes** : Gérez plusieurs classes et créez des variantes (groupes TD, TP, etc.)
- **Mode avec/sans remise** : Choix du mode de tirage avec gestion intelligente
- **Mode historique** : Option pour tenir compte ou ignorer les sessions précédentes
- **Sessions indépendantes** : Chaque jour est une nouvelle session, les étudiants redeviennent disponibles
- **Animations visuelles** : Interface moderne avec animations et confettis configurables
- **Badges clignotants** : Éléments visuels colorés pendant l'animation pour plus de suspense

### 📊 Gestion des sessions
- **Historique des sessions** : Conserve l'historique complet des interrogations par date
- **Barre de progression** : Suivi en temps réel du cycle d'interrogation
- **Statistiques en direct** : Moyenne du jour, nombre d'élèves interrogés
- **Gestion des cycles** : Archivage automatique des cycles complets avec reset
- **Gestion des absents** : Statut "ABS" qui n'impacte pas la progression du cycle

### ⚙️ Notation et saisie
- **Notation intégrée** : Système de notation 0-3 points après chaque tirage
- **Bouton Absent** : Marque un étudiant absent (statut "ABS") sans perturber le cycle
- **Saisie manuelle des scores** : Modification directe des notes dans la liste des élèves
- **Interface améliorée** : Une ligne par élève avec score éditable
- **Sauvegarde automatique** : Toutes les modifications sont sauvegardées instantanément

### 🏫 Gestion des variantes de classes
- **Classe de base** : Format `classe_<nom>.csv` (ex: `classe_1ere-TC_QF.csv`)
- **Variantes** : Format `classe_<nom>_<type>.csv` (ex: `classe_1ere-TC_QF_TD1.csv`)
- **Création automatique** : Créez des variantes directement depuis l'interface
- **Affichage groupé** : Les variantes sont affichées en arborescence sous leur classe de base

### 🔧 Configuration et contrôle
- **Architecture modulaire ES6** : Code organisé en modules séparés par responsabilité
- **Configuration centralisée** : Paramètres d'animation dans `data/config.json`
- **Arrêt propre** : Bouton "Quitter l'application" pour fermeture sécurisée
- **Backups limités** : Conservation des 5 dernières sauvegardes seulement

## 🚀 Installation et utilisation

### Option 1 : Utiliser l'executable Windows (Recommandé)

1. **Générer l'executable** :
   ```cmd
   build.bat
   ```

2. **Lancer l'application** :
   - Double-cliquez sur `lottery_sessions.exe`
   - Le navigateur s'ouvre automatiquement
   - L'application est prête !

### Option 2 : Lancer avec Python

1. **Installer les dépendances** :
   ```cmd
   pip install -r requirements.txt
   ```

2. **Lancer l'application** :
   ```cmd
   python lottery_sessions.py
   ```

## 📁 Structure des fichiers

```
lottery_sessions/
├── 🚀 lottery_sessions.py     # Script principal
├── 📦 backend/                # Logique serveur
│   ├── csv_manager.py      # Gestion des fichiers CSV et variantes
│   └── session_tracker.py  # Suivi des sessions et cycles
├── 🎨 templates/              # Templates HTML
│   └── index.html          # Interface utilisateur
├── 🌎 static/                 # Fichiers statiques
│   ├── styles.css          # Styles CSS
│   ├── main.js             # Point d'entrée ES6
│   ├── animations.js       # Animations
│   └── modules/            # Architecture modulaire ES6
│       ├── state.js        # Gestion de l'état et localStorage
│       ├── api.js          # Client API REST
│       ├── ui.js           # Interface utilisateur
│       ├── classes.js      # Gestion des classes et variantes
│       ├── students.js     # Gestion des étudiants
│       ├── draw.js         # Logique de tirage
│       ├── scoring.js      # Notation et absences
│       ├── cycles.js       # Gestion des cycles
│       └── utils.js        # Fonctions utilitaires
├── 📁 data/                   # Dossier des classes CSV ET configuration
│   ├── classe_1ere-TC_QF.csv           # Classe de base
│   ├── classe_1ere-TC_QF_TD1.csv       # Variante TD1
│   ├── classe_1ere-TC_QF_TD2.csv       # Variante TD2
│   ├── config.json                     # Configuration (animations)
│   ├── backups/                        # Sauvegardes automatiques (5 max)
│   └── cycles/                         # Cycles archivés
│       └── classe_1ere-TC_QF_24-09_03-10.csv
└── 🏃 lottery_sessions.exe    # Executable généré

```

## 📋 Format des fichiers CSV

### Structure avec historique
```csv
nom;prenom;2024-10-01;2024-10-02;2024-10-03
Dupont;Jean;2;ABS;1
Martin;Marie;;0;3
Durand;Paul;1;;
```

- **Colonnes fixes** : `nom` et `prenom`
- **Colonnes dates** : Ajoutées automatiquement (format YYYY-MM-DD)
- **Valeurs de score** :
  - `0` : Réponse erronée / Refus de répondre
  - `1` : Réponse partielle
  - `2` : Réponse correcte
  - `3` : Réponse excellente (optionnel)
  - `ABS` : Étudiant absent (ne compte pas dans le cycle)
  - *(vide)* : Non interrogé

### Variantes de classes
Les variantes partagent les mêmes étudiants (nom/prénom) mais ont des historiques séparés :
- **Base** : `classe_1ere-TC_QF.csv` (nom, prenom uniquement)
- **Variante TD1** : `classe_1ere-TC_QF_TD1.csv` (historique TD1)
- **Variante TD2** : `classe_1ere-TC_QF_TD2.csv` (historique TD2)

## 🎯 Utilisation

### Premier lancement

1. **Sélection de classe** :
   - Au démarrage, sélectionnez une classe existante
   - Ou créez une nouvelle classe
   - Ou importez un fichier CSV

2. **Interface principale** :
   - La liste des élèves s'affiche dans la sidebar (une ligne par élève)
   - Les élèves déjà interrogés sont indiqués visuellement (fond orange)
   - Score du jour modifiable directement à côté du nom

### Effectuer un tirage

1. **Configurer les paramètres** :
   - Mode avec/sans remise
   - Nombre d'élèves à tirer (1-4)
   - Mode historique (on/off)

2. **Lancer le tirage** :
   - Cliquez sur "🎲 Tirage au sort"
   - L'animation de mélange démarre
   - Les gagnants sont sélectionnés

3. **Noter les élèves** :
   - **Panel de notation** : Apparaît automatiquement après le tirage
   - **Scores disponibles** : 0 (erreur), 1 (partiel), 2 (correct), 3 (excellent)
   - **Bouton Absent** : Marque l'étudiant absent (statut "ABS")
   - **Bouton Passer** : Passe au suivant sans noter (étudiant reste disponible)
   - **Notation manuelle** : Modifiez directement les scores dans la liste des élèves
   - **Sauvegarde instantanée** : Tous les scores sont automatiquement sauvegardés
   - **Statistiques mises à jour** : Moyenne et progression actualisées en temps réel

### Gestion des classes et variantes

- **Changer de classe** : Cliquez sur 🔄 dans la sidebar
- **Créer une classe** : Via le sélecteur de classes
- **Importer un CSV** : Format `nom;prenom` supporté
- **Créer une variante** :
  - Cliquez sur le bouton ➕ à côté d'une classe de base
  - Entrez le nom de la variante (ex: TD1, groupe1, TP2)
  - La variante est créée avec les mêmes étudiants mais un historique vierge
  - Si la classe de base n'existe pas, elle est créée automatiquement

### Modes de fonctionnement

#### Mode sans remise (par défaut)
- Les élèves tirés et notés sont décochés automatiquement
- Ils ne peuvent pas être tirés à nouveau **dans la même session (jour)**
- Le lendemain, tous les étudiants redeviennent disponibles

#### Mode avec remise
- Les élèves restent disponibles après le tirage
- Possibilité d'interroger plusieurs fois le même élève **dans la même session**
- Même avec remise, chaque jour est une nouvelle session

#### Sessions indépendantes
- **Chaque jour = nouvelle session** : Les étudiants notés ou absents un jour redeviennent disponibles le lendemain
- **Statut ABS** : Les absents ne comptent pas dans la progression du cycle
- **Réutilisation** : Un étudiant absent le 01/10 peut être interrogé le 02/10

#### Gestion des cycles
- Le cycle continue jusqu'à ce que tous les élèves aient été interrogés au moins une fois avec un **score réel (0-3)**
- **Les absences (ABS) ne comptent pas** dans la progression du cycle
- Quand tous les élèves ont été interrogés, un bouton "🔄 Nouveau cycle" apparaît
- **Archive automatique** : Le cycle est archivé dans `data/cycles/classe_<nom>_<dateDebut>_<dateFin>.csv`
- **Reset du CSV** : La classe active est nettoyée (garde uniquement nom/prenom)
- Tous les étudiants redeviennent disponibles pour un nouveau cycle complet

## 🔧 Configuration avancée

### Fichier de configuration `data/config.json`
Personnalisez tous les paramètres d'animation dans un seul fichier :

```json
{
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
```

### Bouton Quitter
- **Arrêt sécurisé** : Bouton "Quitter l'application" dans la sidebar
- **Confirmation** : Demande de confirmation avant fermeture
- **Page d'arrêt** : Message de confirmation après arrêt du serveur

### Personnalisation des styles
Éditez `static/styles.css` pour modifier :
- Couleurs des animations (orange par défaut)
- Polices et tailles
- Effets visuels

## 📊 Sauvegarde et backup

- **Sauvegarde automatique** : Après chaque modification
- **Backups optimisés** : Dans `data/backups/` (5 dernières versions conservées)
- **Export manuel** : Copier directement le fichier CSV
- **Configuration portable** : Tout dans le dossier `data/` pour faciliter le transport

## ⚠️ Notes importantes

- **Compatibilité** : Windows 10/11 (Chrome, Edge, Firefox)
- **Port** : L'application trouve automatiquement un port libre
- **Données** : Les fichiers CSV et configuration sont dans `data/`
- **Sécurité** : Application locale uniquement (pas d'accès réseau)

## 🐛 Résolution des problèmes

### L'executable ne se lance pas
- Vérifiez que l'antivirus ne bloque pas l'application
- Lancez en tant qu'administrateur si nécessaire
- Créez le dossier `data/` manuellement si nécessaire

### Le navigateur ne s'ouvre pas
- Ouvrez manuellement : `http://localhost:PORT`
- Le port s'affiche dans la console au démarrage

### Erreur de chargement des classes
- Vérifiez le format des fichiers CSV (`nom;prenom`)
- Assurez-vous que le dossier `data/` existe
- Le fichier `config.json` sera créé automatiquement au premier lancement

### L'application ne se ferme pas
- Utilisez le bouton "Quitter l'application" dans la sidebar
- En cas de problème : fermez la fenêtre de console (Ctrl+C)

### Les variantes ne s'affichent pas
- Vérifiez que le nom suit le format `classe_<nom>_<type>.csv`
- La classe de base sera créée automatiquement si elle n'existe pas
- Rechargez la page après création d'une variante

## 📝 Licence

Utilisation libre pour un usage éducatif.

## 🤝 Support

Pour toute question ou problème, consultez le rapport d'expertise dans le dossier parent.