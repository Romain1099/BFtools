@echo off
setlocal

:: Vérifier si le venv existe
if not exist "venv\Scripts\activate.bat" (
    echo [ERREUR] Environnement virtuel non trouve!
    echo.
    echo Veuillez d'abord executer init.bat pour installer l'application.
    echo.
    pause
    exit /b 1
)

:: Activer le venv et lancer main.py
call venv\Scripts\activate.bat
python main.py

:: Désactiver le venv à la fin
deactivate
