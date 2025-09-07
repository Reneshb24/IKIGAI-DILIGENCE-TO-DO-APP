# Ikigai Diligence

## Introduction

**Ikigai Diligence** is a comprehensive **Python-based productivity and personal growth application** that combines personal task management with cloud backup, automated reporting, and intelligent reminders. Built with **Tkinter**, integrated with **Google Drive and Calendar APIs**, and equipped with **Gmail SMTP email support**, this application ensures that users stay productive, organized, and motivated.

It functions as a personal productivity assistant, allowing you to manage tasks locally while syncing data securely with Google Drive, integrating deadlines with Google Calendar, and sending important notifications and weekly reports via email.

---

## Features

* User Authentication (Signup/Login)
* Task Management (add, edit, delete tasks, set deadlines, reminders)
* Google Drive Sync (backup/restore JSON data and profile photo)
* Google Calendar Integration (add deadlines automatically)
* Email Notifications (welcome, reminders, birthdays, weekly reports)
* Weekly PDF Productivity Report (auto-generated using ReportLab)
* Profile Management (user details and photo)
* Chatbot Support (basic productivity queries)

---

## Modules Used

* **tkinter** → Graphical user interface
* **PIL (Pillow)** → Image handling
* **smtplib, email.mime** → Gmail SMTP email sending
* **reportlab** → Generate weekly productivity summary PDFs
* **schedule, threading** → Background reminders and scheduled weekly summary
* **googleapiclient, google-auth** → Google Drive and Calendar integration
* **json** → Local and cloud data storage

---

## How It Works

1. **Authentication**: Users sign up or login. Details are stored in `user_data.json`.
2. **Task Management**: Add, edit, or delete tasks with deadlines.
3. **Google Drive and Calendar**: Data is synced with Drive; deadlines are added to Calendar.
4. **Email System**: Sends welcome emails, reminders, and weekly PDF reports.
5. **Background Threads**: Scheduler runs reminders and weekly summary automatically.

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/Reneshb24/IKIGAI-DILIGENCE-TO-DO-APP
cd ikigai-diligence
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. File Placement

Ensure that `Ikigai_diligence.py`, `credentials.json`, image files (icons, logos), and all related files are placed in the same folder. This is required for the program to run properly.

---

## Google API Setup (Drive and Calendar)

### Step 1: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. Enable the following APIs:

   * Google Drive API
   * Google Calendar API
4. Go to **IAM & Admin → Service Accounts → Create Service Account**.
5. Assign roles:

   * Drive File Editor
   * Calendar Editor
6. Download the JSON key file.
7. Rename it to:

   ```
   credentials.json
   ```
8. Place it in the project root (same folder as `Ikigai_diligence.py`).

### Step 2: Update Code (Line \~70)

In `Ikigai_diligence.py`:

```python
# Replace "credentials.json" with your own Service Account JSON file if the name differs
SERVICE_ACCOUNT_FILE = "credentials.json"
```

---

## Google Drive Data Folder Setup

Ikigai Diligence syncs JSON files with Drive.

1. Create a folder in Google Drive (e.g., `IkigaiDiligence`).
2. Share it with your Service Account email (found in `credentials.json`) and give **Editor** access.
3. Copy the folder ID from the URL:

   ```
   https://drive.google.com/drive/folders/XXXXXXXXXXXXXXXXXXXX
   ```
4. Use this folder ID in the code where required (e.g., inside `upload_to_drive` or `download_from_drive`).

### Required JSON Files

Inside this Drive folder, create these empty JSON files before running the app:

* `user_data.json`
* `task_data.json`
* `feedback_data.json`
* `profile_data.json`
* `chatbot_data.json`

The program downloads them at startup, updates them locally, and uploads them back automatically.

---

## Gmail App Password Setup

### Step 1: Create App Password

1. Go to [Google Account Security](https://myaccount.google.com/security).
2. Enable **2-Step Verification**.
3. Under **App Passwords**, generate a password for Mail.
4. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`).

### Step 2: Update Python File

Replace dummy placeholders in `Ikigai_diligence.py`:

* **Line 843**

```python
msg['From'] = "example@gmail.com"   # Replace with your Gmail
```

* **Line 853**

```python
server.login("example@gmail.com", "**** **** ****")   # Replace with your Gmail and App Password
```

* **Line 1092**

```python
sender_email = "example@gmail.com"          # Replace with your Gmail
sender_password = "**** **** **** ****"     # Replace with your Gmail 16-digit App Password
```

---

## Running the App

```bash
python Ikigai_diligence.py
```

On launch:

* JSON files are synced with Google Drive.
* Task reminder scheduler starts.
* Weekly productivity summary email is scheduled.

---

## Functions and Their Roles

* **signup\_user()** → Registers a new user.
* **login\_user()** → Authenticates user credentials.
* **send\_email\_with\_attachment()** → Sends weekly PDF report.
* **send\_email()** → Sends reminders, welcome emails, notifications.
* **generate\_weekly\_summary()** → Creates productivity summary PDF.
* **upload\_to\_drive()** → Uploads local files to Drive.
* **download\_from\_drive()** → Downloads files from Drive.
* **sync\_data\_with\_drive()** → Synchronizes all JSON data with Drive.
* **check\_task\_reminders()** → Sends reminders for due tasks.
* **start\_reminder\_thread()** → Background thread for reminders.
* **start\_weekly\_summary\_thread()** → Background thread for weekly summaries.

---

## Future Enhancements

* Web dashboard version of Ikigai Diligence
* Mobile companion app (Android/iOS)
* AI-based task prioritization and recommendations
* Advanced analytics and productivity insights
* Encrypted storage for JSON and Drive data

---

## Security Notes

* Do not commit your real Gmail or App Password.
* Do not upload `credentials.json` to GitHub.
* Only dummy placeholders are included in the repository for safety.
* Sensitive files must remain local.

---

## Author

* Renesh B
