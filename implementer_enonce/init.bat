@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Initialisation de l'environnement
echo ========================================
echo.

REM Recherche des installations Python
echo [1/5] Recherche des installations Python avec TCL/TK...
set PYTHON_FOUND=0
set PYTHON_PATH=
set TCL_PATH=

REM Essayer les emplacements courants de Python
for %%V in (311 310 312 39 38) do (
    set "TEST_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python%%V\python.exe"
    if exist "!TEST_PATH!" (
        echo    - Test: !TEST_PATH!

        REM Vérifier si TCL existe pour cette version
        set "TCL_TEST=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python%%V\tcl\tcl8.6"
        if exist "!TCL_TEST!" (
            echo      ^[OK^] TCL/TK trouve : !TCL_TEST!
            set PYTHON_PATH=!TEST_PATH!
            set TCL_PATH=!TCL_TEST!
            set PYTHON_FOUND=1
            goto :found_python
        ) else (
            echo      ^[X^] TCL/TK non trouve
        )
    )
)

REM Essayer python depuis PATH
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%i in ('where python') do (
        set "TEST_PATH=%%i"
        echo    - Test: !TEST_PATH!

        REM Extraire le dossier racine de Python
        for %%A in ("!TEST_PATH!") do set "PYTHON_DIR=%%~dpA"
        set "TCL_TEST=!PYTHON_DIR!tcl\tcl8.6"

        if exist "!TCL_TEST!" (
            echo      ^[OK^] TCL/TK trouve : !TCL_TEST!
            set PYTHON_PATH=!TEST_PATH!
            set TCL_PATH=!TCL_TEST!
            set PYTHON_FOUND=1
            goto :found_python
        ) else (
            echo      ^[X^] TCL/TK non trouve
        )
    )
)

:found_python
if %PYTHON_FOUND% EQU 0 (
    echo.
    echo ERREUR: Aucune installation Python avec TCL/TK trouvee.
    echo Veuillez installer Python avec support TCL/TK.
    pause
    exit /b 1
)

echo.
echo Python trouve : %PYTHON_PATH%
echo TCL trouve    : %TCL_PATH%
echo.

REM Sauvegarder le chemin TCL
echo [2/5] Sauvegarde du chemin TCL...
echo %TCL_PATH%> .tcl_path.txt
echo    ^[OK^] Chemin sauvegarde dans .tcl_path.txt
echo.

REM Créer le venv
echo [3/5] Creation de l'environnement virtuel...
if exist "venv\" (
    echo    Le dossier venv existe deja. Suppression...
    rmdir /s /q venv
)

"%PYTHON_PATH%" -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Echec de creation du venv
    pause
    exit /b 1
)
echo    ^[OK^] Venv cree avec succes
echo.

REM Activer le venv et installer les dépendances
echo [4/5] Activation du venv...
call venv\Scripts\activate.bat
echo    ^[OK^] Venv active
echo.

echo [5/5] Installation des dependances...
if exist "requirements.txt" (
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ERREUR: Echec d'installation des dependances
        pause
        exit /b 1
    )
    echo    ^[OK^] Dependances installees
) else (
    echo    ^[!^] Fichier requirements.txt non trouve
)

echo.
echo ========================================
echo   Initialisation terminee avec succes!
echo ========================================
echo.
echo Vous pouvez maintenant lancer run.bat
echo.
pause
