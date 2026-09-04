@echo off
title Kohisar Model School ^& College (KMS) - Server Runner
color 1F

:: Determine Project Directory (Portable detection)
set "PROJECT_DIR="
if exist "%~dp0manage.py" set "PROJECT_DIR=%~dp0"
if not defined PROJECT_DIR if exist "%cd%\manage.py" set "PROJECT_DIR=%cd%"
if not defined PROJECT_DIR if exist "C:\Users\RashidZada\Desktop\Django-School-Management-System\manage.py" set "PROJECT_DIR=C:\Users\RashidZada\Desktop\Django-School-Management-System"
if not defined PROJECT_DIR if exist "C:\kms-school\manage.py" set "PROJECT_DIR=C:\kms-school"
if not defined PROJECT_DIR if exist "C:\KMS_Software\manage.py" set "PROJECT_DIR=C:\KMS_Software"
if not defined PROJECT_DIR set "PROJECT_DIR=%~dp0"

:: Remove trailing slash if present
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"

cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo           KOHISAR MODEL SCHOOL ^& COLLEGE - QALAGAY SWAT
echo      Student Information, Fee ^& Payroll Management System (KMS)
echo ==============================================================================
echo.
echo [*] Location: %PROJECT_DIR%
echo.

:: 1. Check PostgreSQL Service
echo [*] Checking PostgreSQL Database Service...
sc query postgresql-x64-18 | find "RUNNING" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo     [OK] PostgreSQL Service is running.
) else (
    sc query postgresql | find "RUNNING" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo     [OK] PostgreSQL Service is running.
    ) else (
        echo     [!] Starting PostgreSQL Service...
        net start postgresql-x64-18 >nul 2>&1 || net start postgresql >nul 2>&1
        if %ERRORLEVEL% equ 0 (
            echo     [OK] PostgreSQL Service started successfully.
        ) else (
            echo     [WARNING] Could not start service directly. If permissions are needed,
            echo               ensure PostgreSQL is started via Windows Services.
        )
    )
)
echo.

:: 2. Check Virtual Environment
echo [*] Checking Python Virtual Environment...
if not exist "%PROJECT_DIR%\venv\Scripts\python.exe" (
    color 4F
    echo     [ERROR] Virtual environment python.exe not found in:
    echo             %PROJECT_DIR%\venv\Scripts\python.exe
    echo.
    echo     Please run 'kms_setup.bat' first to initialize the environment.
    echo.
    pause
    exit /b 1
)
echo     [OK] Virtual Environment ready.
echo.

:: 3. Check Port 8001 & Free if Stale Process Exists
echo [*] Preparing Port 8001 for KMS Web Portal...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo     [!] Freeing existing process on port 8001 [PID: %%a]...
    taskkill /F /PID %%a >nul 2>&1
)
echo     [OK] Port 8001 is ready.
echo.

:: 4. Launch Browser Automatically (Delayed by 2 seconds)
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8001/"

:: 5. Display Portal Details
echo ==============================================================================
echo    APPLICATION LAUNCHED SUCCESSFULLY
echo ==============================================================================
echo.
echo    URL:              http://127.0.0.1:8001/
echo    Admin Username:   admin
echo    Admin Password:   admin123
echo    Database Engine:  PostgreSQL (kms_db)
echo.
echo    [NOTE] Keep this terminal window open while using the software.
echo           To stop the server, press CTRL+C or close this window.
echo ==============================================================================
echo.

:: 6. Run Django Development Server
"%PROJECT_DIR%\venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8001

if %ERRORLEVEL% neq 0 (
    color 4F
    echo.
    echo [ERROR] The server stopped unexpectedly.
    pause
)
