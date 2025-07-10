import json
import sqlite3
import time
import smtplib
from twilio.rest import Client
import RPi.GPIO as GPIO
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(config["gpio_motion_pin"], GPIO.IN)
GPIO.setup(config["gpio_buzzer_pin"], GPIO.OUT)

# Setup Twilio
twilio_client = Client(config["twilio_account_sid"], config["twilio_auth_token"])

# Setup SQLite database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS motion_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        status TEXT
    )
''')
conn.commit()

# Email alert
def send_email(subject, body):
    try:
        smtp_server = config["email"]["smtp_server"]
        smtp_port = config["email"]["smtp_port"]
        sender = config["email"]["sender_email"]
        password = config["email"]["sender_password"]
        receiver = config["email"]["receiver_email"]

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("[EMAIL] Alert sent successfully.")
    except Exception as e:
        print(f"[EMAIL] Failed to send: {e}")

# Twilio SMS alert
def send_sms(body):
    try:
        message = twilio_client.messages.create(
            body=body,
            from_=config["twilio_from_number"],
            to=config["alert_to_number"]
        )
        print(f"[SMS] Alert sent. SID: {message.sid}")
    except Exception as e:
        print(f"[SMS] Failed to send: {e}")

# Save event in database
def log_event(status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO motion_events (timestamp, status) VALUES (?, ?)", (timestamp, status))
    conn.commit()
    print(f"[DB] Logged event: {timestamp} - {status}")

# Main loop
try:
    print(" Smart Intrusion Detection System Running...")
    while True:
        motion_detected = GPIO.input(config["gpio_motion_pin"])
        if motion_detected:
            print(f"[{datetime.now()}] Motion Detected!")
            log_event("Motion Detected")
            send_sms("⚠️ Motion detected at your premises!")
            send_email("Intrusion Alert", "⚠️ Motion detected at your premises!")
            GPIO.output(config["gpio_buzzer_pin"], GPIO.HIGH)  # Turn on buzzer
            time.sleep(5)
            GPIO.output(config["gpio_buzzer_pin"], GPIO.LOW)
        else:
            print(f"[{datetime.now()}] No motion.")
            log_event("No Motion")
        time.sleep(10)
except KeyboardInterrupt:
    print("\n🔴 Stopping system...")
finally:
    GPIO.cleanup()
    conn.close()
    print(" GPIO cleaned up. Database closed.")
