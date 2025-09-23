@echo off
echo ========================================
echo    Demarrage de Prep State Analyser
echo ========================================
echo.
cd /d "C:\Users\Utilisateur\Documents\Professionnel\1. Reims 2025 - 2026\Scripts\prep_state_analyser"
echo Installation des dependances si necessaire...
call npm install --silent
echo.
echo Demarrage du serveur...
echo.
echo L'application sera disponible sur : http://localhost:3000
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo ========================================
echo.
npm start