# Smart Intrusion Detection System

A Raspberry Pi-based intrusion detection system using motion sensor (PIR), Twilio SMS alerts, email notifications, and event logging in SQLite.

## Features
- 🚨 SMS & Email alerts when motion is detected
- 📦 SQLite database for event history
- 🔊 Buzzer alarm on motion detection
- 📁 Configurable credentials (via JSON file)
- 🔄 Graceful shutdown with GPIO cleanup

## Requirements
- Raspberry Pi
- PIR Motion Sensor
- Buzzer
- Twilio account
- Gmail account with app password (for email)

## Setup
1. Install dependencies:
   pip install -r requirements.txt
2. Update `config.json` with your credentials.
3. Run:
   python3 app.py
