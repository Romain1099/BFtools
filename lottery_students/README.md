# 🎲 Lottery Sessions - Tirage au sort avec historique

Application de tirage au sort pour la sélection d'étudiants avec suivi des sessions et notation intégrée.

## ✨ Fonctionnalités

### 🎯 Tirage au sort avancé
- **Multi-classes** : Gérez plusieurs classes simultanément
- **Mode avec/sans remise** : Choix du mode de tirage avec gestion intelligente
- **Mode historique** : Option pour tenir compte ou ignorer les sessions précédentes
- **Animations visuelles** : Interface moderne avec animations et confettis configurables
- **Badges clignotants** : Éléments visuels colorés pendant l'animation pour plus de suspense

### 📊 Gestion des sessions
- **Historique des sessions** : Conserve l'historique complet des interrogations par date
- **Barre de progression** : Suivi en temps réel du cycle d'interrogation
- **Statistiques en direct** : Moyenne du jour, nombre d'élèves interrogés
- **Gestion des cycles** : Démarrage automatique de nouveaux cycles

### ⚙️ Notation et saisie
- **Notation intégrée** : Système de notation 0-3 points après chaque tirage
- **Saisie manuelle des scores** : Modification directe des notes dans la liste des élèves
- **Interface améliorée** : Une ligne par élève avec score éditable
- **Sauvegarde automatique** : Toutes les modifications sont sauvegardées instantanément

### 🔧 Configuration et contrôle
- **Configuration centralisée** : Paramètres d'animation et heartbeat dans un fichier JSON
- **Arrêt propre** : Bouton "Quitter l'application" pour fermeture sécurisée
- **Heartbeat configurable** : Contrôle fin de l'arrêt automatique du serveur
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
   cd repertoire\du\programme
   python lottery_sessions.py
   ```

## 📁 Structure des fichiers

```
lottery_sessions/
├── 🚀 lottery_sessions.py     # Script principal
├── 📦 backend/                # Logique serveur
│   ├── csv_manager.py      # Gestion des fichiers CSV
│   └── session_tracker.py  # Suivi des sessions
├── 🎨 templates/              # Templates HTML
│   └── index.html          # Interface utilisateur
├── 🌎 static/                 # Fichiers statiques
│   ├── styles.css          # Styles CSS
│   ├── app.js              # Logique JavaScript
│   └── animations.js       # Animations
├── 📁 data/                   # Dossier des classes CSV ET configuration
│   ├── classe_template.csv       # Exemple de classe
│   ├── config.json         # Configuration (animations, heartbeat)
│   └── backups/            # Sauvegardes automatiques (5 max)
└── 🏃 lottery_sessions.exe    # Executable généré

```

## 📋 Format des fichiers CSV

### Structure avec historique
```csv
nom;prenom;2024-01-15;2024-01-22;2024-01-29
Dupont;Jean;2;;1
Martin;Marie;;0;3
```

- **Colonnes fixes** : `nom` et `prenom`
- **Colonnes dates** : Ajoutées automatiquement (format YYYY-MM-DD)
- **Valeurs de score** :
  - `0` : Réponse erronée / Refus de répondre
  - `1` : Réponse partielle
  - `2` : Réponse correcte
  - `3` : Réponse excellente (optionnel)
  - *(vide)* : Non interrogé

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
   - **Notation automatique** : Après le tirage, le panel de notation apparaît
   - **Notation manuelle** : Modifiez directement les scores dans la liste des élèves
   - **Sauvegarde instantanée** : Tous les scores sont automatiquement sauvegardés
   - **Statistiques mises à jour** : Moyenne et progression actualisées en temps réel

### Gestion des classes

- **Changer de classe** : Cliquez sur 🔄 dans la sidebar
- **Créer une classe** : Via le sélecteur de classes
- **Importer un CSV** : Format `nom;prenom` supporté

### Modes de fonctionnement

#### Mode sans remise (par défaut)
- Les élèves tirés sont décochés automatiquement
- Ils ne peuvent pas être tirés à nouveau dans la même session

#### Mode avec remise
- Les élèves restent disponibles après le tirage
- Possibilité d'interroger plusieurs fois le même élève

#### Mode cycle complet
- **Activé** : Exclut les élèves déjà interrogés depuis le début du cycle
- **Désactivé** : Tous les élèves sont disponibles (ignore l'historique)

#### Gestion des cycles
- Le cycle continue jusqu'à ce que tous les élèves aient été interrogés au moins une fois
- Quand tous les élèves ont été interrogés, un bouton "🔄 Nouveau cycle" apparaît
- Cliquer sur ce bouton remet tout le monde disponible pour un nouveau cycle
- L'historique complet est conservé dans le CSV

## 🔧 Configuration avancée

### Fichier de configuration `data/config.json`
Personnalisez tous les paramètres dans un seul fichier :

```json
{
  "heartbeat": {
    "intervalMs": 5000,     // Fréquence du heartbeat (ms)
    "timeoutMs": 10000,     // Délai avant arrêt auto (ms)
    "checkIntervalMs": 2000 // Fréquence de vérification (ms)
  },
  "animation": {
    "shuffle": {
      "maxShuffles": 6,        // Nombre de mélanges
      "movementDuration": 800,  // Durée des mouvements (ms)
      "delayMin": 450          // Délai minimum entre mélanges
    },
    "highlight": {
      "maxRounds": 4,          // Nombre de tours de clignotement
      "delayMin": 400          // Délai minimum entre clignotements
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
- Le port s'affiche dans la console
- Heartbeat configuré toutes les 5 secondes par défaut

### Erreur de chargement des classes
- Vérifiez le format des fichiers CSV (`nom;prenom`)
- Assurez-vous que le dossier `data/` existe
- Le fichier `config.json` sera créé automatiquement au premier lancement

### L'application ne se ferme pas
- Utilisez le bouton "Quitter l'application" dans la sidebar
- Ou fermez la page web (arrêt automatique en 10 secondes)
- En cas de problème : Ctrl+C dans la console

## 📝 Licence

Utilisation libre pour un usage éducatif.

## 🤝 Support

Pour toute question ou problème, consultez le rapport d'expertise dans le dossier parent.