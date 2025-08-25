from tkinter import ttk, filedialog
import customtkinter as ctk
from tkinter import messagebox, simpledialog
from datetime import datetime
import json
import os
import subprocess
from tkcalendar import DateEntry
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from fpdf import FPDF
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import platform
import threading
import time
from datetime import datetime, timedelta
import schedule
import os, base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

USER_DATA_FILE = 'user_data.json'
TASK_DATA_FILE = 'task_data.json'
FEEDBACK_DATA_FILE = 'feedback_data.json'
PROFILE_DATA_FILE = 'profile_data.json'
CHATBOT_DATA_FILE = 'chatbot_data.json' 

class TaskManagerApp:
    def __init__(self, root):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.root = root
        self.root.title("Ikigai Diligence")
        self.root.geometry("900x600")

        self.current_user = None
        self.profile_photo_path = None
        self.initialize_drive_api()  
        self.load_user_data()
        self.load_task_data()
        self.load_feedback_data()
        self.load_profile_data()
        self.load_chatbot_data()
        self.create_start_page()
    
    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def initialize_drive_api(self):
        SCOPES = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/calendar'
        ]
        SERVICE_ACCOUNT_FILE = 'ikigai-diligence-444410-ef2de96affdf.json'
        self.credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        self.calendar_service = build('calendar', 'v3', credentials=self.credentials)
	    
    def start_reminder_thread(self):
        reminder_thread = threading.Thread(target=self.send_reminders_every_7_hours)
        reminder_thread.daemon = True  
        reminder_thread.start()
        
    def send_reminders_every_7_hours(self):
        while True:
            self.check_and_send_notifications()
            time.sleep(7 * 60 * 60)
            
    def load_user_data(self):
        results = self.drive_service.files().list(q="name='user_data.json'", fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            self.user_data = {}
            self.save_user_data()
            return
        file_id = items[0]['id']
        request = self.drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        self.user_data = json.load(fh)
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                self.user_data = json.load(f)

    def save_user_data(self):
	    with open(USER_DATA_FILE, 'w') as f:
	        json.dump(self.user_data, f)
	    results = self.drive_service.files().list(q="name='user_data.json'", fields="files(id)").execute()
	    items = results.get('files', [])
	    if items:
	        file_id = items[0]['id']
	        media = MediaFileUpload(USER_DATA_FILE, mimetype='application/json')
	        self.drive_service.files().update(fileId=file_id, media_body=media).execute()
	    else:
	        file_metadata = {'name': 'user_data.json'}
	        media = MediaFileUpload(USER_DATA_FILE, mimetype='application/json')
	        self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    def load_task_data(self):
        results = self.drive_service.files().list(q="name='task_data.json'", fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            self.task_data = {}
            self.save_task_data()
            return
        file_id = items[0]['id']
        request = self.drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        self.task_data = json.load(fh)
        if os.path.exists(TASK_DATA_FILE):
            with open(TASK_DATA_FILE, 'r') as f:
            	self.task_data = json.load(f)

    def save_task_data(self):
	    with open(TASK_DATA_FILE, 'w') as f:
	        json.dump(self.task_data, f)
	    results = self.drive_service.files().list(q="name='task_data.json'", fields="files(id)").execute()
	    items = results.get('files', [])
	    if items:
	        file_id = items[0]['id']
	        media = MediaFileUpload(TASK_DATA_FILE, mimetype='application/json')
	        self.drive_service.files().update(fileId=file_id, media_body=media).execute()
	    else:
	        file_metadata = {'name': 'task_data.json'}
	        media = MediaFileUpload(TASK_DATA_FILE, mimetype='application/json')
	        self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    def load_feedback_data(self):
        results = self.drive_service.files().list(q="name='feedback_data.json'", fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            self.feedback_data = {}
            self.save_feedback_data()
            return
        file_id = items[0]['id']
        request = self.drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        self.feedback_data = json.load(fh)
        if os.path.exists(FEEDBACK_DATA_FILE):
            with open(FEEDBACK_DATA_FILE, 'r') as f:
                self.feedback_data = json.load(f)

    def save_feedback_data(self):
	    with open(FEEDBACK_DATA_FILE, 'w') as f:
	        json.dump(self.feedback_data, f)
	    results = self.drive_service.files().list(q="name='feedback_data.json'", fields="files(id)").execute()
	    items = results.get('files', [])
	    if items:
	        file_id = items[0]['id']
	        media = MediaFileUpload(FEEDBACK_DATA_FILE, mimetype='application/json')
	        self.drive_service.files().update(fileId=file_id, media_body=media).execute()
	    else:
	        file_metadata = {'name': 'feedback_data.json'}
	        media = MediaFileUpload(FEEDBACK_DATA_FILE, mimetype='application/json')
	        self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    def load_profile_data(self):
        results = self.drive_service.files().list(q="name='profile_data.json'", fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            self.profile_data = {}
            self.save_profile_to_file()
            return
        file_id = items[0]['id']
        request = self.drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        fh.seek(0)
        self.profile_data = json.load(fh)
        if os.path.exists(PROFILE_DATA_FILE):
            with open(PROFILE_DATA_FILE, 'r') as f:
                self.profile_data = json.load(f)

    def save_profile_to_file(self):
	    with open(PROFILE_DATA_FILE, 'w') as f:
	        json.dump(self.profile_data, f)
	    results = self.drive_service.files().list(q="name='profile_data.json'", fields="files(id)").execute()
	    items = results.get('files', [])
	    if items:
	        file_id = items[0]['id']
	        media = MediaFileUpload(PROFILE_DATA_FILE, mimetype='application/json')
	        self.drive_service.files().update(fileId=file_id, media_body=media).execute()
	    else:
	        file_metadata = {'name': 'profile_data.json'}
	        media = MediaFileUpload(PROFILE_DATA_FILE, mimetype='application/json')
	        self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    def load_chatbot_data(self):
        results = self.drive_service.files().list(q="name='chatbot_data.json'", fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            self.chatbot_data = {}
            self.save_chatbot_data()
            return
        file_id = items[0]['id']
        request = self.drive_service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        self.chatbot_data = json.load(fh)
        if os.path.exists(CHATBOT_DATA_FILE):
            with open(CHATBOT_DATA_FILE, 'r') as f:
                self.chatbot_data = json.load(f)

    def save_chatbot_data(self):
        with open(CHATBOT_DATA_FILE, 'w') as f:
            json.dump(self.chatbot_data, f)
        results = self.drive_service.files().list(q="name='chatbot_data.json'", fields="files(id)").execute()
        items = results.get('files', [])
        if items:
            file_id = items[0]['id']
            media = MediaFileUpload(CHATBOT_DATA_FILE, mimetype='application/json')
            self.drive_service.files().update(fileId=file_id, media_body=media).execute()
        else:
            file_metadata = {'name': 'chatbot_data.json'}
            media = MediaFileUpload(CHATBOT_DATA_FILE, mimetype='application/json')
            self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    def create_start_page(self):
	    self.clear_widgets()
	    try:
	        logo_image = ctk.CTkImage(Image.open("ikigai(var1).png"), size=(550, 500))
	        logo_label = ctk.CTkLabel(self.root, image=logo_image, text="")
	        logo_label.image = logo_image  
	        logo_label.pack(pady=(10, 20))
	        ctk.CTkLabel(self.root, text="Where Purpose Meets Productivity.", font=("Arial", 16, "italic"), text_color="#4CAF50").pack(pady=(10))  
	    except Exception:
	        pass 
	    button_frame = ctk.CTkFrame(self.root, fg_color="#F7F7F7", corner_radius=10)
	    button_frame.pack(pady=20)
	    try:
	        signup_icon = ctk.CTkImage(Image.open("signup_icon.png"), size=(40, 40))
	        login_icon = ctk.CTkImage(Image.open("login_icon.png"), size=(40, 40))
	    except Exception:
	        signup_icon = None
	        login_icon = None  
	    ctk.CTkButton(button_frame, text="Sign Up", image=signup_icon, compound="left", font=("Arial", 14),
	                  fg_color="#0078D4", text_color="white", hover_color="#0056A3", command=self.sign_up).grid(row=0, column=0, padx=20, pady=10)
	    ctk.CTkButton(button_frame, text="Login", image=login_icon, compound="left", font=("Arial", 14),
	                  fg_color="#0078D4", text_color="white", hover_color="#0056A3", command=self.login).grid(row=0, column=1, padx=20, pady=10)
	    watermark_frame = ctk.CTkFrame(self.root, fg_color=self.root["bg"], border_width=0)
	    watermark_frame.pack(side=ctk.BOTTOM, fill=ctk.X, padx=10, pady=10)
	    creators = ["CREATOR:",  "Renesh B"]
	    for creator in creators:
	        try:
	            creators_label = ctk.CTkLabel(watermark_frame, text=creator, font=("Arial", 15), text_color="gray")
	            creators_label.pack(anchor='e')
	        except Exception:
	            pass 
	        self.root.update()
	        self.root.after(1000)
	      
    def send_welcome_email(self, username, password):
	    user_profile = self.profile_data.get(username, {})
	    subject = "Welcome to Ikigai Diligence!"
	    message = f"""
	    <html>
	        <body>
	            <h2 style="color: #4CAF50;">Welcome, {user_profile.get('name', username)}!</h2>
	            <p>Thank you for choosing Ikigai Diligence. We're excited to have you on board!</p>
	            <p>Your account details:</p>
	            <p><strong>Username:</strong> {username}</p>
	            <p><strong>Password:</strong> {password}</p>
	            <p style="color: red;"><strong>Important:</strong> For your security, we recommend that you change your password after your first login. Do not share your password with anyone.</p>
	            <p>If you have any questions or need assistance, feel free to reach out.</p>
	            <p>Best Regards,<br>IKIGAI DILIGENCE</p>
	        </body>
	    </html>
	    """
	    self.send_email(user_profile['email'], subject, message)
    def create_top_bar(self, title="Ikigai Diligence ", color="#0078D4"):
	    top_bar = ctk.CTkFrame(self.root, fg_color=color, corner_radius=0)
	    top_bar.pack(fill=ctk.X, pady=(0, 10))   
	    title_label = ctk.CTkLabel(
	        top_bar, text=title, font=("Courier New", 20, "bold"), text_color="white"
	    )
	    title_label.pack(pady=10)  
    
    def open_chatbot(self):
	    self.clear_widgets()
	    self.create_top_bar(title="Ikigai Diligence ", color="#0078D4")
	
	    self.chat_display = ctk.CTkScrollableFrame(self.root, corner_radius=10)
	    self.chat_display.pack(pady=10, fill=ctk.BOTH, expand=True)
	
	    input_frame = ctk.CTkFrame(self.root)
	    input_frame.pack(fill=ctk.X, pady=10, padx=10)
	
	    self.user_input = ctk.CTkEntry(input_frame, placeholder_text="Type your message...", width=600)
	    self.user_input.pack(side=ctk.LEFT, padx=(0, 10), fill=ctk.X, expand=True)
	
	    send_button = ctk.CTkButton(input_frame, text="Send", command=self.send_message)
	    send_button.pack(side=ctk.RIGHT)
	
	    ctk.CTkButton(self.root, text="Back", command=self.create_main_page).pack(pady=10)
	    self.display_message(" Hello! How can I assist you today?", sender="System")
	
    def display_message(self, message, sender="System"):
	    if sender == "User":
	        bg_color = "#A8D5BA"
	        alignment = "e"
	        heading = "YOU"
	    else:
	        bg_color = "#A0522D"
	        alignment = "w"
	        heading = "IKIGAI"
	    card_frame = ctk.CTkFrame(self.chat_display, corner_radius=10, fg_color=bg_color)
	    card_frame.pack(pady=5, padx=10, anchor=alignment)
	    heading_label = ctk.CTkLabel(card_frame, text=heading, font=("Arial", 12, "bold"), text_color="#000000")
	    heading_label.pack(anchor="w" if sender == "System" else "e", padx=10, pady=(5, 0))
	    message_label = ctk.CTkLabel(card_frame, text=message, font=("Arial", 14), wraplength=400, justify="left",text_color="#000000")
	    message_label.pack(pady=5, padx=10)
	    timestamp_label = ctk.CTkLabel(
	        card_frame, text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), font=("Arial", 10), text_color="gray"
	    )
	    timestamp_label.pack(anchor="e", padx=10)
	
    def send_message(self):
	    user_message = self.user_input.get()
	    if user_message.strip():
	        self.display_message(user_message, sender="User")
	        response = self.get_chatbot_response(user_message)
	        self.display_message(response, sender="System")
	        self.user_input.delete(0, ctk.END)

    def get_chatbot_response(self, user_message):
        for entry in self.chatbot_data.get("responses", []):
            if user_message.lower() in entry["question"].lower():
                return entry["answer"]
        return "I'm sorry, I don't understand that. Could you clarify?"

    def sign_up(self):
	    self.clear_widgets()
	    ctk.CTkLabel(self.root, text="Sign Up", font=("Courier New", 28, "bold")).pack(pady=20)
	    form_frame = ctk.CTkFrame(self.root)
	    form_frame.pack(pady=20)
	    ctk.CTkLabel(form_frame, text="Username:").grid(row=0, column=0, padx=10, pady=10, sticky=ctk.W)
	    username_entry = ctk.CTkEntry(form_frame, width=250)  
	    username_entry.grid(row=0, column=1, padx=10, pady=10)
	
	    ctk.CTkLabel(form_frame, text="Password:").grid(row=1, column=0, padx=10, pady=10, sticky=ctk.W)
	    password_entry = ctk.CTkEntry(form_frame, show='*', width=250) 
	    password_entry.grid(row=1, column=1, padx=10, pady=10)
	    show_password_var = ctk.BooleanVar()
	    ctk.CTkCheckBox(form_frame, text="Show Password", variable=show_password_var,
	                    command=lambda: password_entry.configure(show='' if show_password_var.get() else '*')).grid(row=2, column=1, sticky=ctk.E, padx=10, pady=(0, 5))
	    already_account_label = ctk.CTkLabel(
	        self.root, text="Already have an account?", font=("Arial", 12, "underline"), text_color="blue", cursor="hand2"
	    )
	    already_account_label.place(x=800, y=225)
	    already_account_label.bind("<Button-1>", lambda e: self.login())
	    ctk.CTkButton(self.root, text="Sign Up", command=lambda: self.handle_sign_up(username_entry.get(), password_entry.get()),
	                  font=("Arial", 14), fg_color="#0078D4", text_color="white", hover_color="#0056A3", width=150).pack(pady=20)
	    ctk.CTkButton(self.root, text="Back", command=self.create_start_page, font=("Arial", 14),
	                  fg_color="#0078D4", text_color="white", hover_color="#0056A3", width=150).pack(pady=10)

    def handle_sign_up(self, username, password):
	    if username and password:
	        if username in self.user_data:
	            messagebox.showerror("Error", "Username already exists.")
	            self.create_start_page()
	        else:
	            self.user_data[username] = password
	            self.save_user_data()
	            self.current_user = username
	            messagebox.showinfo("Success", "Sign-Up successful!")
	            self.collect_profile_data(username)
	    else:
	        messagebox.showerror("Error", "Username and password are required.")
	        self.create_start_page()

    def collect_profile_data(self, username):
	    self.clear_widgets()
	    self.create_top_bar(title="Profile Information", color="#4CAF50")
	    if username not in self.profile_data:
	        self.profile_data[username] = {}
	    details_frame = ctk.CTkFrame(self.root, corner_radius=15, fg_color="#E8F5E9", width=600)
	    details_frame.place(relx=0.5, rely=0.08, anchor="n")
	    photo_frame = ctk.CTkFrame(details_frame, fg_color="#FFFFFF", corner_radius=10)
	    photo_frame.pack(pady=10)
	    default_image_path = "signup_icon.png"
	    profile_photo_path = self.profile_data[username].get('photo', default_image_path)
	    profile_image = ctk.CTkImage(Image.open(profile_photo_path), size=(100, 100))
	    
	    self.photo_label = ctk.CTkLabel(photo_frame, image=profile_image, text="")
	    self.photo_label.pack(pady=10)
	    ctk.CTkButton(photo_frame,
              text="Upload Photo",
              font=("Arial", 14),
              fg_color="#0078D4",
              text_color="white",
              hover_color="#0056A3",
              command=lambda: self.upload_profile_photo(self.photo_label, username)).pack(pady=5)
	    form_frame = ctk.CTkFrame(details_frame, fg_color="#FFFFFF", corner_radius=10)
	    form_frame.pack(pady=10, padx=20, fill=ctk.BOTH)
	    entries = {}
	    inputs = [
	        ("Name", "Enter your full name", ""),
	        ("Date of Birth", "Select your date of birth", "dob"),
	        ("Address", "Enter your address", ""),
	        ("Age", "Calculated automatically", "age", "readonly"),
	        ("Occupation", "Enter your occupation", ""),
	        ("Contact No", "Enter your phone number", ""),
	        ("Email", "Enter your email address", ""),
	    ]
	
	    for i, (label, placeholder, field, *opts) in enumerate(inputs):
	        ctk.CTkLabel(form_frame, text=f"{label}:", font=("Arial", 14), text_color="#0078D4").grid(row=i, column=0, padx=10, pady=10, sticky=ctk.W)
	        if field == "dob":
	            dob_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
	            dob_entry.grid(row=i, column=1, padx=10, pady=10)
	            entries[field] = dob_entry
	        elif field == "age":
	            age_entry = ctk.CTkEntry(form_frame, placeholder_text=placeholder, state="readonly", width=300)
	            age_entry.grid(row=i, column=1, padx=10, pady=10)
	            entries[field] = age_entry
	        else:
	            entry = ctk.CTkEntry(form_frame, placeholder_text=placeholder, width=300, state=opts[0] if opts else "normal")
	            entry.grid(row=i, column=1, padx=10, pady=10)
	            entries[label.lower().replace(" ", "_")] = entry
	    dob_entry.bind("<FocusOut>", lambda event: self.calculate_age(dob_entry.get(), age_entry))
	    buttons_frame = ctk.CTkFrame(self.root, fg_color="#E8F5E9", corner_radius=15, width=600)
	    buttons_frame.place(relx=0.5, rely=0.8, anchor="n")
	    ctk.CTkButton(buttons_frame,
	                  text="Save Profile",
	                  font=("Arial", 16),
	                  fg_color="#0078D4",
	                  text_color="white",
	                  hover_color="#0056A3",
	                  command=lambda: self.save_profile_data(
	                      username,
	                      entries["name"].get(),
	                      dob_entry.get(),
	                      entries["address"].get(),
	                      entries["age"].get(),
	                      entries["occupation"].get(),
	                      entries["contact_no"].get(),
	                      entries["email"].get()
	                  )).pack(pady=20)
	    ctk.CTkButton(buttons_frame,
	                  text="Back",
	                  font=("Arial", 14),
	                  fg_color="#0078D4",
	                  text_color="white",
	                  hover_color="#0056A3",
	                  command=self.create_start_page).pack(pady=10)

    def get_upload_photo_function(self, username):
	    def upload():
	        self.upload_profile_photo(self.photo_label, username)
	    return upload

    def calculate_age(self, dob_str, age_entry):
        if dob_str:
        	dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        	today = datetime.today().date()
        	age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        	age_entry.configure(state='normal')
        	age_entry.delete(0, ctk.END)
        	age_entry.insert(0, str(age))
        	age_entry.configure(state='readonly')
        	return age 
        return None

    def upload_profile_photo(self, photo_label, username):
	    new_photo_path = filedialog.askopenfilename(
	        title="Select Profile Photo",
	        filetypes=[("All Files", "*.*"), ("PDF Files", "*.pdf"),("Image Files", "*.png;*.jpg;*.jpeg")]
	    )
	    if new_photo_path:
	        try:
	            folder_id = self.get_or_create_profile_photos_folder()
	            file_metadata = {'name': os.path.basename(new_photo_path), 'parents': [folder_id]}
	            media = MediaFileUpload(new_photo_path, resumable=True)
	            uploaded_file = self.drive_service.files().create(
	                body=file_metadata,
	                media_body=media,
	                fields='id, name'
	            ).execute()
	            request = self.drive_service.files().get_media(fileId=uploaded_file['id'])
	            fh = io.BytesIO()
	            downloader = MediaIoBaseDownload(fh, request)
	            done = False
	            while not done:
	                status, done = downloader.next_chunk()
	            fh.seek(0)
	            local_photo_path = os.path.join("profile_photos", uploaded_file['name'])
	            os.makedirs("profile_photos", exist_ok=True)
	            with open(local_photo_path, "wb") as f:
	                f.write(fh.read())
	            self.profile_photo_path = local_photo_path 
	            if username not in self.profile_data:
	                self.profile_data[username] = {}
	            self.profile_data[username]['photo'] = local_photo_path 
	            self.save_profile_to_file()
	            profile_image = ctk.CTkImage(Image.open(local_photo_path), size=(100, 100))
	            photo_label.configure(image=profile_image)
	            photo_label.image = profile_image  
	            messagebox.showinfo("Success", "Profile photo uploaded and updated successfully!")
	        except Exception as e:
	            messagebox.showerror("Error", f"An error occurred: {str(e)}")
	    else:
	        messagebox.showwarning("Warning", "No file selected. Please try again.")
	
    def get_or_create_profile_photos_folder(self):
	    results = self.drive_service.files().list(
	        q="mimeType='application/vnd.google-apps.folder' and name='profile_photos'",
	        fields="files(id, name)"
	    ).execute()
	    items = results.get('files', [])
	    if items:
	        return items[0]['id']  
	    else:
	        file_metadata = {'name': 'profile_photos', 'mimeType': 'application/vnd.google-apps.folder'}
	        folder = self.drive_service.files().create(body=file_metadata, fields='id').execute()
	        return folder.get('id')  

    def save_profile_data(self, username, name, dob, address, age, occupation, contact, email):
	    if username not in self.profile_data:
	        self.profile_data[username] = {}
	
	    self.profile_data[username] = {
	        'name': name,
	        'dob': dob,
	        'address': address,
	        'age': age,
	        'occupation': occupation,
	        'contact': contact,
	        'email': email,
	        'photo': self.profile_photo_path  
	    }
	    self.save_profile_to_file()
	    messagebox.showinfo("Success", "Profile information saved successfully!")
	    self.send_welcome_email(username, self.user_data[username])
	    self.login()

    def download_profile_photo(self, username):
	    user_profile = self.profile_data.get(username, {})
	    photo_path = user_profile.get('photo')
	    if not photo_path:
	        return
	    file_name = os.path.basename(photo_path)
	    local_photo_path = os.path.join("profile_photos", file_name)
	    if not os.path.exists(local_photo_path):  
	        try:
	            results = self.drive_service.files().list(
	                q=f"name='{file_name}'", fields="files(id, name)"
	            ).execute()
	            items = results.get('files', [])
	            if items:
	                file_id = items[0]['id']
	                request = self.drive_service.files().get_media(fileId=file_id)
	                fh = io.BytesIO()
	                downloader = MediaIoBaseDownload(fh, request)
	                done = False
	                while not done:
	                    status, done = downloader.next_chunk()
	                fh.seek(0)
	                os.makedirs("profile_photos", exist_ok=True)
	                with open(local_photo_path, "wb") as f:
	                    f.write(fh.read())
	                print(f"Photo downloaded and saved locally as {local_photo_path}")
	            else:
	                print("Photo not found in Google Drive.")
	        except Exception as e:
	            print(f"Error downloading photo: {e}")
	    self.profile_data[username]['photo'] = local_photo_path
	    self.save_profile_to_file()

    def login(self):
	    self.clear_widgets()
	    ctk.CTkLabel(self.root, text="Login", font=("Courier New", 28, "bold")).pack(pady=20)
	    form_frame = ctk.CTkFrame(self.root)
	    form_frame.pack(pady=20)
	    ctk.CTkLabel(form_frame, text="Username:").grid(row=0, column=0, padx=10, pady=10, sticky=ctk.W)
	    username_entry = ctk.CTkEntry(form_frame, width=250) 
	    username_entry.grid(row=0, column=1, padx=10, pady=10)
	    ctk.CTkLabel(form_frame, text="Password:").grid(row=1, column=0, padx=10, pady=10, sticky=ctk.W)
	    password_entry = ctk.CTkEntry(form_frame, show='*', width=250)  
	    password_entry.grid(row=1, column=1, padx=10, pady=10)
	    show_password_var = ctk.BooleanVar()
	    ctk.CTkCheckBox(form_frame, text="Show Password", variable=show_password_var,
	                    command=lambda: password_entry.configure(show='' if show_password_var.get() else '*')).grid(row=2, column=1, sticky=ctk.E, padx=10, pady=(0, 5))
	    link_frame = ctk.CTkFrame(self.root, fg_color=self.root["bg"]) 
	    link_frame.place(x=650, y=225)
	    dont_have_account_label = ctk.CTkLabel(
	        link_frame, text="Don't have an account?", font=("Arial", 12, "underline"), text_color="blue", cursor="hand2"
	    )
	    dont_have_account_label.pack(side=ctk.LEFT, padx=(0, 10))  
	    dont_have_account_label.bind("<Button-1>", lambda e: self.sign_up())
	    forgot_password_label = ctk.CTkLabel(
	        link_frame, text="Forgot Password?", font=("Arial", 12, "underline"), text_color="blue", cursor="hand2"
	    )
	    forgot_password_label.pack(side=ctk.RIGHT)  
	    forgot_password_label.bind("<Button-1>", lambda e: self.forgot_password(username_entry.get()))
	    ctk.CTkButton(self.root, text="Login", command=lambda: self.handle_login(username_entry.get(), password_entry.get()),
	                  font=("Arial", 14), fg_color="#0078D4", text_color="white", hover_color="#0056A3", width=150).pack(pady=20)
	    ctk.CTkButton(self.root, text="Back", command=self.create_start_page, font=("Arial", 14),
	                  fg_color="#0078D4", text_color="white", hover_color="#0056A3", width=150).pack(pady=10)

    def forgot_password(self, username):
    	self.clear_widgets()
    	ctk.CTkLabel(self.root, text="Password Recovery", font=("Courier New", 28, "bold")).pack(pady=20)
    	form_frame = ctk.CTkFrame(self.root)
    	form_frame.pack(pady=20)
    	ctk.CTkLabel(form_frame, text="Username:").grid(row=0, column=0, padx=10, pady=10, sticky=ctk.W)
    	username_entry = ctk.CTkEntry(form_frame)
    	username_entry.grid(row=0, column=1, padx=10, pady=10)
    	username_entry.insert(0, username)
    	ctk.CTkLabel(form_frame, text="Date of Birth:").grid(row=1, column=0, padx=10, pady=10, sticky=ctk.W)
    	dob_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
    	dob_entry.grid(row=1, column=1, padx=10, pady=10)
    	ctk.CTkButton(self.root, text="Recover Password", command=lambda: self.recover_password(username_entry.get(), dob_entry.get())).pack(pady=20)
    	ctk.CTkButton(self.root, text="Back", command=self.create_start_page).pack(pady=10)
    
    def recover_password(self, username, dob):
        if username in self.user_data:
        	user_profile = self.profile_data.get(username, {})
        	if user_profile.get('dob') == dob:
        	   password = self.user_data[username]
        	   messagebox.showinfo("Password Recovery", f"Your password is: {password}")
        	   self.create_start_page()
        	else:
        		messagebox.showerror("Error", "Date of Birth does not match.")
        else:
        	messagebox.showerror("Error", "Username not found.")

    def check_profile_completion(self):
	    if self.current_user and self.current_user in self.profile_data:
	        profile = self.profile_data[self.current_user]
	        if not all([profile.get('name'), profile.get('dob'), profile.get('email')]):
	            messagebox.showinfo("Profile Incomplete", "Please complete your profile for a better experience.")
	            self.collect_profile_data(self.current_user)
	            
    def show_error(self, message):
	    from tkinter import messagebox
	    messagebox.showerror("Error", message)
    def show_message(self, message):
	    from tkinter import messagebox
	    messagebox.showinfo("Info", message)

    def handle_login(self, username, password):
	    if username in self.user_data and self.user_data[username] == password:
	        self.current_user = username
	        self.download_profile_photo(username)
	        self.check_profile_completion()
	        self.create_main_page()
	        self.start_reminder_thread()
	        self.start_weekly_summary_thread()
	        self.check_and_send_summary(username)
	    else:
	        messagebox.showerror("Error", "Invalid credentials.")
	        self.create_start_page()

    def generate_weekly_summary(self,username):
	    user_profile = self.profile_data.get(username, {})
	    user_email = user_profile.get("email", "")
	    if not user_email:
	        print("User email not found. Cannot send weekly summary.")
	        return
	
	    current_date = datetime.now().date()
	    week_start = current_date - timedelta(days=current_date.weekday())
	    week_end = week_start + timedelta(days=6)
	
	    tasks = [
	        task for task in self.task_data.values()
	        if task['user'] == username and week_start <= datetime.strptime(task['due_date'], "%Y-%m-%d").date() <= week_end
	    ]
	    completed_tasks = [task for task in tasks if task['completed']]
	    pending_tasks = [task for task in tasks if not task['completed']]
	
	    total_tasks = len(tasks)
	    completed_percentage = (len(completed_tasks) / total_tasks) * 100 if total_tasks else 0
	    pdf = FPDF()
	    pdf.set_auto_page_break(auto=True, margin=15)
	    pdf.add_page()
	    pdf.set_font("Arial", size=12)
	    pdf.set_font("Arial", style="B", size=16)
	    pdf.cell(0, 10, "IKIGAI DILIGENCE - Weekly Summary", ln=True, align="C")
	    pdf.set_font("Arial", style="B", size=14)
	    pdf.cell(0, 10, "Where Purpose Meets Productivity.", ln=True, align="C")
	    pdf.ln(5)
	    pdf.set_font("Arial", style="B", size=14)
	    pdf.cell(0, 10, "Personal Details:", ln=True)
	    pdf.set_font("Arial", size=12)
	    details = [
	        f"Name: {user_profile.get('name', 'N/A')}",
	        f"Date of Birth: {user_profile.get('dob', 'N/A')}",
	        f"Age: {user_profile.get('age', 'N/A')}",
	        f"Address: {user_profile.get('address', 'N/A')}",
	        f"Contact No: {user_profile.get('contact', 'N/A')}",
	        f"Email: {user_email}",
	    ]
	    for detail in details:
	        pdf.cell(0, 10, detail, ln=True)
	    pdf.ln(2)
	    pdf.set_font("Arial", style="B", size=14)
	    pdf.cell(0, 10, "Weekly Analysis:", ln=True)
	    pdf.set_font("Arial", size=12)
	    pdf.cell(0, 10, f"Total Tasks Assigned: {total_tasks}", ln=True)
	    pdf.cell(0, 10, f"Tasks Completed: {len(completed_tasks)} ({completed_percentage:.2f}%)", ln=True)
	    pdf.cell(0, 10, f"Tasks Pending: {len(pending_tasks)}", ln=True)
	    pdf.ln(5)
	    pdf.set_font("Arial", style="B", size=14)
	    pdf.cell(0, 10, "Detailed Summary Insights:", ln=True)
	    pdf.set_font("Arial", size=12)
	    if completed_percentage == 100:
	        pdf.cell(0, 10, "Congratulations! You completed all tasks this week. Keep up the great work!", ln=True)
	    elif completed_percentage >= 80:
	        pdf.cell(0, 10, "Excellent performance! You're achieving high productivity. Consider fine-tuning to hit 100%.", ln=True)
	    elif completed_percentage >= 50:
	        pdf.cell(0, 10, "You completed over half of your tasks. Prioritize pending tasks to improve productivity.", ln=True)
	    else:
	        pdf.cell(0, 10, "Focus on planning and task management. Consider breaking tasks into smaller steps.", ln=True)
	    pdf.multi_cell(0, 10, "Tip: Regularly review your pending tasks and allocate specific time slots to improve focus and productivity.")
	    pdf.ln(5)
	    pdf.set_font("Arial", style="B", size=14)
	    pdf.cell(0, 10, "Incomplete Tasks:", ln=True)
	    pdf.set_font("Arial", size=12)
	    if pending_tasks:
	        pdf.set_font("Arial", size=10)
	        pdf.cell(20, 10, "S.No", 1)
	        pdf.cell(70, 10, "Task Name", 1)
	        pdf.cell(50, 10, "Due Date", 1)
	        pdf.cell(50, 10, "Description", 1, ln=True)
	        for idx, task in enumerate(pending_tasks, 1):
	            pdf.cell(20, 10, str(idx), 1)
	            pdf.cell(70, 10, task['name'], 1)
	            pdf.cell(50, 10, task['due_date'], 1)
	            pdf.cell(50, 10, task['description'], 1, ln=True)
	    else:
	        pdf.cell(0, 10, "All tasks were completed this week!", ln=True)
	    pdf.ln(5)
	    pdf.add_page()
	    pdf.set_font("Arial", style="B", size=14)
	    pdf.cell(0, 10, "Completed Tasks:", ln=True)
	    if completed_tasks:
	        pdf.set_font("Arial", size=10)
	        pdf.cell(20, 10, "S.No", 1)
	        pdf.cell(70, 10, "Task Name", 1)
	        pdf.cell(50, 10, "Completion Date", 1)
	        pdf.cell(50, 10, "Description", 1, ln=True)
	        for idx, task in enumerate(completed_tasks, 1):
	            pdf.cell(20, 10, str(idx), 1)
	            pdf.cell(70, 10, task['name'], 1)
	            pdf.cell(50, 10, task.get('completion_date', 'N/A'), 1)
	            pdf.cell(50, 10, task['description'], 1, ln=True)
	    else:
	        pdf.cell(0, 10, "No tasks were completed this week.", ln=True)
	    pdf.ln(10)
	    pdf.set_font("Arial", style="B", size=14)
	    pdf.cell(0, 10, "Productivity Analysis:", ln=True)
	    task_dates = [datetime.strptime(task['due_date'], "%Y-%m-%d").date() for task in tasks]
	    completed_dates = [datetime.strptime(task['due_date'], "%Y-%m-%d").date() for task in completed_tasks]
	    plt.figure(figsize=(6, 4))
	    plt.hist(task_dates, bins=7, alpha=0.5, label='Tasks Due', color='blue')
	    plt.hist(completed_dates, bins=7, alpha=0.5, label='Tasks Completed', color='green')
	    plt.xlabel('Date')
	    plt.ylabel('Number of Tasks')
	    plt.title('Tasks Due vs Completed')
	    plt.legend()
	    graph_path = "productivity_graph.png"
	    plt.savefig(graph_path)
	    plt.close()
	    pdf.image(graph_path, x=10, y=pdf.get_y(), w=190)
	    os.remove(graph_path)
	    pdf.ln(20)
	    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	    pdf.set_font("Arial", size=10, style="I")
	    pdf.set_y(-5)
	    pdf.cell(0, 10, f"Generated on: {timestamp}", ln=True, align="C")
	    pdf_filename = f"{username}_Weekly_Summary.pdf"
	    pdf.output(pdf_filename)
	    print(f"Weekly summary saved as {pdf_filename}.")
	    subject = "Your Weekly Productivity Summary"
	    message = f"""
	    <html>
	        <body>
	            <p>Dear {user_profile.get('name', username)},</p>
	            <p>Attached is your weekly productivity summary. Keep up the great work!</p>
	            <p>Best regards,<br>Ikigai Diligence</p>
	        </body>
	    </html>
	    """
	    self.send_email_with_attachment(user_email, subject, message, pdf_filename)
  
    def schedule_weekly_summary(self):
	    schedule.every().sunday.at("18:00").do(lambda: [
	        generate_weekly_summary(username)
	        for username in self.user_data.keys()
	    ])
	    while True:
	        schedule.run_pending()
	        time.sleep(1)

    def check_and_send_summary(self, username):
     self.generate_weekly_summary(username)

    def send_email_with_attachment(self, to_email, subject, message, attachment_path):
	    try:
	        msg = MIMEMultipart()
	        msg['From'] = "renesb2406@gmail.com"
	        msg['To'] = to_email
	        msg['Subject'] = subject
	        msg.attach(MIMEText(message, 'html'))
	        with open(attachment_path, "rb") as attachment:
	            part = MIMEText(attachment.read(), 'base64', 'utf-8')
	            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
	            msg.attach(part)
	        with smtplib.SMTP('smtp.gmail.com', 587) as server:
	            server.starttls()
	            server.login("reneb2406@gmail.com", "rnaw jmsj cjxh lubz" )
	            server.send_message(msg)
	        print(f"Weekly summary sent to {to_email}.")
	    except Exception as e:
	        print(f"Failed to send email: {e}")
        
    def start_weekly_summary_thread(self):
	    weekly_thread = threading.Thread(target=self.schedule_weekly_summary)
	    weekly_thread.daemon = True
	    weekly_thread.start()

    def create_main_page(self):
	    self.clear_widgets()
	    header_frame = ctk.CTkFrame(self.root, fg_color="#4CAF50", corner_radius=0, height=100)
	    header_frame.pack(fill=ctk.X)
	    ctk.CTkLabel(header_frame, text=f"Welcome, {self.current_user}!", 
	                 font=("Courier New", 36, "bold"), text_color="white").pack(pady=20)
	    center_frame = ctk.CTkFrame(self.root, fg_color="#E8F5E9", corner_radius=20, width=700, height=500)
	    center_frame.place(relx=0.5, rely=0.51, anchor="center")
	    profile_photo = self.profile_data[self.current_user].get('photo')
	    if profile_photo and os.path.exists(profile_photo):
	        profile_icon = ctk.CTkImage(Image.open(profile_photo), size=(80, 80))
	    else:
	        profile_icon = ctk.CTkImage(Image.open("signup_icon.png"), size=(80, 80))
	    ctk.CTkLabel(center_frame, text="Your Profile", font=("Arial", 20, "bold"), text_color="#3E4E50").pack(pady=10)
	    ctk.CTkLabel(center_frame, image=profile_icon, text="").pack(pady=10)
	    button_frame = ctk.CTkFrame(center_frame, fg_color="#FFFFFF", corner_radius=15)
	    button_frame.pack(pady=30)
	    buttons = [
	        ("Notifications", "notification_icon.png", self.create_notification_window),
	        ("View Profile", "signup_icon.png", self.view_profile),
	        ("Add Task", "add_task_icon.png", self.add_task),
	        ("Load Tasks", "load_task_icon.png", self.load_tasks),
	        ("View Productivity", "productivity_icon.png", self.view_productivity),
	        ("Logout", "logout_icon.jpeg", self.logout),
	    ]
	    for i, (text, icon_path, command) in enumerate(buttons):
	        try:
	            button_icon = ctk.CTkImage(Image.open(icon_path), size=(50, 50))
	        except Exception:
	            button_icon = None  
	        ctk.CTkButton(button_frame, text=text, image=button_icon, compound="top",
	                      font=("Arial", 16, "bold"), fg_color="#0078D4", text_color="white",
	                      hover_color="#0056A3", command=command, width=150, height=100).grid(row=i // 2, column=i % 2, padx=20, pady=20)
	    footer_frame = ctk.CTkFrame(self.root, fg_color="#F1F8E9", corner_radius=0, height=50)
	    footer_frame.pack(side=ctk.BOTTOM, fill=ctk.X)
	    try:
	        chatbot_icon = ctk.CTkImage(Image.open("chatbot_icon.png"), size=(40, 40))
	    except Exception:
	        chatbot_icon = None 
	
	    ctk.CTkButton(footer_frame, text="Need Help?", image=chatbot_icon, compound="left",
	                  font=("Arial", 14, "bold"), fg_color="#FF9800", text_color="white",
	                  hover_color="#FB8C00", command=self.open_chatbot).pack(side=ctk.RIGHT, padx=20, pady=10)
    
    def get_or_create_profile_photos_folder(self):
	    results = self.drive_service.files().list(
	        q="mimeType='application/vnd.google-apps.folder' and name='profile_photos'",
	        fields="files(id, name)"
	    ).execute()
	    items = results.get('files', [])
	    if items:
	        return items[0]['id'] 
	    else:
	        file_metadata = {'name': 'profile_photos', 'mimeType': 'application/vnd.google-apps.folder'}
	        folder = self.drive_service.files().create(body=file_metadata, fields='id').execute()
	        return folder.get('id')
	        
    def upload_profile_photo_view_profile(self):
	    new_photo_path = filedialog.askopenfilename(
	        title="Select Profile Photo",
	        filetypes=[("All Files", "*.*"), ("PDF Files", "*.pdf"),("Image Files", "*.png;*.jpg;*.jpeg")]
	    )
	    if new_photo_path:
	        try:
	            folder_id = self.get_or_create_profile_photos_folder()
	            file_metadata = {'name': os.path.basename(new_photo_path), 'parents': [folder_id]}
	            media = MediaFileUpload(new_photo_path, resumable=True)
	            uploaded_file = self.drive_service.files().create(
	                body=file_metadata,
	                media_body=media,
	                fields='id, name'
	            ).execute()
	            request = self.drive_service.files().get_media(fileId=uploaded_file['id'])
	            fh = io.BytesIO()
	            downloader = MediaIoBaseDownload(fh, request)
	            done = False
	            while not done:
	                status, done = downloader.next_chunk()
	            fh.seek(0)
	            local_photo_path = os.path.join("profile_photos", uploaded_file['name'])
	            os.makedirs("profile_photos", exist_ok=True)
	            with open(local_photo_path, "wb") as f:
	                f.write(fh.read())
	            self.profile_data[self.current_user]['photo'] = local_photo_path
	            self.save_profile_to_file()
	            self.view_profile()
	            messagebox.showinfo("Success", "Profile photo updated successfully!")
	        except Exception as e:
	            messagebox.showerror("Error", f"An error occurred: {str(e)}")
	    else:
	        messagebox.showwarning("Warning", "No file selected. Please try again.")

    def view_profile(self):
	    self.clear_widgets()
	    header_frame = ctk.CTkFrame(self.root, fg_color="#4CAF50", corner_radius=0, height=100)
	    header_frame.pack(fill=ctk.X)
	    ctk.CTkLabel(header_frame,text="Profile Information",font=("Courier New", 28, "bold"),text_color="white", ).pack(pady=20)
	    profile_frame = ctk.CTkFrame(self.root, fg_color="#E8F5E9", corner_radius=20, width=700, height=500)
	    profile_frame.place(relx=0.5, rely=0.35, anchor="center")
	    profile_info = self.profile_data[self.current_user]
	    default_image_path = "signup_icon.png"
	    photo_frame = ctk.CTkFrame(profile_frame, fg_color="#FFFFFF", corner_radius=15)
	    photo_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n")
	    if profile_info.get("photo") and os.path.exists(profile_info["photo"]):
	    	profile_image = ctk.CTkImage(Image.open(profile_info["photo"]), size=(120, 120))
	    else:
	    	 profile_image = ctk.CTkImage(Image.open(default_image_path), size=(120, 120))
	    ctk.CTkLabel(photo_frame, image=profile_image, text="").pack(pady=10)
	    ctk.CTkButton(photo_frame,
              text="Update Photo",
              font=("Arial", 14, "bold"),
              fg_color="#0078D4",
              text_color="white",
              hover_color="#0056A3",
              command=self.upload_profile_photo_view_profile).pack(pady=5)
	    details_frame = ctk.CTkFrame(profile_frame, fg_color="#FFFFFF", corner_radius=15)
	    details_frame.grid(row=0, column=1, padx=20, pady=20, sticky="n")
	
	    details = [
	        ("Name", profile_info["name"]),
	        ("Date of Birth", profile_info["dob"]),
	        ("Address", profile_info["address"]),
	        ("Age", profile_info["age"]),
	        ("Occupation", profile_info["occupation"]),
	        ("Contact No", profile_info["contact"]),
	        ("Email", profile_info["email"]),
	    ]
	    for label, value in details:
	        ctk.CTkLabel(details_frame,text=f"{label}: {value}",font=("Courier New", 20),
	text_color="#3E4E50",).pack(anchor="w", pady=5)
	    button_frame = ctk.CTkFrame(self.root, fg_color="#F1F8E9", corner_radius=15, width=600)
	    button_frame.place(relx=0.5, rely=0.65, anchor="center")
	    edit_profile_icon = ctk.CTkImage(Image.open("edit_icon.png"), size=(40, 40))
	    change_password_icon = ctk.CTkImage(Image.open("change_password_icon.png"), size=(40, 40))
	    ctk.CTkButton(button_frame,text="Edit Profile",image=edit_profile_icon,compound="left",font=("Arial", 16, "bold"),fg_color="#0078D4",text_color="white",hover_color="#0056A3",command=self.edit_profile,width=200,).grid(row=0, column=0, padx=20, pady=10)
	    ctk.CTkButton(button_frame,text="Change Password",image=change_password_icon,compound="left",font=("Arial", 16, "bold"),fg_color="#0078D4",text_color="white",hover_color="#0056A3",command=self.change_password,width=200,).grid(row=0, column=1, padx=20, pady=10)
	    ctk.CTkButton(self.root,text="Back",font=("Arial", 14, "bold"),fg_color="#0078D4",text_color="white",hover_color="#0056A3",
command=self.create_main_page,width=150,).place(relx=0.5, rely=0.85, anchor="center")

    def edit_profile(self):
	    self.clear_widgets()
	    ctk.CTkLabel(self.root, text="Edit Profile", font=("Courier New", 28, "bold")).pack(pady=20)
	    profile_info = self.profile_data[self.current_user]
	    form_frame = ctk.CTkFrame(self.root)
	    form_frame.pack(pady=20)
	    ctk.CTkLabel(form_frame, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky=ctk.W)
	    name_entry = ctk.CTkEntry(form_frame)
	    name_entry.grid(row=0, column=1, padx=10, pady=10)
	    name_entry.insert(0, profile_info['name'])
	    ctk.CTkLabel(form_frame, text="Date of Birth:").grid(row=1, column=0, padx=10, pady=10, sticky=ctk.W)
	    dob_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
	    dob_entry.grid(row=1, column=1, padx=10, pady=10)
	    dob_entry.set_date(datetime.strptime(profile_info['dob'], "%Y-%m-%d"))
	    ctk.CTkLabel(form_frame, text="Address:").grid(row=2, column=0, padx=10, pady=10, sticky=ctk.W)
	    address_entry = ctk.CTkEntry(form_frame)
	    address_entry.grid(row=2, column=1, padx=10, pady=10)
	    address_entry.insert(0, profile_info['address'])
	    ctk.CTkLabel(form_frame, text="Occupation:").grid(row=3, column=0, padx=10, pady=10, sticky=ctk.W)
	    occupation_entry = ctk.CTkEntry(form_frame)
	    occupation_entry.grid(row=3, column=1, padx=10, pady=10)
	    occupation_entry.insert(0, profile_info['occupation'])
	    ctk.CTkLabel(form_frame, text="Contact No:").grid(row=4, column=0, padx=10, pady=10, sticky=ctk.W)
	    contact_entry = ctk.CTkEntry(form_frame)
	    contact_entry.grid(row=4, column=1, padx=10, pady=10)
	    contact_entry.insert(0, profile_info['contact'])
	    self.age_entry = ctk.CTkEntry(form_frame, state='readonly') 
	    ctk.CTkLabel(form_frame, text="Age:").grid(row=5, column=0, padx=10, pady=10, sticky=ctk.W)
	    self.age_entry.grid(row=5, column=1, padx=10, pady=10)
	    dob_entry.bind("<FocusOut>", lambda event: self.calculate_age(dob_entry.get(), self.age_entry))
	    ctk.CTkButton(self.root, text="Save Changes", command=lambda: self.save_profile_changes(
	        name_entry.get(), dob_entry.get(), address_entry.get(), occupation_entry .get(), contact_entry.get()
	    )).pack(pady=20)
	    ctk.CTkButton(self.root, text="Back", command=self.view_profile).pack(pady=10)
        
    def save_profile_changes(self, name, dob, address, occupation, contact):
        age = self.calculate_age(dob, self.age_entry)
        self.profile_data[self.current_user] = {
            'name': name,
            'dob': dob,
            'address': address,
            'age': age,  
            'occupation': occupation,
            'contact': contact,
            'email': self.profile_data[self.current_user]['email'],  
            'photo': self.profile_data[self.current_user]['photo']  
        }
        self.save_profile_to_file()
        messagebox.showinfo("Success", "Profile updated successfully!")
        self.view_profile()
    
    def change_password(self):
        self.clear_widgets()
        ctk.CTkLabel(self.root, text="Change Password", font=("Courier New", 28, "bold")).pack(pady=20)
        form_frame = ctk.CTkFrame(self.root)
        form_frame.pack(pady=20)
        ctk.CTkLabel(form_frame, text="Old Password:").grid(row=0, column=0, padx=10, pady=10, sticky=ctk.W)
        old_password_entry = ctk.CTkEntry(form_frame, show='*')
        old_password_entry.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(form_frame, text="New Password:").grid(row=1, column=0, padx=10, pady=10, sticky=ctk.W)
        new_password_entry = ctk.CTkEntry(form_frame, show='*')
        new_password_entry.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(self.root, text="Change Password", command=lambda: self.handle_change_password(
            old_password_entry.get(), new_password_entry.get()
        )).pack(pady=20)
        ctk.CTkButton(self.root, text="Back", command=self.view_profile).pack(pady=10)

    def handle_change_password(self, old_password, new_password):
        if self.user_data.get(self.current_user) == old_password:
            self.user_data[self.current_user] = new_password
            self.save_user_data()
            self.send_email(self.profile_data[self.current_user]['email'], "Password Change Notification", f"""
            <html>
                <body>
                    <h2 style="color: #4CAF50;">Password Change Notification</h2>
                    <p>Dear {self.profile_data[self.current_user]['name']},</p>
                    <p>Your password has been successfully changed.</p>
                    <p>If you did not make this change, please contact support immediately.</p>
                    <p>Best Regards,<br>IKIGAI DILIGENCE</p>
                </body>
            </html>
            """)
            messagebox.showinfo("Success", "Password changed successfully!")
            self.view_profile()
        else:
            messagebox.showerror("Error", "Old password is incorrect.")
            
    def send_email(self, to_email, subject, message):
	        try:
	            sender_email = "reneb2406@gmail.com"
	            sender_password = "rnaw jmsj cjxh lubz" 
	            msg = MIMEMultipart()
	            msg['From'] = sender_email
	            msg['To'] = to_email
	            msg['Subject'] = subject
	
	            msg.attach(MIMEText(message, 'html'))
	
	            with smtplib.SMTP('smtp.gmail.com', 587) as server:
	                server.starttls()
	                server.login(sender_email, sender_password)
	                server.send_message(msg)
	
	            print(f"Email sent successfully to {to_email}!")
	        except Exception as e:
	            print(f"Failed to send email: {e}")

    def send_birthday_greeting(self, user_profile):
        subject = "Happy Birthday!"
        message = f"""
        <html>
            <body>
                <h2 style="color: #4CAF50;">Happy Birthday, {user_profile['name']}!</h2>
                <p>Wishing you a wonderful day filled with joy and happiness.</p>
                <p>Best Regards,<br>IKIGAI DILIGENCE</p>
            </body>
        </html>
        """
        self.send_email(user_profile['email'], subject, message)

    def send_task_reminder(self, user_profile, task):
	    subject = "Task Reminder: Due Today!"
	    current_time = datetime.now()
	    due_time = datetime.strptime(task['due_date'], "%Y-%m-%d")
	    if not task.get('due_time'):
	        due_time = due_time.replace(hour=23, minute=59, second=59)
	    else:
	        due_time = datetime.strptime(f"{task['due_date']} {task['due_time']}", "%Y-%m-%d %H:%M:%S")
	    time_left = due_time - current_time
	    total_minutes = time_left.total_seconds() // 60
	    hours_left = total_minutes // 60
	    minutes_left = total_minutes % 60
	    time_remaining = f"{int(hours_left)} hour(s) and {int(minutes_left)} minute(s)"
	    message = f"""
	    <html>
	        <body>
	            <h2 style="color: #FF5733;">Reminder: Task '{task['name']}' is Due Today!</h2>
	            <p><strong>Description:</strong> {task['description']}</p>
	            <p><strong>Time Remaining:</strong> {time_remaining}</p>
	            <p>Please make sure to complete it on time.</p>
	            <p>If you have already completed this task, kindly disregard this reminder.</p>
	            <p>Best Regards,<br>IKIGAI DILIGENCE</p>
	        </body>
	    </html>
	    """
	    self.send_email(user_profile['email'], subject, message)

    def check_and_send_notifications(self):
        current_date = datetime.now().date()
        for username, profile in self.profile_data.items():
            if username == self.current_user:
                dob = datetime.strptime(profile['dob'], "%Y-%m-%d").date()
                if dob.month == current_date.month and dob.day == current_date.day:
                    self.send_birthday_greeting(profile)
                for task in self.task_data.values():
                    if task['user'] == username and not task['completed']:
                        due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
                        if due_date == current_date:
                            self.send_task_reminder(profile, task)
                        elif due_date == current_date - timedelta(days=1):
                        	self.send_task_reminder(profile, task)
                        elif due_date < current_date:
                            overdue_message = f"""
                            <html>
                                <body>
                                    <h2 style="color: #FF0000;">Overdue Task Notification</h2>
                                    <p>Task '{task['name']}' was due on {due_date}! Please check.</p>
                                    <p>Best Regards,<br>IKIGAI DILIGENCE</p>
                                </body>
                            </html>
                            """
                            self.send_email(profile['email'], "Overdue Task Notification", overdue_message)

    def create_notification_window(self):
	    self.clear_widgets()
	    self.check_and_send_notifications()
	    header_frame = ctk.CTkFrame(self.root, fg_color="#0078D4", corner_radius=10)
	    header_frame.pack(fill="x", pady=10, padx=10)
	    header_label = ctk.CTkLabel(header_frame, text="Notifications", font=("Courier New", 28, "bold"), text_color="white")
	    header_label.pack(pady=10)
	    content_frame = ctk.CTkScrollableFrame(self.root, width=600, height=400, fg_color="#f5f5f5", corner_radius=10)
	    content_frame.pack(fill="both", expand=True, padx=20, pady=10)
	    notifications = []
	    birthday_wishes = []
	    current_date = datetime.now().date()
	    for task in self.task_data.values():
	        if task['user'] == self.current_user and not task['completed']:
	            due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
	            if due_date == current_date:
	                notifications.append(f"Task '{task['name']}' is due today! Please complete it.")
	            elif due_date < current_date:
	                notifications.append(f"Task '{task['name']}' was due on {due_date}!")
	            reminder_date = task.get('reminder_date')
	            if reminder_date:
	                reminder_date = datetime.strptime(reminder_date, "%Y-%m-%d").date()
	                if reminder_date == current_date:
	                    notifications.append(f"Reminder: Task '{task['name']}' is due today! Please complete the task soon.")
	    for username, profile in self.profile_data.items():
	        if username == self.current_user:
	            dob = datetime.strptime(profile['dob'], "%Y-%m-%d").date()
	            if dob.month == current_date.month and dob.day == current_date.day:
	                birthday_wishes.append(f"Wish You A Happy Birthday, {profile['name']}!")
	    if notifications or birthday_wishes:
	        if notifications:
	            for message in notifications:
	                self.create_notification_card(message, content_frame)
	        if birthday_wishes:
	            for message in birthday_wishes:
	                self.create_notification_card(message, content_frame)
	    else:
	        no_notification_label = ctk.CTkLabel(content_frame, text="No new notifications.", font=("Courier New", 16, "italic"), text_color="gray")
	        no_notification_label.pack(pady=20)
	    footer_frame = ctk.CTkFrame(self.root, fg_color="#0078D4")
	    footer_frame.pack(side="bottom", fill="x", pady=10, padx=10)
	    refresh_button = ctk.CTkButton(footer_frame, text="Refresh", command=self.create_notification_window, fg_color="#FFFFFF", text_color="#0078D4", font=("Courier New", 14, "bold"))
	    refresh_button.pack(side=ctk.LEFT, padx=10, pady=10)
	    back_button = ctk.CTkButton(footer_frame, text="Back", command=self.create_main_page, fg_color="#FFFFFF", text_color="#0078D4", font=("Courier New", 14, "bold"))
	    back_button.pack(side=ctk.RIGHT, padx=10, pady=10, anchor="center")
	
    def create_notification_card(self, message, parent_frame):
	    card_frame = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color="#FFFFFF", border_color="#0078D4", border_width=1)
	    card_frame.pack(pady=5, padx=10, fill=ctk.X)
	    message_label = ctk.CTkLabel(card_frame, text=message, font=("Courier New", 16), wraplength=550, text_color="#333333")
	    message_label.pack(pady=10, padx=10)
	    timestamp_label = ctk.CTkLabel(card_frame, text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), font=("Courier New", 12, "italic"), text_color="gray")
	    timestamp_label.pack(pady=(0, 10), padx=10)

    def add_task(self):
        self.clear_widgets()
        header_frame = ctk.CTkFrame(self.root, fg_color="#0078D4", corner_radius=10)
        header_frame.pack(fill="x", pady=10, padx=10)
        header_label = ctk.CTkLabel(header_frame, text="Add Task", font=("Courier New", 28, "bold"), text_color="white")
        header_label.pack(pady=10)
        form_frame = ctk.CTkFrame(self.root)
        form_frame.pack(pady=20)
        ctk.CTkLabel(form_frame, text="Task Name:").grid(row=0, column=0, padx=10, pady=10, sticky=ctk.W)
        task_name_entry = ctk.CTkEntry(form_frame)
        task_name_entry.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(form_frame, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky=ctk.W)
        task_description_entry = ctk.CTkEntry(form_frame)
        task_description_entry.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkLabel(form_frame, text="Due Date:").grid(row=2, column=0, padx=10, pady=10, sticky=ctk.W)
        task_due_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        task_due_date_entry.grid(row=2, column=1, padx=10, pady=10)
        ctk.CTkLabel(form_frame, text="Reminder Date (optional):").grid(row=3, column=0, padx=10, pady=10, sticky=ctk.W)
        task_reminder_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
        task_reminder_date_entry.grid(row=3, column=1, padx=10, pady=10)
        ctk.CTkButton(self.root, text="Add Task", command=lambda: self.save_task(
            task_name_entry.get(), task_description_entry.get(),
            task_due_date_entry.get(), task_reminder_date_entry.get()
        )).pack(pady=20)
        ctk.CTkButton(self.root, text="Back", command=self.create_main_page).pack(pady=10)

    def save_task(self, name, description, due_date_str, reminder_date_str):
        if name and description and due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                reminder_date = datetime.strptime(reminder_date_str, "%Y-%m-%d").date() if reminder_date_str else None
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use yyyy-mm-dd.")
                self.add_task()
                return
            task_id = str(len(self.task_data) + 1)
            self.task_data[task_id] = {
                'name': name,
                'description': description,
                'due_date': due_date.isoformat(),
                'reminder_date': reminder_date.isoformat() if reminder_date else None,
                'completed': False,
                'remarks': [],
                'proof': None,
                'user': self.current_user
            }
            self.save_task_data()
            self.create_main_page()
        else:
            messagebox.showerror("Error", "All fields are required.")
            self.add_task()

    def upload_proof(self, task_id):
	    task = self.task_data.get(task_id)
	    if not task:
	        messagebox.showerror("Error", "Task not found.")
	        return
	    file_path = filedialog.askopenfilename(
	        title="Select Proof File",
	        filetypes=[("All Files", "*.*"), ("PDF Files", "*.pdf"), ("Image Files", "*.png;*.jpg;*.jpeg")]
	    )
	    if file_path:
	        folder_id = self.get_or_create_proofs_folder()
	        file_metadata = {
	            'name': os.path.basename(file_path),
	            'parents': [folder_id]  
	        }
	        media = MediaFileUpload(file_path, resumable=True)
	        uploaded_file = self.drive_service.files().create(
	            body=file_metadata,
	            media_body=media,
	            fields='id, name'
	        ).execute()
	        task['proof'] = {
	            'file_id': uploaded_file.get('id'),
	            'file_name': uploaded_file.get('name')
	        }
	        self.save_task_data()
	        messagebox.showinfo("Success", "Proof uploaded successfully.")
	    else:
	        messagebox.showwarning("Warning", "No file selected. Please try again.")
		
    def get_or_create_proofs_folder(self):
	    results = self.drive_service.files().list(
	        q="mimeType='application/vnd.google-apps.folder' and name='proofs'",
	        fields="files(id, name)"
	    ).execute()
	    items = results.get('files', [])
	    if items:
	        return items[0]['id']  
	    else:
	        file_metadata = {
	            'name': 'proofs',
	            'mimeType': 'application/vnd.google-apps.folder'
	        }
	        folder = self.drive_service.files().create(body=file_metadata, fields='id').execute()
	        return folder.get('id')  
	
    def edit_task(self, task_id):
	    task = self.task_data.get(task_id)
	    if not task:
	        messagebox.showerror("Error", "Task not found.")
	        return
	    self.clear_widgets()
	    ctk.CTkLabel(self.root, text="Edit Task", font=("Courier New", 28, "bold")).pack(pady=20)
	    form_frame = ctk.CTkFrame(self.root)
	    form_frame.pack(pady=20)
	    ctk.CTkLabel(form_frame, text="Task Name:").grid(row=0, column=0, padx=10, pady=10, sticky=ctk.W)
	    task_name_entry = ctk.CTkEntry(form_frame)
	    task_name_entry.grid(row=0, column=1, padx=10, pady=10)
	    task_name_entry.insert(0, task['name'])
	    ctk.CTkLabel(form_frame, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky=ctk.W)
	    task_description_entry = ctk.CTkEntry(form_frame)
	    task_description_entry.grid(row=1, column=1, padx=10, pady=10)
	    task_description_entry.insert(0, task['description'])
	    ctk.CTkLabel(form_frame, text="Due Date:").grid(row=2, column=0, padx=10, pady=10, sticky=ctk.W)
	    due_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
	    due_date_entry.grid(row=2, column=1, padx=10, pady=10)
	    due_date_entry.set_date(datetime.strptime(task['due_date'], "%Y-%m-%d"))
	    ctk.CTkLabel(form_frame, text="Reminder Date (optional):").grid(row=3, column=0, padx=10, pady=10, sticky=ctk.W)
	    reminder_date_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd')
	    reminder_date_entry.grid(row=3, column=1, padx=10, pady=10)
	    if task.get('reminder_date'):
	        reminder_date_entry.set_date(datetime.strptime(task['reminder_date'], "%Y-%m-%d"))
	    ctk.CTkButton(
	        self.root,
	        text="Save Changes",
	        command=lambda: self.save_edited_task(
	            task_id,
	            task_name_entry.get(),
	            task_description_entry.get(),
	            due_date_entry.get(),
	            reminder_date_entry.get()
	        )
	    ).pack(pady=20)
	    ctk.CTkButton(self.root, text="Back", command=self.load_tasks).pack(pady=10)
	
    def save_edited_task(self, task_id, name, description, due_date, reminder_date):
	    task = self.task_data.get(task_id)
	    if not task:
	        messagebox.showerror("Error", "Task not found.")
	        return	
	    task['name'] = name
	    task['description'] = description
	    try:
	        datetime.strptime(due_date, "%Y-%m-%d")
	        task['due_date'] = due_date
	    except ValueError:
	        messagebox.showerror("Error", "Invalid Due Date format. Use YYYY-MM-DD.")
	        return	
	    if reminder_date:
	        try:
	            datetime.strptime(reminder_date, "%Y-%m-%d")
	            task['reminder_date'] = reminder_date
	        except ValueError:
	            messagebox.showerror("Error", "Invalid Reminder Date format. Use YYYY-MM-DD.")
	            return
	    self.save_task_data()
	    messagebox.showinfo("Success", "Task updated successfully!")
	    self.load_tasks()
    
    def load_tasks(self):
	    self.clear_widgets()
	    self.create_top_bar(title="Tasks", color="#0078D4")
	    action_frame = ctk.CTkFrame(self.root)
	    action_frame.pack(pady=10)
	    search_icon = ctk.CTkImage(Image.open("search_icon.png"), size=(20, 20))
	    refresh_icon = ctk.CTkImage(Image.open("refresh_icon.png"), size=(20, 20))
	    search_entry = ctk.CTkEntry(action_frame, width=300, placeholder_text="Search tasks...")
	    search_entry.grid(row=0, column=0, padx=10, pady=10)
	    ctk.CTkButton(action_frame, image=search_icon, text="Search", command=lambda: self.search_task(search_entry.get()), compound="top").grid(row=0, column=1, padx=10, pady=10)
	    ctk.CTkButton(action_frame, image=refresh_icon, text="Refresh", command=self.populate_task_cards, compound="top").grid(row=0, column=2, padx=10, pady=10)
	    delete_download_frame = ctk.CTkFrame(self.root)
	    delete_download_frame.pack(pady=10)
	    delete_icon = ctk.CTkImage(Image.open("delete_icon.png"), size=(20, 20))
	    download_icon = ctk.CTkImage(Image.open("download1_icon.png"), size=(20, 20))
	    ctk.CTkButton(delete_download_frame, image=delete_icon, text="Delete Task", command=self.delete_selected_task, compound="top").grid(row=0, column=0, padx=10, pady=10)
	    ctk.CTkButton(delete_download_frame, image=download_icon, text="Download Tasks", command=self.download_tasks, compound="top").grid(row=0, column=1, padx=10, pady=10)
	    tab_frame = ctk.CTkFrame(self.root)
	    tab_frame.pack(pady=10, fill="both", expand=True)
	    self.task_tab_control = ttk.Notebook(tab_frame)
	    self.incomplete_tab = ttk.Frame(self.task_tab_control)
	    self.completed_tab = ttk.Frame(self.task_tab_control)
	    self.task_tab_control.add(self.incomplete_tab, text="Incomplete Tasks")
	    self.task_tab_control.add(self.completed_tab, text="Completed Tasks")
	    self.task_tab_control.pack(fill="both", expand=True)
	    self.incomplete_task_frame = ctk.CTkScrollableFrame(self.incomplete_tab, corner_radius=10)
	    self.incomplete_task_frame.pack(fill="both", expand=True, padx=10, pady=10)
	    self.completed_task_frame = ctk.CTkScrollableFrame(self.completed_tab, corner_radius=10)
	    self.completed_task_frame.pack(fill="both", expand=True, padx=10, pady=10)
	    self.selected_task_id = None
	    self.selected_task_checkbox = None
	    self.populate_task_cards()
	    footer_frame = ctk.CTkFrame(self.root)
	    footer_frame.pack(pady=10)
	    ctk.CTkButton(footer_frame, text="Edit Task", command=self.edit_selected_task).pack(side="left", padx=10)
	    ctk.CTkButton(footer_frame, text="Add Remark", command=self.add_remark_to_selected_task).pack(side="left", padx=10)
	    ctk.CTkButton(footer_frame, text="Upload Proof", command=self.upload_proof_for_selected_task).pack(side="left", padx=10)
	    ctk.CTkButton(footer_frame, text="View Proof", command=self.view_proof_for_selected_task).pack(side="left", padx=10)
	    ctk.CTkButton(footer_frame, text="Mark as Completed", command=self.mark_as_completed).pack(side="left", padx=10)
	    ctk.CTkButton(footer_frame, text="Back", command=self.create_main_page).pack(side="left", padx=10)
	
    def populate_task_cards(self):
	    for widget in self.incomplete_task_frame.winfo_children():
	        widget.destroy()
	    for widget in self.completed_task_frame.winfo_children():
	        widget.destroy()
	    current_date = datetime.now().date()
	    incomplete_tasks = [
	        (task_id, task) for task_id, task in self.task_data.items()
	        if task['user'] == self.current_user and not task['completed']
	    ]
	    incomplete_tasks.sort(key=lambda x: datetime.strptime(x[1]['due_date'], "%Y-%m-%d").date())
	    for task_id, task in incomplete_tasks:
	        due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
	        color = "#A8D5BA"  
	        status_label_text = None
	        if due_date < current_date:
	            color = "#F28C8C"  
	            status_label_text = "OVERDUE TASK"
	        elif due_date == current_date:
	            color = "#FBCEB1" 
	            status_label_text = "DUE TODAY"
	        task_frame = ctk.CTkFrame(self.incomplete_task_frame, corner_radius=10, fg_color=color, width=600)
	        task_frame.pack(pady=10, padx=10, fill="x", expand=True)
	        checkbox = ctk.CTkCheckBox(task_frame, text="")
	        checkbox.pack(side="right", padx=10, pady=10)    
	        task_title = ctk.CTkLabel(task_frame, text=f"{task['name']}", font=("Arial", 20, "bold"), text_color="#000000")
	        task_title.pack(anchor="w", padx=10, pady=5)
	        task_details = f"""
	        DESCRIPTION: {task['description']}
	        DUE DATE: {task['due_date']}
	        REMINDER DATE: {task.get('reminder_date', 'None')}
	        REMARKS: {'; '.join(task['remarks']) or 'None'}
	        PROOF STATUS: {'Uploaded' if task.get('proof') else 'Not Uploaded'}
	        """
	        task_detail_label = ctk.CTkLabel(task_frame, text=task_details, justify="left", wraplength=550, text_color="#000000")
	        task_detail_label.pack(anchor="w", padx=10, pady=5)
	        if status_label_text:
	            status_label = ctk.CTkLabel(task_frame, text=status_label_text, font=("Arial", 12, "bold"), text_color="#000000")
	            status_label.pack(anchor="e", padx=10, pady=5)
	        task_frame.bind("<Button-1>", lambda e, t_id=task_id, t_frame=task_frame, cb=checkbox: self.select_task(t_id, t_frame, cb))
	        for child in task_frame.winfo_children():
	            child.bind("<Button-1>", lambda e, t_id=task_id, t_frame=task_frame, cb=checkbox: self.select_task(t_id, t_frame, cb))
	    for task_id, task in self.task_data.items():
	        if task['user'] == self.current_user and task['completed']:
	            task_frame = ctk.CTkFrame(self.completed_task_frame, corner_radius=10, fg_color="#E8F5E9", width=600)
	            task_frame.pack(pady=10, padx=10, fill="x", expand=True)
	
	            checkbox = ctk.CTkCheckBox(task_frame, text="")
	            checkbox.pack(side="right", padx=10, pady=10)
	
	            task_title = ctk.CTkLabel(task_frame, text=f"{task['name']}", font=("Arial", 20, "bold"),text_color="#000000")
	            task_title.pack(anchor="w", padx=10, pady=5)
	            task_details = f"""
	            DESCRIPTION :  {task['description']}
	            DUE DATE :  {task['due_date']}
	            REMINDER DATE :  {task.get('reminder_date', 'None')}
	            REMARKS :  {'; '.join(task['remarks']) or 'None'}
	            PROOF STATUS : {'Uploaded' if task.get('proof') else 'Not Uploaded'}
	            """
	            task_detail_label = ctk.CTkLabel(task_frame, text=task_details, justify="left", wraplength=550,text_color="#000000")
	            task_detail_label.pack(anchor="w", padx=10, pady=5)
	            task_frame.bind("<Button-1>", lambda e, t_id=task_id, t_frame=task_frame, cb=checkbox: self.select_task(t_id, t_frame, cb))
	            for child in task_frame.winfo_children():
	                child.bind("<Button-1>", lambda e, t_id=task_id, t_frame=task_frame, cb=checkbox: self.select_task(t_id, t_frame, cb))
	
    def select_task(self, task_id, task_frame, checkbox):
	    if self.selected_task_id:
	        prev_frame = self.selected_task_frame
	        prev_checkbox = self.selected_task_checkbox
	        if prev_frame and prev_frame.winfo_exists():
	            prev_task = self.task_data[self.selected_task_id]
	            if prev_task['completed']:
	                prev_frame.configure(fg_color="#A8D5BA")
	            else:
	                prev_due_date = datetime.strptime(prev_task['due_date'], "%Y-%m-%d").date()
	                if prev_due_date < datetime.now().date():
	                    prev_frame.configure(fg_color="#F28C8C")  
	                elif prev_due_date == datetime.now().date():
	                    prev_frame.configure(fg_color="#FBCEB1")  
	                else:
	                    prev_frame.configure(fg_color="#A8D5BA")
	            prev_checkbox.deselect()
	    self.selected_task_id = task_id
	    self.selected_task_frame = task_frame
	    self.selected_task_checkbox = checkbox
	    task = self.task_data[task_id]
	    task_frame.configure(fg_color="#D3D3D3")  
	    if task['completed']:
	        task_frame.configure(fg_color="#A8D5BA")  
	    else:
	        due_date = datetime.strptime(task['due_date'], "%Y-%m-%d").date()
	        if due_date < datetime.now().date():
	            task_frame.configure(fg_color="#FFCCCC")  
	        elif due_date == datetime.now().date():
	            task_frame.configure(fg_color="#FFE4B5")  
	        else:
	            task_frame.configure(fg_color="#E8F5E9")
	    checkbox.select()  
     
    def get_selected_task_id(self):
	    return self.selected_task_id
    def search_task(self, query):
	    query = query.lower()
	    for widget in self.incomplete_task_frame.winfo_children():
	        widget.destroy()
	    for widget in self.completed_task_frame.winfo_children():
	        widget.destroy()
	    for task_id, task in self.task_data.items():
	        if task['user'] == self.current_user and (query in task['name'].lower() or query in task['description'].lower()):
	            task_frame = ctk.CTkFrame(
	                self.incomplete_task_frame if not task['completed'] else self.completed_task_frame,
	                corner_radius=10, fg_color="#E8F5E9", width=600, height=200
	            )
	            task_frame.pack(pady=10, padx=10, fill="both", expand=True)
	            checkbox = ctk.CTkCheckBox(task_frame, text="")
	            checkbox.pack(side="right", padx=10, pady=10)
	            task_title = ctk.CTkLabel(task_frame, text=f"{task['name']}", font=("Arial", 20, "bold"))
	            task_title.pack(anchor="w", padx=10, pady=5)
	            task_details = f"""
	            DESCRIPTION :  {task['description']}
	            DUE DATE :  {task['due_date']}
	            REMARKS :  {'; '.join(task['remarks']) or 'None'}
	            PROOF STATUS :  {'Uploaded' if task.get('proof') else 'Not Uploaded'}
	            """
	            task_detail_label = ctk.CTkLabel(task_frame, text=task_details, justify="left")
	            task_detail_label.pack(anchor="w", padx=10, pady=5)
	
    def delete_selected_task(self):    
	    task_id = self.get_selected_task_id()
	    if task_id:
	        confirm = messagebox.askyesno("Delete Task", "Are you sure you want to delete this task?")
	        if confirm:
	            del self.task_data[task_id]
	            self.save_task_data()
	            self.populate_task_cards()
	    else:
	        messagebox.showwarning("Warning", "Please select a task to delete.")
	        
    def download_tasks(self):
	    incomplete_tasks = [task for task_id, task in self.task_data.items() if not task['completed'] and task['user'] == self.current_user]
	    completed_tasks = [task for task_id, task in self.task_data.items() if task['completed'] and task['user'] == self.current_user]
	    pdf_file_path = f"{self.current_user}_tasks.pdf"
	    pdf = SimpleDocTemplate(pdf_file_path, pagesize=letter)
	    elements = []
	    header_style = ParagraphStyle(name='Header', fontSize=24, alignment=1, fontName='Helvetica-Bold')
	    elements.append(Paragraph("IKIGAI DILIGENCE", header_style))
	    elements.append(Spacer(1, 12))
	    quote_style = ParagraphStyle(name='Quote', fontSize=14, alignment=1, fontName='Helvetica-Oblique')
	    elements.append(Paragraph("Your tasks, your journey, your diligence.", quote_style))
	    elements.append(Spacer(1, 24))
	    personal_details_style = ParagraphStyle(name='PersonalDetails', fontSize=18, fontName='Helvetica-Bold')
	    elements.append(Paragraph("Personal Details", personal_details_style))
	    elements.append(Spacer(1, 12))
	    user_profile = self.profile_data[self.current_user]
	    details = [
	        ("Name:", user_profile['name']),
	        ("Date of Birth:", user_profile['dob']),
	        ("Age:", user_profile['age']),
	        ("Address:", user_profile['address']),
	        ("Contact No:", user_profile['contact']),
	        ("Email:", user_profile['email']),
	    ]
	    for label, value in details:
	        elements.append(Paragraph(f"{label} {value}", ParagraphStyle(name='Detail', fontSize=12)))
	    elements.append(Spacer(1, 24))
	    task_details_style = ParagraphStyle(name='TaskDetails', fontSize=18, fontName='Helvetica-Bold')
	    elements.append(Paragraph("Task Details", task_details_style))
	    elements.append(Spacer(1, 12))
	    if incomplete_tasks:
	        elements.append(Paragraph("Details of Incompleted Tasks", task_details_style))
	        elements.append(Spacer(1, 12))
	        incomplete_table_data = [["S.No", "Task Name", "Description", "Remarks", "Due Date", "Proof"]]
	        for index, task in enumerate(incomplete_tasks, start=1):
	            incomplete_table_data.append([
	                index,
	                task['name'],
	                task['description'],
	                '; '.join(task['remarks']),
	                task['due_date'],
	                'Uploaded' if task.get('proof') else 'Not Uploaded'
	            ])
	        incomplete_table = Table(incomplete_table_data)
	        incomplete_table.setStyle(TableStyle([
	            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
	            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
	            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
	            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
	            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
	            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
	            ('GRID', (0, 0), (-1, -1), 1, colors.black),
	        ]))
	        elements.append(incomplete_table)
	        elements.append(Spacer(1, 24))
	
	    if completed_tasks:
	        elements.append(Paragraph("Details of Completed Tasks", task_details_style))
	        elements.append(Spacer(1, 12))
	        completed_table_data = [["S.No", "Task Name", "Description", "Remarks", "Due Date", "Proof"]]
	        for index, task in enumerate(completed_tasks, start=1):
	            completed_table_data.append([
	                index,
	                task['name'],
	                task['description'],
	                '; '.join(task['remarks']),
	                task['due_date'],
	                'Uploaded' if task.get('proof') else 'Not Uploaded'
	            ])
	        completed_table = Table(completed_table_data)
	        completed_table.setStyle(TableStyle([
	            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
	            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
	            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
	            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
	            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
	            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
	            ('GRID', (0, 0), (-1, -1), 1, colors.black),
	        ]))
	        elements.append(completed_table)
	        elements.append(Spacer(1, 24))
	    download_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	    download_date = datetime.now().date().strftime("%Y-%m-%d")
	    watermark_style = ParagraphStyle(name='Watermark', fontSize=10, alignment=1, textColor=colors.grey)
	    elements.append(Spacer(1, 24))
	    elements.append(Paragraph(f"Downloaded on: {download_time}", watermark_style))
	    elements.append(Paragraph(f"Date: {download_date}", watermark_style))
	
	    pdf_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                   filetypes=[("PDF files", "*.pdf")],
                                                   title="Save Tasks As")
	    if not pdf_file_path: 
	        messagebox.showwarning("Cancelled", "Download cancelled.")
	        return
	    pdf.build(elements)
	    messagebox.showinfo("Success", f"Tasks downloaded successfully as {pdf_file_path}!")
    
    def edit_selected_task(self):
	    if self.selected_task_id:
	        self.edit_task(self.selected_task_id)
	    else:
	        messagebox.showwarning("Warning", "Please select a task to edit.")
	
    def add_remark(self, task_id):
	    task = self.task_data.get(task_id)
	    if not task:
	        messagebox.showerror("Error", "Task not found.")
	        return
	    remark = simpledialog.askstring("Add Remark", "Enter your remark:")
	    if remark:
	        task['remarks'].append(remark)
	        self.save_task_data()
	        messagebox.showinfo("Success", "Remark added successfully!")
	        self.populate_task_cards()
	    else:
	        messagebox.showwarning("Warning", "No remark entered.")
    
    def add_remark_to_selected_task(self):
	    if self.selected_task_id:
	        self.add_remark(self.selected_task_id)
	    else:
	        messagebox.showwarning("Warning", "Please select a task to add a remark.")
	
    def upload_proof_for_selected_task(self):
	    task_id = self.get_selected_task_id()
	    if task_id:
	        file_path = filedialog.askopenfilename(
	            title="Select Proof File",
	            filetypes=[("All Files", "*.*"), ("PDF Files", "*.pdf"), ("Image Files", "*.png;*.jpg;*.jpeg")]
	        )
	        if file_path:
	            try:
	                file_metadata = {'name': os.path.basename(file_path)}
	                media = MediaFileUpload(file_path, resumable=True)
	                uploaded_file = self.drive_service.files().create(
	                    body=file_metadata, media_body=media, fields='id, name'
	                ).execute()
	                self.task_data[task_id]['proof'] = {
	                    'file_id': uploaded_file.get('id'),
	                    'file_name': uploaded_file.get('name')
	                }
	                self.save_task_data()
	                messagebox.showinfo("Success", "Proof uploaded successfully.")
	                self.populate_task_cards()
	            except Exception as e:
	                messagebox.showerror("Error", f"Failed to upload proof: {str(e)}")
	        else:
	            messagebox.showwarning("Warning", "No file selected. Please try again.")
	    else:
	        messagebox.showwarning("Warning", "Please select a task to upload proof.")

    def view_proof_for_selected_task(self):
	    task_id = self.get_selected_task_id()
	    if task_id:
	        proof_info = self.task_data[task_id].get('proof')
	        if proof_info:
	            file_id = proof_info.get('file_id')
	            file_name = proof_info.get('file_name', 'downloaded_file') 
	            try:
	                if platform.system() == "Linux" and "ANDROID_STORAGE" in os.environ:
	                    temp_file_path = os.path.join('/storage/emulated/0/Download', file_name)
	                else: 
	                    temp_file_path = os.path.join(os.getcwd(), file_name)
	                request = self.drive_service.files().get_media(fileId=file_id)
	                with io.FileIO(temp_file_path, 'wb') as fh:
	                    downloader = MediaIoBaseDownload(fh, request)
	                    done = False
	                    while not done:
	                        status, done = downloader.next_chunk()
	                if platform.system() == "Linux" and "ANDROID_STORAGE" in os.environ:
	                    messagebox.showinfo("File Saved", f"File saved to Downloads folder:\n{temp_file_path}\n"
	                                                      f"Please open it manually from your file manager.")
	                elif platform.system() == "Windows":
	                    os.startfile(temp_file_path) 
	                elif platform.system() == "Darwin":
	                    subprocess.run(['open', temp_file_path], check=True)  
	                else:
	                    subprocess.run(['xdg-open', temp_file_path], check=True)  
	            except Exception as e:
	                messagebox.showerror("Error", f"Failed to view proof: {str(e)}")
	        else:
	            messagebox.showwarning("Warning", "No proof file found for this task.")
	    else:
	        messagebox.showwarning("Warning", "Please select a task to view proof.")

    def mark_as_completed(self):
	    task_id = self.get_selected_task_id()
	    if task_id:
	        task = self.task_data.get(task_id)
	        if not task:
	            messagebox.showerror("Error", "Task not found.")
	            return
	        if not task.get('proof'):
	            messagebox.showwarning("Warning", "Please upload proof before marking the task as completed.")
	            return
	        task['completed'] = True
	        task['completion_date'] = datetime.now().strftime("%Y-%m-%d")
	        self.save_task_data()
	        messagebox.showinfo("Success", "Task marked as completed.")
	        self.populate_task_cards()
	    else:
	        messagebox.showwarning("Warning", "Please select a task to mark as completed.")
    
    def view_productivity(self):
	    self.clear_widgets()
	    ctk.CTkLabel(self.root, text="Productivity", font=("Courier New", 28, "bold")).pack(pady=20)
	
	    task_dates = [datetime.strptime(task['due_date'], "%Y-%m-%d").date() for task in self.task_data.values() if task['user'] == self.current_user]
	    completed_dates = [datetime.strptime(task['due_date'], "%Y-%m-%d").date() for task in self.task_data.values() if task['completed'] and task['user'] == self.current_user]
	    fig, ax = plt.subplots()
	    ax.hist(task_dates, bins=30, alpha=0.5, label='Tasks Due', color='blue')
	    ax.hist(completed_dates, bins=30, alpha=0.5, label='Tasks Completed', color='green')
	    ax.set_xlabel('Date')
	    ax.set_ylabel('Number of Tasks')
	    ax.set_title('Task Due Dates vs Completed Dates')
	    ax.legend()
	    canvas = FigureCanvasTkAgg(fig, master=self.root)
	    canvas.draw()
	    canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)
	    button_frame = ctk.CTkFrame(self.root)
	    button_frame.pack(side=ctk.TOP, anchor='ne', padx=20, pady=(0, 10))
	    download_icon = ctk.CTkImage(Image.open("download_icon.png"), size=(20, 20))
	    ctk.CTkButton(button_frame, text="Download Graph", image=download_icon, compound="left", command=self.download_productivity_report).pack(pady=10)
	    ctk.CTkButton(self.root, text="Back", command=self.create_main_page).pack(pady=10)
	
    def download_productivity_report(self):
	    pdf = FPDF()
	    pdf.set_auto_page_break(auto=True, margin=15)
	    pdf.add_page()
	    pdf.rect(5, 5, 200, 287)  
	    pdf.set_font("Arial", 'B', 24)
	    pdf.cell(0, 10, "IKIGAI DILIGENCE", ln=True, align='C')
	    pdf.ln(5)
	    pdf.set_font("Arial", 'I', 14)
	    pdf.set_text_color(100, 100, 255) 
	    pdf.cell(0, 10, "Your tasks, your journey, your diligence.", ln=True, align='C')
	    pdf.ln(10)  
	    pdf.set_font("Arial", 'B', 18)
	    pdf.cell(0, 10, "Personal Details", ln=True, border=True)
	    pdf.set_font("Arial", '', 12)
	    pdf.set_text_color(0, 0, 0) 
	    user_profile = self.profile_data[self.current_user]
	    details = [
	        ("Name:", user_profile['name']),
	        ("Date of Birth:", user_profile['dob']),
	        ("Age:", user_profile['age']),
	        ("Address:", user_profile['address']),
	        ("Contact No:", user_profile['contact']),
	        ("Email:", user_profile['email']),
	    ]
	    for label, value in details:
	        pdf.cell(0, 10, f"{label} {value}", ln=True)
	    pdf.ln(10)  
	    pdf.set_font("Arial", 'B', 18)
	    pdf.cell(0, 10, "Productivity Graph", ln=True, border=True)
	    pdf.ln(5)  
	    fig, ax = plt.subplots()
	    task_dates = [datetime.strptime(task['due_date'], "%Y-%m-%d").date() for task in self.task_data.values() if task['user'] == self.current_user]
	    completed_dates = [datetime.strptime(task['due_date'], "%Y-%m-%d").date() for task in self.task_data.values() if task['completed'] and task['user'] == self.current_user]
	    ax.hist(task_dates, bins=30, alpha=0.5, label='Tasks Due', color='blue')
	    ax.hist(completed_dates, bins=30, alpha=0.5, label='Tasks Completed', color='green')
	    ax.set_xlabel('Date')
	    ax.set_ylabel('Number of Tasks')
	    ax.set_title('Task Due Dates vs Completed Dates')
	    ax.legend()
	    graph_path = "temp_productivity_graph.png"
	    fig.savefig(graph_path)
	    plt.close(fig)  
	    pdf.image(graph_path, x=10, y=pdf.get_y(), w=180)  
	    pdf.ln(10)  
	    download_time = datetime.now().strftime("%H:%M:%S")
	    download_date = datetime.now().date().strftime("%Y-%m-%d")
	    watermark_text = f"Downloaded on: {download_time} | Date: {download_date}"
	
	    pdf.set_font("Arial", 'I', 10)  
	    pdf.set_text_color(0, 0, 0)  
	    pdf.set_y(272)  
	    pdf.cell(0, 10, watermark_text, ln=True, align='R') 
	    pdf_file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
	                                                   filetypes=[("PDF files", "*.pdf")],
	                                                   title="Save Productivity Report As")
	    if not pdf_file_path:  
	        messagebox.showwarning("Cancelled", "Download cancelled.")
	        return
	    pdf.output(pdf_file_path)
	    messagebox.showinfo("Success", f"Productivity report downloaded successfully as {pdf_file_path}!")

    def logout(self):
        self.check_and_send_notifications()
        self.current_user = None
        self.show_rating_and_feedback()

    def show_rating_and_feedback(self):
        self.clear_widgets()
        ctk.CTkLabel(self.root, text="Rate Your Experience", font=("Courier New", 28, "bold")).pack(pady=20)
        feedback_frame = ctk.CTkFrame(self.root)
        feedback_frame.pack(pady=20)
        ctk.CTkLabel(feedback_frame, text="How would you rate our app?").grid(row=0, column=0, padx=10, pady=10, sticky=ctk.W)
        rating_var = ctk.IntVar(value=3)
        rating_scale = ctk.CTkSlider(feedback_frame, from_=1, to=5, variable=rating_var)
        rating_scale.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(feedback_frame, text="Feedback (optional):").grid(row=1, column=0, padx=10, pady=10, sticky=ctk.W)
        feedback_entry = ctk.CTkEntry(feedback_frame)
        feedback_entry.grid(row=1, column=1, padx=10, pady=10)
        ctk.CTkButton(self.root, text="Submit Feedback", command=lambda: self.submit_feedback(rating_var.get(), feedback_entry.get())).pack(pady=20)

    def submit_feedback(self, rating, feedback):
        if self.current_user not in self.feedback_data:
            self.feedback_data[self.current_user] = []
        feedback_entry = {
            "rating": rating,
            "feedback": feedback,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.feedback_data[self.current_user].append(feedback_entry)
        self.save_feedback_data()  
        self.show_thank_you(rating, feedback)

    def show_thank_you(self, rating, feedback):
        self.clear_widgets()
        thank_you_label = ctk.CTkLabel(self.root, text="Thank You!", font=("Courier New", 28, "bold"))
        thank_you_label.pack(pady=30, fill=ctk.X)
        feedback_label = ctk.CTkLabel(self.root, text=f"Your rating: {rating}/5\nFeedback: {feedback}")
        feedback_label.pack(pady=20)

        if rating >= 4:
            feedback_message = "We're glad you're enjoying Ikigai Diligence! Your feedback is valuable to us."
        elif rating >= 2:
            feedback_message = "Thank you for your feedback. We'll work hard to improve your experience."
        else:
            feedback_message = "We're sorry to hear you're not happy with our app. We appreciate your feedback and will strive to do better."

        feedback_label = ctk.CTkLabel(self.root, text=feedback_message)
        feedback_label.pack(pady=20)

        ctk.CTkButton(self.root, text="Close", command=self.root.quit).pack(pady=10)

def main():
    root = ctk.CTk()
    app = TaskManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
