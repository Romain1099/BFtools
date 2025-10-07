@echo off
echo ========================================
echo  Lancement de Lottery Sessions
echo  Mode développement
echo ========================================
echo.

REM Vérifier si le venv existe
if not exist venv (
    echo ERREUR: Environnement virtuel non trouvé
    echo Exécutez d'abord : init.bat
    echo.
    pause
    exit /b 1
)

REM Activer le venv et lancer l'application
call venv\Scripts\activate.bat
python lottery_sessions.py
