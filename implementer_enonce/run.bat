@echo off
setlocal

echo ========================================
echo   Lancement de l'application
echo ========================================
echo.

REM Vérifier que le venv existe
if not exist "venv\Scripts\activate.bat" (
    echo ERREUR: Environnement virtuel non trouve.
    echo Veuillez d'abord executer init.bat
    echo.
    pause
    exit /b 1
)

REM Vérifier que le fichier TCL path existe
if not exist ".tcl_path.txt" (
    echo ERREUR: Fichier .tcl_path.txt non trouve.
    echo Veuillez d'abord executer init.bat
    echo.
    pause
    exit /b 1
)

REM Activer le venv
echo [1/2] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo    ^[OK^] Venv active
echo.

REM Lancer l'application
echo [2/2] Lancement de l'interface graphique...
python modules\UI_v2.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERREUR: L'application s'est terminee avec une erreur.
    echo.
    pause
)

exit /b 0
