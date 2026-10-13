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
echo Available backup files (.sql, .xlsx, .json):
if exist "%PROJECT_DIR%\kms_initial_data.json" echo   [0] kms_initial_data.json (Original system initial data)
if exist "%PROJECT_DIR%\backups\*.*" (
    dir /b "%PROJECT_DIR%\backups\*.sql" "%PROJECT_DIR%\backups\*.xlsx" "%PROJECT_DIR%\backups\*.json" 2>nul
)
echo.
echo Drag and drop a backup file (.sql, .xlsx, or .json) here, or type the file name,
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
for %%F in ("%RESTORE_FILE%") do set "EXT=%%~xF"

if /I "%EXT%"==".sql" (
    "%PROJECT_DIR%\venv\Scripts\python.exe" -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_app.settings'); django.setup(); from school.backup_utils import restore_from_sql_bytes; ok, msg = restore_from_sql_bytes(open(r'%RESTORE_FILE%', 'rb').read()); print(msg); exit(0 if ok else 1)"
) else if /I "%EXT%"==".xlsx" (
    "%PROJECT_DIR%\venv\Scripts\python.exe" -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_app.settings'); django.setup(); from school.backup_utils import restore_from_master_excel; ok, msg = restore_from_master_excel(open(r'%RESTORE_FILE%', 'rb')); print(msg); exit(0 if ok else 1)"
) else (
    "%PROJECT_DIR%\venv\Scripts\python.exe" manage.py loaddata "%RESTORE_FILE%"
)

if %ERRORLEVEL% equ 0 (
    "%PROJECT_DIR%\venv\Scripts\python.exe" "%PROJECT_DIR%\init_db.py" --sync-sequences
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
