# Dev README - SyncUSB

## Lancement rapide avec .bat

### Utilisation simple
1. Copiez `SyncUSB.bat` sur votre bureau
2. Double-cliquez pour lancer l'application
3. Le .bat active automatiquement l'environnement virtuel et lance le programme

## Construction d'un exécutable OnFile (optionnel)

### Commande automatique
```bash
python build_onefile.py
```

### Commande manuelle avec PyInstaller
```bash
# Installation de PyInstaller
python -m pip install pyinstaller

# Construction de l'exécutable onefile
pyinstaller --onefile --windowed --name=SyncUSB --add-data=src;src --hidden-import=customtkinter --hidden-import=psutil --hidden-import=PIL --distpath=dist --workpath=build main.py
```

### Résultat OnFile
- L'exécutable sera créé dans `dist/SyncUSB.exe`
- Taille approximative: 20-30MB (inclut Python et toutes les dépendances)
- Portable: peut être exécuté sur n'importe quel PC Windows sans installation

### Options de construction avancées

#### Avec icône personnalisée
```bash
pyinstaller --onefile --windowed --name=SyncUSB --icon=icon.ico --add-data=src;src --hidden-import=customtkinter --hidden-import=psutil --hidden-import=PIL main.py
```

#### Mode debug (console visible)
```bash
pyinstaller --onefile --console --name=SyncUSB-debug --add-data=src;src --hidden-import=customtkinter --hidden-import=psutil --hidden-import=PIL main.py
```

### Dépannage

#### Modules manquants
Si l'exécutable plante au démarrage, ajoutez le module manquant:
```bash
--hidden-import=module_name
```

#### Taille de l'exécutable
Pour réduire la taille, utilisez:
```bash
--exclude-module=module_inutile
```

#### Optimisation UPX (optionnel)
```bash
# Installation d'UPX
# Télécharger depuis https://upx.github.io/
pyinstaller --onefile --upx-dir=C:\path\to\upx --windowed --name=SyncUSB main.py
```

### Tests recommandés
1. Tester l'exécutable sur une machine sans Python
2. Vérifier la détection USB
3. Tester la synchronisation sur différents types de clés USB
4. Contrôler les performances (temps de démarrage)