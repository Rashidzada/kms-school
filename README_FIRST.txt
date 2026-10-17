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
5. DYNAMIC SCHOOL RE-BRANDING & WHITE-LABELING (FOR ANY SCHOOL)
--------------------------------------------------------------------------------
  * To use this software for Kohisar Model School or ANY OTHER SCHOOL:
    Go to 'Settings' (top right / sidebar).
  * You can change:
    - School Full Name (e.g. Govt High School Qalagay, Army Public School, etc.)
    - Short Name / Code (e.g. KMS, GHSQ, BPS)
    - School Logo (JPG/PNG - automatically resizes and updates everywhere)
    - Subtitle / Tagline
    - Campus Address & Contact Numbers
  * When updated, the entire system (admin panel, header, sidebar, ID badges,
    DMC result cards, fee vouchers, registers, tab titles, and favicons)
    updates instantly with ZERO hardcoded references!

--------------------------------------------------------------------------------
6. AUTOMATIC OFFLINE BACKUP (SAFE HARD DRIVE / USB) & CLOUD
--------------------------------------------------------------------------------
  * Configurable Safe Folder: In 'Settings', choose any safe drive (e.g. D:\School_Backups,
    E:\School_Backups, or external drive).
  * Dual Preservation: Every backup generates both a complete PostgreSQL dump (.sql)
    and a 16-Sheet Master Excel workbook (.xlsx).
  * Auto Day Timer & Scheduled Time: Set backup frequency (e.g. 1 Day) and daily run time.
  * Choose Behavior Mode:
    - Silent Background: Backs up quietly with no interruption or screen freeze.
    - Prompt First: Shows a non-intrusive reminder (Run Now / Later).
    - Progress Modal: Shows full step-by-step progress popup.
  * Cloud Email: Optional Gmail SMTP or Cloud HTTPS Email (Port 443) backup delivery.
  * 1-Click Full Restore: In Settings, upload any .sql or .xlsx file to restore 100% data.

--------------------------------------------------------------------------------
7. MASTER SCHOOL & TEACHER TIMETABLE (PINK & GREEN BOARDS)
--------------------------------------------------------------------------------
  * Exact Digital Replicas:
    - Primary Wing (Pink Board): Nursery, Prep, 1st, 2nd, 3rd, 4th, 5th.
    - Middle, High & College (Green Board): 6th, 7th, 8th, 9th, 10th, 1st Year, 2nd Year.
    - 8 Periods structure with break interval (Periods 01-05, Break, Periods 06-08).
  * Double-Booking / Clash Detection:
    - System instantly flags any teacher scheduled in 2 or more classes during the same period.
    - Real-time warning badge and clash summary cards.
  * 1-Page Landscape Office Printer Layout:
    - Formatted for standard A4 landscape school printing with header, dynamic logo, and signatures.
  * Interactive Assignments:
    - Click any cell to assign or change teacher/subject with instant conflict checking.
    - Click any teacher name to filter their individual schedule and view free periods.

--------------------------------------------------------------------------------
8. STUDENT EXAM FEE & COLLECTION REGISTER
--------------------------------------------------------------------------------
  * Simple Student List & Fee Register:
    - Go to 'Examinations' -> 'Exam Fee Collection List'.
    - Filter by Class, Section, and Session.
    - Displays: S#, Admission No, Student Name, Father Name, Class & Section,
      Payable Exam Fee, Paid Amount, Balance Due, and Signature block.
  * Office Printer Ready (Portrait) & 1-Click Excel Export for staff.
================================================================================

