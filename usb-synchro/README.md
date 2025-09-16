Ce répertoire contient une petite application de synchronisation de ressources sur clé USB à destination d'enseignants. 

# Installation 

- Cliquer sur le fichier : @install.bat

L'installation s'effectue automatiquement pour peu que vous ayez une installation python. 

# Fonctionnement 

1. Lancer ou double cliquer sur le script "run.bat" ou "SyncUSB.bat"
2. Insérer votre clé USB et s'assurer qu'elle est bien détectée par l'application. 
3. Mettre la clé USB par défaut. 
4. Cliquer sur l'onglet 'Sync UP' et configurer le mapping : Dosser sur l'ordinateur -> dossier sur clé USB.
5. Personnaliser les formats de fichiers désirés ou non. 

Le mapping est sauvegardé et sera retrouvé à chaque synchronisation. 

# Quelques détails

Le programme fonctionne ainsi : 

Ayant connaissance des fichiers à déplacer vers la clé USB, le programme analyse par date de modification les fichiers sur votre ordinateur. 
Il analyse ensuite le répertoire de destination sur la clé USB et compare les dates de modification des documents déjà présents. 
Il copie / colle ensuite les documents qui ne sont pas à jour sur votre clé USB ( écrase le contenu remplacé sur la clé USB ). 