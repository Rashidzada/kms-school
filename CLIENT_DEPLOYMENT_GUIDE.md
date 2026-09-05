# Kohisar Model School & College (KMS) - Client Deployment & Handover Guide

> **System Name:** Student Information, Fee & Payroll Management System (KMS)  
> **Institution:** Kohisar Model School & College, Qalagay, Swat  
> **Database:** PostgreSQL 18 (`kms_db`)  
> **Web Framework:** Django 6.1.1 (Python 3.11 - 3.14 compatible)  
> **Default Port:** `8000` (`http://127.0.0.1:8000/`)

---

## 1. What to Give / Send to the Client (Package Contents)

When handing over the software to the client, place the following contents inside a clean folder (e.g. named `KMS_Software`) and zip it (or copy via USB drive).

### Files and Folders to Include:
```text
KMS_Software/
│
├── kms_setup.bat             <-- ONE-CLICK AUTOMATED INSTALLER FOR CLIENT
├── kms_run.bat               <-- ONE-CLICK DAILY APPLICATION RUNNER
├── kms_backup.bat            <-- ONE-CLICK INSTANT DATABASE BACKUP TOOL
├── kms_restore.bat           <-- ONE-CLICK INSTANT DATABASE RESTORATION TOOL
├── create_shortcut.ps1       <-- DESKTOP SHORTCUT HELPER SCRIPT
├── init_db.py                <-- AUTOMATIC POSTGRESQL DATABASE INITIALIZER
│
├── kms_initial_data.json     <-- COMPLETE INITIAL SCHOOL DATA (Classes, Sections,
│                                 Teachers, Scales, Students, Ledgers, Receipts, Expenses)
├── kms_db_backup.sql         <-- POSTGRESQL SQL ENGINE DUMP BACKUP
├── requirements.txt          <-- PYTHON DEPENDENCY MANIFEST
├── manage.py                 <-- DJANGO SYSTEM CONTROLLER
│
├── school/                   <-- School info, classes, sections, sessions, subjects
├── students/                 <-- Student admission, family links, status tracking
├── teachers/                 <-- Teacher registry, designations, credentials
├── finance/                  <-- Pay scales, salary generation, fee ledgers, receipts
├── accounts/                 <-- Authentication, user roles & permissions
├── school_app/               <-- Central project settings & routing
├── templates/                <-- Bootstrap 5 responsive UI templates
├── static/                   <-- CSS, JavaScript, Kohisar emblem/assets
└── media/                    <-- Uploaded files & school logo
```

### Files and Folders to EXCLUDE (Do NOT Send):
1. **`venv/` folder:** **DO NOT** copy the virtual environment folder. Virtual environments contain absolute hardcoded file paths tied to your specific Windows user profile. The client's `kms_setup.bat` will automatically build a 100% clean, native virtual environment on their machine in less than 60 seconds!
2. **`.git/` folder:** Exclude to keep your Git version control history private and save download size.
3. **`__pycache__/` folders:** Automatically regenerated cache files.
4. **`*.log` files:** Local debug logs.

---

## 2. Software Prerequisites (What to Install FIRST on Client PC)

Before running the KMS software for the first time on the client computer, install these two free prerequisites:

### Prerequisite 1: Python (Version 3.11, 3.12, 3.13, or 3.14)
1. Download Python for Windows from the official website:
   👉 **[https://www.python.org/downloads/](https://www.python.org/downloads/)**
2. Run the downloaded installer.
3. **CRITICAL STEP (Do NOT skip):**
   At the very first screen of the installer, **CHECK THE BOX** that says:
   `[x] Add python.exe to PATH` (or `Add Python to environment variables`).
4. Click **"Install Now"** and wait for it to finish.

### Prerequisite 2: PostgreSQL Database Engine (Version 15, 16, 17, or 18)
1. Download the official PostgreSQL Windows installer from EnterpriseDB:
   👉 **[https://www.enterprisedb.com/downloads/postgres-postgresql-downloads](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)**
2. Run the installer and click **Next** through the setup steps.
3. When prompted to set a password for the superuser (`postgres`):
   - Enter password: `postgres`
   - Retype password: `postgres`
   *(If the client chooses a different password, see Section 7 below to update `settings.py`).*
4. Keep the default port as `5432`.
5. Keep default locale and complete the installation.

### Prerequisite 3: Modern Web Browser
- Google Chrome, Microsoft Edge, Mozilla Firefox, or Brave.

---

## 3. Where to Place the Software on the Client PC

### Recommended Location:
Extract or copy the folder to the root of a permanent drive, such as:
- `C:\KMS_Software`  
  *or*
- `D:\KMS_Software`

### Why this location is recommended:
- Avoids Windows User Profile path limits (e.g. `C:\Users\username\...`).
- Prevents accidental deletion when clearing desktop files or Downloads.
- Provides standard administrative permissions.
- Note: The setup script will automatically create a desktop shortcut, so users will never need to navigate into `C:\KMS_Software` manually.

---

## 4. Step-by-Step Client Setup (One-Click Automated Setup)

1. Open the software folder: `C:\KMS_Software`
2. Right-click **`kms_setup.bat`** and click **Run as administrator** (or simply double-click).
3. The wizard will automatically execute all 6 installation steps:
   - **Step 1:** Verifies Python is installed and configured in PATH.
   - **Step 2:** Checks and starts the PostgreSQL database service.
   - **Step 3:** Creates an isolated virtual environment (`venv`) and installs required packages (`Django`, `psycopg`, `crispy-bootstrap5`, `Pillow`).
   - **Step 4:** Automatically connects to PostgreSQL and creates the `kms_db` database if it does not already exist.
   - **Step 5:** Applies database schema migrations and loads all Kohisar Model School initial data, classes, sections, teacher registers, fee structures, and financial ledgers.
   - **Step 6:** Creates a convenient **"Kohisar Model School (KMS)"** shortcut on the Windows Desktop.
4. When prompted: `Would you like to start Kohisar Model School System now? (Y/N):`, type `Y` and press Enter!

---

## 5. Daily Operation: How to Run the Software with One Click

Every day when school staff want to use the system:

1. **Double-click** the **`Kohisar Model School (KMS)`** shortcut on the Desktop.  
   *(Or double-click `kms_run.bat` inside the folder).*
2. The launcher will automatically:
   - Verify that PostgreSQL is running (and start it automatically if stopped).
   - Free Port 8000 if previously bound.
   - Automatically open Google Chrome / Edge to:
     **`http://127.0.0.1:8000/`**
3. **Login Details:**
   - **Username:** `admin`
   - **Password:** `admin123`
4. **To close the software:** Simply close the black terminal window when done for the day.

---

## 6. One-Click Database Backup & Restore

### Taking an Instant Backup (`kms_backup.bat`):
- Double-click **`kms_backup.bat`**.
- It will create a complete snapshot of all school data inside `backups/` folder with an exact timestamp:
  e.g. `backups/kms_backup_2026-09-04_120000.json`.
- **Recommendation:** Keep a regular copy of the `backups/` folder on an external USB flash drive or Google Drive.

### Restoring from a Backup (`kms_restore.bat`):
- Double-click **`kms_restore.bat`**.
- It displays all available backup files.
- Press `Enter` to restore the original baseline data (`kms_initial_data.json`), or drag-and-drop any timestamped backup file to restore it instantly!

---

## 7. Multi-PC School Network Access (LAN Setup)

If Kohisar Model School wants other computers in the school (e.g. Principal Office, Accounts Office, Reception Desk) to access the system:

1. Find the IP address of the main computer running the server:
   - Open Command Prompt and type: `ipconfig`
   - Look for IPv4 Address (e.g. `192.168.1.50`).
2. In `kms_run.bat`, change:
   `manage.py runserver 127.0.0.1:8000`
   to:
   `manage.py runserver 0.0.0.0:8000`
3. In `school_app/settings.py`, ensure:
   `ALLOWED_HOSTS = ['*']`
4. Other staff members on the school Wi-Fi or LAN cable can access the system by opening their browser and going to:
   `http://192.168.1.50:8000/`

---

## 8. Common Troubleshooting & FAQs

| Issue / Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **`python is not recognized as an internal or external command`** | Python was installed without the PATH environment variable. | Re-run the Python installer, select **Modify**, and make sure **"Add python.exe to PATH"** is checked. Restart the computer. |
| **`Could not connect to PostgreSQL server`** | PostgreSQL service is stopped or port is blocked. | Open Windows Start menu, search for **Services**, locate **postgresql-x64-XX**, right click, and select **Start**. |
| **`Password authentication failed for user postgres`** | Client typed a different password during PostgreSQL installation. | Open `school_app/settings.py`, locate `DATABASES['default']['PASSWORD']`, change `'postgres'` to the custom password used during install, and save. |
| **`Port 8000 is already in use`** | A previous instance is still running. | Double-click `kms_run.bat`. It has built-in auto-kill logic that detects and frees port 8000 automatically. |
| **Web page shows `This site can't be reached`** | Server window was closed. | Double-click the Desktop shortcut `Kohisar Model School (KMS)` to restart the server. |
