@echo off
setlocal enabledelayedexpansion

echo ===============================================
echo  Detection de Python avec support TCL/Tkinter
echo ===============================================
echo.

:: Créer le dossier de config s'il n'existe pas
if not exist "qf_gen_config" mkdir qf_gen_config

:: Variables
set "VALID_PYTHON="
set "TCL_PATH="
set "VENV_DIR=venv"

:: Chercher toutes les installations Python
echo Recherche des installations Python...
echo.

:: Méthode 1: Utiliser py launcher (recommandé)
py -0 >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Python Launcher detecte
    for /f "tokens=2 delims= " %%v in ('py -0 2^>^&1 ^| findstr /r "^[ ]*-[0-9]"') do (
        call :check_python_version "py %%v"
        if defined VALID_PYTHON goto :found
    )
)

:: Méthode 2: Chercher python.exe dans le PATH
echo [INFO] Recherche dans le PATH...
for %%p in (python.exe) do (
    if exist "%%~$PATH:p" (
        call :check_python_version "%%~$PATH:p"
        if defined VALID_PYTHON goto :found
    )
)

:: Méthode 3: Chercher dans les emplacements standards
echo [INFO] Recherche dans les emplacements standards...

:: Recherche dans %LOCALAPPDATA%\Programs\Python
if exist "%LOCALAPPDATA%\Programs\Python" (
    for /d %%p in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%p\python.exe" (
            call :check_python_version "%%p\python.exe"
            if defined VALID_PYTHON goto :found
        )
    )
)

:: Recherche dans %PROGRAMFILES%\Python
if exist "%PROGRAMFILES%\Python" (
    for /d %%p in ("%PROGRAMFILES%\Python\Python*") do (
        if exist "%%p\python.exe" (
            call :check_python_version "%%p\python.exe"
            if defined VALID_PYTHON goto :found
        )
    )
)

:: Recherche dans Program Files (x86)\Python
set "PFX86=%ProgramFiles(x86)%"
if exist "%PFX86%\Python" (
    for /d %%p in ("%PFX86%\Python\Python*") do (
        if exist "%%p\python.exe" (
            call :check_python_version "%%p\python.exe"
            if defined VALID_PYTHON goto :found
        )
    )
)

:: Recherche dans C:\Python
if exist "C:\Python" (
    for /d %%p in ("C:\Python\Python*") do (
        if exist "%%p\python.exe" (
            call :check_python_version "%%p\python.exe"
            if defined VALID_PYTHON goto :found
        )
    )
)

:: Aucune version valide trouvée
echo.
echo [ERREUR] Aucune installation Python avec support TCL/Tkinter trouvee!
echo.
echo Veuillez installer Python avec tkinter inclus:
echo - Telechargez depuis https://www.python.org/downloads/
echo - Lors de l'installation, assurez-vous que "tcl/tk and IDLE" est coche
echo.
pause
exit /b 1

:found
echo.
echo ===============================================
echo  Python valide trouve!
echo ===============================================
echo Python: %VALID_PYTHON%
echo TCL_LIBRARY: %TCL_PATH%
echo.

:: Sauvegarder le chemin TCL dans le fichier de config
echo %TCL_PATH% > "qf_gen_config\tcl_path.txt"
echo [OK] Chemin TCL sauvegarde dans qf_gen_config\tcl_path.txt
echo.

:: Créer le venv
echo ===============================================
echo  Creation de l'environnement virtuel
echo ===============================================

if exist "%VENV_DIR%" (
    echo [INFO] Environnement virtuel existant trouve
    choice /C YN /M "Voulez-vous le supprimer et recreer"
    if errorlevel 2 goto :skip_venv
    if errorlevel 1 (
        echo [INFO] Suppression de l'ancien venv...
        rmdir /s /q "%VENV_DIR%"
    )
)

echo [INFO] Creation du venv avec %VALID_PYTHON%...
%VALID_PYTHON% -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de la creation du venv
    pause
    exit /b 1
)
echo [OK] Venv cree avec succes
echo.

:skip_venv
:: Activer le venv et installer les dépendances
if exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ===============================================
    echo  Installation des dependances
    echo ===============================================
    call "%VENV_DIR%\Scripts\activate.bat"

    if exist "requirements.txt" (
        echo [INFO] Installation depuis requirements.txt...
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        if %errorlevel% equ 0 (
            echo [OK] Dependances installees avec succes
        ) else (
            echo [ATTENTION] Erreurs lors de l'installation des dependances
        )
    ) else (
        echo [ATTENTION] requirements.txt non trouve
    )
    echo.
)

echo ===============================================
echo  Installation terminee!
echo ===============================================
echo.
echo Pour utiliser l'application:
echo   1. Activez le venv: %VENV_DIR%\Scripts\activate.bat
echo   2. Lancez: python main.py
echo.
pause
exit /b 0

:: ==========================================
:: Fonction pour vérifier une version Python
:: ==========================================
:check_python_version
set "PYTHON_CMD=%~1"
echo [TEST] Verification de %PYTHON_CMD%...

:: Tester si Python fonctionne
%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ECHEC] Python ne fonctionne pas
    goto :eof
)

:: Obtenir la version
for /f "tokens=2" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set "PY_VERSION=%%v"
echo   Version: %PY_VERSION%

:: Tester tkinter
%PYTHON_CMD% -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ECHEC] tkinter non disponible
    goto :eof
)
echo   [OK] tkinter disponible

:: Obtenir le chemin TCL_LIBRARY
for /f "delims=" %%t in ('%PYTHON_CMD% -c "import tkinter; import os; tcl_path = os.path.join(os.path.dirname(os.path.dirname(tkinter.__file__)), 'tcl'); dirs = os.listdir(tcl_path) if os.path.exists(tcl_path) else []; tcl_ver = [d for d in dirs if d.startswith('tcl8')]; print(os.path.join(tcl_path, tcl_ver[0]) if tcl_ver else '')" 2^>nul') do set "TEST_TCL_PATH=%%t"

if defined TEST_TCL_PATH (
    if exist "!TEST_TCL_PATH!" (
        echo   [OK] TCL_LIBRARY trouve: !TEST_TCL_PATH!
        set "VALID_PYTHON=%PYTHON_CMD%"
        set "TCL_PATH=!TEST_TCL_PATH!"
        goto :eof
    )
)

:: Chercher alternativement dans le répertoire Python
for /f "delims=" %%t in ('%PYTHON_CMD% -c "import sys; import os; print(os.path.join(sys.prefix, 'tcl'))" 2^>nul') do set "ALT_TCL_BASE=%%t"

if exist "!ALT_TCL_BASE!" (
    for /d %%d in ("!ALT_TCL_BASE!\tcl8*") do (
        echo   [OK] TCL_LIBRARY trouve: %%d
        set "VALID_PYTHON=%PYTHON_CMD%"
        set "TCL_PATH=%%d"
        goto :eof
    )
)

echo   [ECHEC] TCL_LIBRARY non trouve
goto :eof
