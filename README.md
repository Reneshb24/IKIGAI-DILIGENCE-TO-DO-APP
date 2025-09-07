# Ikigai Diligence

## Introduction

**Ikigai Diligence** is a comprehensive **Python-based productivity and personal growth application** that combines personal task management with cloud backup, automated reporting, and intelligent reminders. Built with **Tkinter**, integrated with **Google Drive and Calendar APIs**, and equipped with **Gmail SMTP email support**, this application ensures that users stay productive, organized, and motivated.

It functions as a personal productivity assistant, allowing users to manage tasks locally while syncing data securely with Google Drive, integrating deadlines with Google Calendar, and sending important notifications and weekly reports via email. The app is designed to be fully operational out-of-the-box once dependencies are installed and configuration is completed.

---

## Features

* **User Authentication**: Signup/Login with secure credential storage.
* **Task Management**: Add, edit, delete tasks, set deadlines, reminders, mark tasks as complete or pending, and track progress.
* **Google Drive Sync**: Backup and restore JSON data, profile photos, and task-related files.
* **Google Calendar Integration**: Automatically add deadlines and events to the calendar.
* **Email Notifications**: Send welcome emails, reminders, birthday greetings, and weekly PDF reports.
* **Weekly PDF Productivity Report**: Auto-generated using ReportLab summarizing task completion, pending tasks, and productivity trends.
* **Profile Management**: Store and update user details, including profile photos.
* **Chatbot Support**: Handles basic productivity-related queries.
* **Background Scheduler**: Runs reminders and weekly summary generation automatically without interrupting the main GUI.

---

## Modules Used

* **tkinter** → Graphical user interface creation.
* **PIL (Pillow)** → Image loading, resizing, and display.
* **smtplib, email.mime** → Sending emails via Gmail SMTP.
* **reportlab** → Generate weekly PDF productivity summaries.
* **schedule, threading** → Background task scheduling for reminders and weekly summaries.
* **googleapiclient, google-auth** → Google Drive and Calendar API integration.
* **json** → Local and cloud storage of task and user data.
* **datetime** → Task deadline handling and date comparisons.
* **os, shutil** → File handling and local directory management.

---

## How It Works

1. **Authentication**: Users create an account or login. Credentials are saved securely in `user_data.json`.
2. **Task Management**: Users can create tasks with titles, descriptions, priority levels, and deadlines. Tasks can be edited, marked as complete, or deleted.
3. **Google Drive Integration**: JSON files storing user data, tasks, profiles, feedback, and chatbot data are automatically synced with Google Drive.
4. **Google Calendar Integration**: Task deadlines are automatically added to the user's Google Calendar to ensure timely reminders.
5. **Email System**: Sends automated welcome emails, task reminders, birthday wishes, and weekly productivity reports.
6. **Background Threads**: `threading` and `schedule` modules handle recurring reminders and weekly summary generation without interrupting the main GUI.
7. **Chatbot Support**: Users can ask basic productivity questions, and the bot provides responses from pre-defined JSON datasets.

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

Dependencies include `tkinter`, `Pillow`, `google-api-python-client`, `google-auth`, `reportlab`, `schedule`, and `threading`.

### 3. File Placement

Ensure that the following files are in the same folder for proper operation:

* `Ikigai_diligence.py`
* `credentials.json`
* Image files (icons, logos)
* JSON templates (`user_data.json`, `task_data.json`, `feedback_data.json`, `profile_data.json`, `chatbot_data.json`)

All files should remain in the same directory to ensure smooth functioning.

---

## Google API Setup (Drive and Calendar)

### 1. Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project.
3. Enable the following APIs:

   * Google Drive API
   * Google Calendar API
4. Navigate to **IAM & Admin → Service Accounts → Create Service Account**.
5. Assign roles:

   * Drive File Editor
   * Calendar Editor
6. Download the JSON key file and rename it to `credentials.json`.
7. Place `credentials.json` in the project root (same folder as `Ikigai_diligence.py`).

### 2. Update Code for Service Account

In `Ikigai_diligence.py` around line 70:

```python
SERVICE_ACCOUNT_FILE = "credentials.json"  # Replace if your file name differs
```

### 3. Setup Google Drive Folder

1. Create a folder in Google Drive, e.g., `IkigaiDiligence`.
2. Share it with your Service Account email and provide **Editor** access.
3. Copy the folder ID from the URL:

   ```
   https://drive.google.com/drive/folders/XXXXXXXXXXXXXXXXXXXX
   ```
4. Use this folder ID in the code wherever required for upload/download functions.
5. Create these empty JSON files inside the folder before running the app:

   * `user_data.json`
   * `task_data.json`
   * `feedback_data.json`
   * `profile_data.json`
   * `chatbot_data.json`

The app will automatically download them at startup, update locally, and upload changes back to Drive.

---

## Gmail App Password Setup

### 1. Create App Password

1. Go to [Google Account Security](https://myaccount.google.com/security).
2. Enable **2-Step Verification**.
3. Under **App Passwords**, generate a new password for Mail.
4. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`).

### 2. Paste in Python File

Update the following lines in `Ikigai_diligence.py` with your Gmail and app password:

* **Line 843**

```python
msg['From'] = "your_email@gmail.com"  # Replace with your Gmail address
```

* **Line 853**

```python
server.login("your_email@gmail.com", "your_16_digit_app_password")  # Replace with Gmail and App Password
```

* **Line 1092**

```python
sender_email = "your_email@gmail.com"
sender_password = "your_16_digit_app_password"
```

This ensures the application can send emails for reminders, notifications, and weekly reports securely.

---

## Running the App

```bash
python Ikigai_diligence.py
```

* On launch, JSON files are synced with Google Drive.
* Background threads start for task reminders and weekly summary emails.
* GUI provides full access to task management, profile updates, and chatbot functionality.

---

## Key Functions and Details

* **signup\_user()** → Registers new users, ensuring unique usernames.
* **login\_user()** → Authenticates users with secure password validation.
* **add\_task() / edit\_task() / delete\_task()** → Full CRUD operations for tasks, including deadlines and priority levels.
* **send\_email\_with\_attachment()** → Sends weekly PDF reports via email.
* **send\_email()** → Sends reminders, notifications, welcome messages, and birthdays.
* **generate\_weekly\_summary()** → Creates PDF summarizing weekly task activity.
* **upload\_to\_drive() / download\_from\_drive()** → Upload/download JSON and image files to/from Google Drive.
* **sync\_data\_with\_drive()** → Synchronizes all JSON files automatically.
* **check\_task\_reminders()** → Monitors task deadlines and sends reminders.
* **start\_reminder\_thread()** → Background thread continuously monitors tasks for due reminders.
* **start\_weekly\_summary\_thread()** → Background thread generates and sends weekly PDF summaries.
* **chatbot\_query()** → Handles productivity-related queries using JSON datasets.

All functions integrate with background threads to ensure GUI responsiveness and smooth operation.

---

## Future Enhancements

* Web dashboard version of Ikigai Diligence.
* Mobile companion app for Android/iOS.
* AI-based task prioritization and recommendations.
* Advanced analytics and productivity insights.
* Encrypted local and cloud data storage.
* Real-time collaboration features for teams.

---

## Security Notes

* Never commit real Gmail credentials or `credentials.json` to GitHub.
* Dummy placeholders are included for safe public usage.
* All sensitive files (credentials, JSON backups, passwords) must remain local and secure.

---

## Author

* Renesh B
