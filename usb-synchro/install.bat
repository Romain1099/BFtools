@echo off
echo Installation du programme de synchronisation USB...
echo.

REM Vérification de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installé ou pas dans le PATH
    echo Veuillez installer Python depuis https://www.python.org/
    pause
    exit /b 1
)

echo Python détecté.
echo.

REM Création de l'environnement virtuel
echo Création de l'environnement virtuel...
if exist "venv" (
    echo L'environnement virtuel existe déjà.
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERREUR: Échec de la création de l'environnement virtuel
        pause
        exit /b 1
    )
    echo Environnement virtuel créé.
)

echo.
echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo Mise à jour de pip...
python -m pip install --upgrade pip

echo Installation des dépendances...
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERREUR: Échec de l'installation des dépendances
    pause
    exit /b 1
)

echo.
echo ✅ Installation terminée avec succès!
echo.
echo Pour lancer le programme, exécutez:
echo    run.bat
echo.
pause