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
set BACKUP_FILE=%PROJECT_DIR%\backups\kms_backup_%TIMESTAMP%.json

echo ==============================================================================
echo         KOHISAR MODEL SCHOOL ^& COLLEGE - DATABASE BACKUP UTILITY
echo ==============================================================================
echo.
echo [*] Backing up KMS database...
echo [*] Destination: %BACKUP_FILE%
echo.

"%PROJECT_DIR%\venv\Scripts\python.exe" manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 -o "%BACKUP_FILE%"

if %ERRORLEVEL% equ 0 (
    color 2F
    echo [SUCCESS] Backup created successfully!
    echo File: %BACKUP_FILE%
) else (
    color 4F
    echo [ERROR] Backup failed. Please ensure virtual environment and database are active.
)

echo.
echo ==============================================================================
pause
