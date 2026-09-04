@echo off
title Kohisar Model School ^& College (KMS) - Automated Setup Wizard
color 1F

:: Determine Project Directory (Portable detection)
if exist "%~dp0manage.py" (
    set "PROJECT_DIR=%~dp0"
) else (
    set "PROJECT_DIR=%cd%"
)

:: Remove trailing slash if present
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo           KOHISAR MODEL SCHOOL ^& COLLEGE - QALAGAY SWAT
echo     Automated Client Setup ^& Installation Wizard for KMS Software
echo ==============================================================================
echo.
echo [*] Installation Folder: %PROJECT_DIR%
echo.

:: -----------------------------------------------------------------------------
:: STEP 1: Verify Python Installation
:: -----------------------------------------------------------------------------
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 goto :ERR_NO_PYTHON

for /f "tokens=*" %%v in ('python --version') do set "PY_VER=%%v"
echo     [OK] Found %PY_VER%
echo.

:: -----------------------------------------------------------------------------
:: STEP 2: Verify PostgreSQL Service
:: -----------------------------------------------------------------------------
echo [2/6] Checking PostgreSQL Database Service...
sc query postgresql-x64-18 | find "RUNNING" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo     [OK] PostgreSQL Service [v18] is running.
) else (
    sc query postgresql | find "RUNNING" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo     [OK] PostgreSQL Service is running.
    ) else (
        echo     [*] Attempting to start PostgreSQL Service...
        net start postgresql-x64-18 >nul 2>&1 || net start postgresql >nul 2>&1
        if %ERRORLEVEL% equ 0 (
            echo     [OK] PostgreSQL Service started successfully.
        ) else (
            echo     [NOTE] If PostgreSQL runs under a different service name or port,
            echo            ensure it is started via Windows Services [services.msc].
        )
    )
)
echo.

:: -----------------------------------------------------------------------------
:: STEP 3: Setup Virtual Environment & Install Dependencies
:: -----------------------------------------------------------------------------
echo [3/6] Setting up Python Virtual Environment [venv]...
if not exist "%PROJECT_DIR%\venv\Scripts\python.exe" (
    echo     [*] Creating isolated Python virtual environment...
    python -m venv "%PROJECT_DIR%\venv"
    if %ERRORLEVEL% neq 0 (
        color 4F
        echo     [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo     [OK] Virtual environment created.
) else (
    echo     [OK] Virtual environment already exists.
)

echo     [*] Installing/Verifying required packages [Django, psycopg, crispy-forms, Pillow]...
"%PROJECT_DIR%\venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
"%PROJECT_DIR%\venv\Scripts\python.exe" -m pip install -r "%PROJECT_DIR%\requirements.txt"
if %ERRORLEVEL% neq 0 (
    color 4F
    echo     [ERROR] Package installation failed. Check internet connection or requirements.txt.
    pause
    exit /b 1
)
echo     [OK] All Python dependencies are installed and up to date.
echo.

:: -----------------------------------------------------------------------------
:: STEP 4: Initialize PostgreSQL Database (kms_db)
:: -----------------------------------------------------------------------------
echo [4/6] Initializing PostgreSQL database 'kms_db'...
"%PROJECT_DIR%\venv\Scripts\python.exe" "%PROJECT_DIR%\init_db.py"
if %ERRORLEVEL% neq 0 (
    color 4F
    echo.
    echo     [ERROR] Database initialization failed.
    echo     Please make sure PostgreSQL is running with user 'postgres' and password 'postgres'.
    pause
    exit /b 1
)
echo.

:: -----------------------------------------------------------------------------
:: STEP 5: Apply Migrations & Seed Initial Data
:: -----------------------------------------------------------------------------
echo [5/6] Applying database migrations and seeding initial data...
"%PROJECT_DIR%\venv\Scripts\python.exe" "%PROJECT_DIR%\manage.py" migrate --noinput
if %ERRORLEVEL% neq 0 (
    color 4F
    echo     [ERROR] Migration failed. Check settings and database connection.
    pause
    exit /b 1
)
echo     [OK] Database schema up to date.

if exist "%PROJECT_DIR%\kms_initial_data.json" (
    echo     [*] Loading complete Kohisar Model School data ^& configuration...
    "%PROJECT_DIR%\venv\Scripts\python.exe" "%PROJECT_DIR%\manage.py" loaddata "%PROJECT_DIR%\kms_initial_data.json" >nul 2>&1
    echo     [OK] School data, classes, teachers, and records loaded successfully.
) else (
    echo     [*] Ensuring default superuser exists...
    "%PROJECT_DIR%\venv\Scripts\python.exe" "%PROJECT_DIR%\init_db.py" --create-superuser
)
echo.

:: -----------------------------------------------------------------------------
:: STEP 6: Create Desktop Shortcut
:: -----------------------------------------------------------------------------
echo [6/6] Creating Desktop Shortcut...
if exist "%PROJECT_DIR%\create_shortcut.ps1" (
    powershell -ExecutionPolicy Bypass -File "%PROJECT_DIR%\create_shortcut.ps1" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo     [OK] Shortcut "Kohisar Model School (KMS)" created on your Desktop!
    ) else (
        echo     [NOTE] Could not automatically create desktop shortcut. You can double click 'kms_run.bat'.
    )
) else (
    echo     [NOTE] Shortcut script not found. You can double click 'kms_run.bat'.
)
echo.

:: -----------------------------------------------------------------------------
:: COMPLETE
:: -----------------------------------------------------------------------------
cls
color 2F
echo ==============================================================================
echo                      INSTALLATION COMPLETED SUCCESSFULLY!
echo ==============================================================================
echo.
echo    Kohisar Model School ^& College (KMS) System is fully configured!
echo.
echo    PORTAL URL:       http://127.0.0.1:8001/
echo    ADMIN USERNAME:   admin
echo    ADMIN PASSWORD:   admin123
echo.
echo    To launch the software daily, simply double-click the shortcut:
echo    'Kohisar Model School (KMS)' on your Desktop, or run 'kms_run.bat'.
echo ==============================================================================
echo.
set /p LAUNCH="Would you like to start Kohisar Model School System now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    call "%PROJECT_DIR%\kms_run.bat"
) else (
    echo.
    echo Setup is finished. You can run the application anytime using kms_run.bat!
    pause
)
exit /b 0

:ERR_NO_PYTHON
color 4F
echo.
echo ==============================================================================
echo [ERROR] Python is NOT detected in your system PATH!
echo ==============================================================================
echo.
echo Please follow these simple steps to install Python:
echo  1. Download Python [version 3.11, 3.12, 3.13, or 3.14] from:
echo     https://www.python.org/downloads/
echo  2. Run the installer and CRITICAL:
echo     [*] CHECK the box 'Add python.exe to PATH' at the bottom of the installer!
echo  3. Complete installation, close this window, and run 'kms_setup.bat' again.
echo.
echo ==============================================================================
pause
exit /b 1
