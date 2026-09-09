================================================================================
       KOHISAR MODEL SCHOOL & COLLEGE (KMS) - SOFTWARE HANDOVER PACKAGE
================================================================================

Welcome to the Kohisar Model School & College Management System!
This software contains all modules for:
  * Student Admissions & Registration
  * Fee Management & Monthly Fee Ledgers
  * Teacher Registry & Payroll Processing
  * Examination Management, Marks Grid, Award Sheets & Result Lists
  * Examination Roll Number Slips & Admit Cards (Bulk & Individual)
  * Blank Handwriting Marks Sheets for Teachers
  * Excel Import & Export with Duplicate Prevention

--------------------------------------------------------------------------------
1. QUICK INSTALLATION (FOR NEW COMPUTERS)
--------------------------------------------------------------------------------
Before starting, ensure the computer has:
  A. Python 3.11, 3.12, 3.13 or 3.14 (Download: https://www.python.org/downloads/)
     IMPORTANT: Make sure to CHECK the box 'Add python.exe to PATH' during installation!
  B. PostgreSQL Database (Download: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
     Default password during setup: postgres

To install KMS software:
  1. Extract this zip archive to C:\KMS_Software (or any folder of your choice).
  2. Double-click 'kms_setup.bat'.
  3. The wizard will automatically set up the environment, database, and create a
     'Kohisar Model School (KMS)' shortcut directly on your Desktop!

--------------------------------------------------------------------------------
2. DAILY OPERATION (HOW TO LAUNCH)
--------------------------------------------------------------------------------
  * Simply double-click the 'Kohisar Model School (KMS)' shortcut on your Desktop,
    OR double-click 'kms_run.bat' inside the software folder.
  * Your web browser will open automatically to:
    http://127.0.0.1:8000/

--------------------------------------------------------------------------------
3. DEFAULT LOGIN CREDENTIALS
--------------------------------------------------------------------------------
  * Web Portal: http://127.0.0.1:8000/
  * Username:   admin
  * Password:   admin123

--------------------------------------------------------------------------------
4. NEW EXAMINATION & ROLL NUMBER SLIP FEATURES
--------------------------------------------------------------------------------
  * Roll Number Slips:
    Go to 'Examinations' -> 'Roll Number Slips'. You can print for the FULL SCHOOL
    (all classes at once) or select any specific class. Each card includes candidate
    photo box, circular school logo, date sheet, and examination hall rules.
  * Enter Marks Grid:
    Go to 'Examinations' -> 'Enter Marks Grid' to enter multi-subject marks in a live
    spreadsheet, or upload filled Excel sheets with automatic duplicate prevention.
  * Master Class Result Sheet:
    Format matching official school result lists with Positions (1st, 2nd, 3rd),
    Grand Total, %age, Board Grades, and print/excel export.
  * Blank Marks Collection Sheet:
    Print clean sheets with no dashes for teachers to write paper marks by hand.

--------------------------------------------------------------------------------
5. BACKUP & SAFETY
--------------------------------------------------------------------------------
  * To take a backup anytime, simply double-click 'kms_backup.bat'.
  * Backups are automatically saved with date & time inside the 'backups/' folder.
================================================================================
