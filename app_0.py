from flask import Flask
from flask_mail import Mail
import os
from app import app
# app = Flask(__name__)

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Example SMTP configuration using environment variables
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.example.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() in ('true', '1', 't')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'your_username')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'your_password')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'your_email@example.com')
app.config['MAIL_MAX_EMAILS'] = os.getenv('MAIL_MAX_EMAILS', None)
app.config['MAIL_SUPPRESS_SEND'] = os.getenv('MAIL_SUPPRESS_SEND', 'False').lower() in ('true', '1', 't')
app.config['MAIL_ASCII_ATTACHMENTS'] = os.getenv('MAIL_ASCII_ATTACHMENTS', 'True').lower() in ('true', '1', 't')

mail = Mail(app)

# Print all configuration settings starting with MAIL_
print("Printing all MAIL_ configurations:")
for key in app.config:
    if key.startswith('MAIL_'):
        print(f'{key}: {app.config[key]}')

# Example of sending an email (replace this with your actual email sending code)
from flask_mail import Message

with app.app_context():
    msg = Message(
        subject="Test Email",
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=["chrisjsmez@gmail.com"],
        body="This is a test email sent from Flask-Mail"
    )
    try:
        print("Attempting to send email...")
        mail.send(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
