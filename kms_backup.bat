@echo off
title Kohisar Model School ^& College (KMS) - Database Backup Utility
color 1F

if exist "%~dp0manage.py" (
    set "PROJECT_DIR=%~dp0"
) else (
    set "PROJECT_DIR=%cd%"
)
if "%PROJECT_DIR:~-1%"=="\" set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
cd /d "%PROJECT_DIR%"

if not exist "%PROJECT_DIR%\backups" mkdir "%PROJECT_DIR%\backups"

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%%datetime:~10,2%%datetime:~12,2%
set SQL_FILE=%PROJECT_DIR%\backups\KMS_Full_Backup_%TIMESTAMP%.sql
set XLSX_FILE=%PROJECT_DIR%\backups\KMS_Full_Master_Backup_%TIMESTAMP%.xlsx
set JSON_FILE=%PROJECT_DIR%\backups\kms_backup_%TIMESTAMP%.json

echo ==============================================================================
echo         KOHISAR MODEL SCHOOL ^& COLLEGE - FULL DATABASE BACKUP UTILITY
echo ==============================================================================
echo.
echo [*] Backing up 100%% of KMS database (SQL + Master Excel + JSON)...
echo.

"%PROJECT_DIR%\venv\Scripts\python.exe" -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_app.settings'); django.setup(); from school.backup_utils import generate_full_sql_dump, generate_full_master_excel; open(r'%SQL_FILE%', 'wb').write(generate_full_sql_dump()); open(r'%XLSX_FILE%', 'wb').write(generate_full_master_excel().getvalue())"
"%PROJECT_DIR%\venv\Scripts\python.exe" manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission -e admin.logentry -e sessions.session --indent 2 -o "%JSON_FILE%"

if %ERRORLEVEL% equ 0 (
    color 2F
    echo [SUCCESS] Full Backup created successfully!
    echo   1. PostgreSQL Dump : %SQL_FILE%
    echo   2. Master Excel    : %XLSX_FILE%
    echo   3. Django JSON     : %JSON_FILE%
) else (
    color 4F
    echo [ERROR] Backup failed. Please ensure virtual environment and database are active.
)

echo.
echo ==============================================================================
pause
