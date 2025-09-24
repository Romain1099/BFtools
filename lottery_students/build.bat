@echo off
echo ========================================
echo  Building Lottery Sessions Executable
echo ========================================
echo.

REM Installer les dépendances
echo [1/3] Installation des dépendances...
pip install -r requirements.txt

REM Nettoyer les anciens builds
echo [2/3] Nettoyage des anciens builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist lottery_sessions.exe del lottery_sessions.exe

REM Compiler avec PyInstaller
echo [3/3] Compilation avec PyInstaller...
pyinstaller lottery_sessions.spec

REM Copier l'executable à la racine
if exist dist\lottery_sessions.exe (
    copy dist\lottery_sessions.exe .
    echo.
    echo ========================================
    echo  Build terminé avec succès !
    echo  Executable : lottery_sessions.exe
    echo ========================================
) else (
    echo.
    echo ========================================
    echo  ERREUR : La compilation a échoué
    echo ========================================
)

pause