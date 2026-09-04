@echo off
title Kohisar Model School ^& College (KMS) - Database Restore Utility
color 1F

if exist "%~dp0manage.py" (
    set "PROJECT_DIR=%~dp0"
) else (
    set "PROJECT_DIR=%cd%"
)
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
cd /d "%PROJECT_DIR%"

cls
echo ==============================================================================
echo         KOHISAR MODEL SCHOOL ^& COLLEGE - DATABASE RESTORE UTILITY
echo ==============================================================================
echo.
echo Available backup files:
if exist "%PROJECT_DIR%\kms_initial_data.json" echo   [0] kms_initial_data.json (Original system initial data)
if exist "%PROJECT_DIR%\backups\*.json" (
    dir /b "%PROJECT_DIR%\backups\*.json"
)
echo.
echo Drag and drop a backup JSON file here, or type the file name,
echo or press ENTER to load 'kms_initial_data.json':
set /p RESTORE_FILE="> "

if "%RESTORE_FILE%"=="" set "RESTORE_FILE=%PROJECT_DIR%\kms_initial_data.json"
set RESTORE_FILE=%RESTORE_FILE:"=%

if not exist "%RESTORE_FILE%" (
    if exist "%PROJECT_DIR%\backups\%RESTORE_FILE%" (
        set "RESTORE_FILE=%PROJECT_DIR%\backups\%RESTORE_FILE%"
    )
)

if not exist "%RESTORE_FILE%" (
    color 4F
    echo [ERROR] Specified file does not exist: %RESTORE_FILE%
    pause
    exit /b 1
)

echo.
echo [*] Restoring from: %RESTORE_FILE%...
"%PROJECT_DIR%\venv\Scripts\python.exe" manage.py loaddata "%RESTORE_FILE%"

if %ERRORLEVEL% equ 0 (
    color 2F
    echo.
    echo [SUCCESS] Database successfully restored from %RESTORE_FILE%!
) else (
    color 4F
    echo.
    echo [ERROR] Restore failed. Please check the error details above.
)

echo.
pause
