@echo off
echo ========================================
echo  Initialisation du projet
echo  Lottery Sessions
echo ========================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installé ou n'est pas dans le PATH
    echo Installez Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Créer le venv s'il n'existe pas
if not exist venv (
    echo [1/2] Creation de l'environnement virtuel...
    python -m venv venv
    echo.
) else (
    echo [1/2] Environnement virtuel existant détecté
    echo.
)

REM Activer le venv et installer les dépendances
echo [2/2] Installation des dépendances...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo ========================================
echo  Initialisation terminée avec succès !
echo ========================================
echo.
echo Pour lancer l'application:
echo   - Mode développement : run.bat
echo   - Build executable   : build.bat
echo.
pause
