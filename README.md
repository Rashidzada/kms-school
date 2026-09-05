# kms-school — Kohisar Model School & College (KMS) ERP System

[![Institution](https://img.shields.io/badge/Institution-Kohisar%20Model%20School%20%26%20College-1a365d.svg)](http://127.0.0.1:8000/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](http://127.0.0.1:8000/)
[![Engine](https://img.shields.io/badge/Database-PostgreSQL%2018-blue.svg)](https://www.postgresql.org/)

A comprehensive, production-grade **Student Information, Fee Ledger, Payroll & Accounts ERP System** custom-engineered for **Kohisar Model School & College, Qalagay, Swat** according to the 26-page Institutional Software Requirements Specification (SRS v1.0).

---

## 🏛️ System Features & Core Modules

### 1. 🎓 Student Information & Admissions (`students`)
- **Sequential Admission Engine:** Auto-incrementing admission IDs starting at `1001`.
- **Family / Household Grouping:** Multi-sibling linkages under unified parent accounts (`FAM-0001`).
- **Official Print Registers:** Formatted, print-ready Admission Register and Withdrawal Register.
- **Academic Promotion Workflow:** Single-student promotion and bulk multi-select promotion across academic sessions.
- **Formal Withdrawal Workflow:** Status freezing and automated stoppage of future fee charges.
- **Printable Certificates:** Official School Leaving Certificate (SLC) and Character Certificate with institutional seal and authorized signatures.

### 2. 👨‍🏫 Faculty & Payroll Management (`teachers`)
- **Staff Registry:** Faculty profiles, credentials, academic designations, and pay scale assignment.
- **Pay Scale Matrix:** Configurable Basic Pay, Medical Allowance, Conveyance Allowance, and Adhoc Relief.
- **Batch Salary Generation:** One-click monthly payroll generation across all active staff.
- **Salary Slips & Disbursements:** Per-staff printable Salary Slip, Experience Certificate, and Staff ID Cards.

### 3. 💳 12-Month Fee Ledgers & Financial Collection (`finance`)
- **Automated 12-Month Ledgers:** Calendar year billing (Jan–Dec) pro-rated for mid-session admissions.
- **Interactive School-Wide Fee Grid:** Matrix overview of all classes, sections, and monthly fee statuses.
- **Atomic Receipting & Allocation:** Payments applied strictly to oldest unpaid months first with automated receipt generation (`REC-1001`...).
- **Family Lump-Sum Payments:** Single combined receipt for siblings enrolled in different classes.
- **Fee Reports:** Defaulters List, Family Dues Summary, and Class-Wise Collection Summary.

### 4. 📊 Cashbook & Institutional Accounting (`accounts`)
- **Unified Double-Entry Cashbook:** Combines fee receipts (Income), general operational expenses, and paid faculty salaries (Disbursements).
- **Daily & Monthly Rollups:** Real-time cash balance, daily summaries, and calendar month financial statements.

### 5. ⚙️ Institutional Settings & Administration (`school`)
- **Executive Dashboard:** Live statistics on student strength, faculty headcount, monthly collections, and cash balance.
- **Branded Master Control:** Custom administrative console featuring Kohisar emblem and institutional branding.
- **Database Backup Engine:** Live downloadable snapshots and one-click restore utilities.

### 6. 📊 Universal Excel Import & Export (`openpyxl` Data Hub)
- **Central Data Exchange Hub (`/excel-hub/`):** Unified institutional dashboard to manage all import/export tasks in one place.
- **Sample Spreadsheet Templates:** Download pre-formatted Excel templates (`.xlsx`) with sample data for Students, Faculty/Staff, and Classes/Sections.
- **Bulk Student & Staff Onboarding:** Upload `.xlsx` spreadsheets to onboard or migrate hundreds of records in seconds, automatically creating classes, sections, family units, and initializing 12-month fee ledgers.
- **Real-Time Data Exports:** One-click institutional exports with professional navy styling and auto-adjusted columns for:
  - Student Directory & Admissions
  - Faculty & Staff Directory with Salary Scales
  - Academic Classes & Fee Schedules
  - 12-Month Fee Register Grid
  - Outstanding Fee Defaulters List
  - Consolidated Cashbook Ledger (Income & Expenses)
  - Monthly Financial Statements & Cashflows

---

## 🚀 Quick Start & One-Click Execution

### For Daily Use:
Double-click the **`Kohisar Model School (KMS)`** shortcut on your Desktop, or double-click **`kms_run.bat`**.
The system will automatically:
1. Verify and launch the PostgreSQL database service.
2. Free network port 8000.
3. Automatically launch your default web browser to:  
   👉 **`http://127.0.0.1:8000/`**

### Default Administrator Credentials:
- **Username:** `admin`
- **Password:** `admin123`

---

## 🛠️ Automated Setup on New Computers

To deploy on a new computer:
1. Ensure **Python (3.11+)** and **PostgreSQL (15+)** are installed.
2. Double-click **`kms_setup.bat`**.
3. The wizard will configure virtual environments, create the `kms_db` database, apply migrations, seed all school classes/teachers/students, and place a shortcut on your Desktop.

Refer to **`CLIENT_DEPLOYMENT_GUIDE.md`** for full client handover and setup instructions.

---

## 🔒 Security & Backups

- **Instant Backup:** Double-click **`kms_backup.bat`** to create a timestamped backup in `backups/`.
- **Instant Restore:** Double-click **`kms_restore.bat`** to restore any previous backup.

---

## 🏫 Institution Details
- **School:** Kohisar Model School & College
- **Campus:** Qalagay, Swat, Khyber Pakhtunkhwa, Pakistan
- **System:** Kohisar Management System (KMS) ERP
