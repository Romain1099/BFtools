@echo off
echo Lancement du programme de synchronisation USB...

REM Activation de l'environnement virtuel
call venv\Scripts\activate.bat

REM Lancement du programme
python main.py

pause