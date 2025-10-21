# The Literary Voice 📚

**An AI-powered book recommendation CLI that scrapes Goodreads to find the most helpful reviews and reformats them into conversational, actionable insights.**

---

## Features

✨ **Smart Review Analysis** - Finds the most-liked Goodreads reviews  
🤖 **AI Reformatting** - Transforms reviews into structured insights  
💳 **Credit System** - Freemium model with tiered subscriptions  
🔐 **Secure Authentication** - Email/password with API key management  
⚡ **Fast & Elegant** - Beautiful CLI with typing effects  

---

## Installation

### Requirements
- Python 3.8+
- pip

### Install Dependencies

```bash
pip install requests beautifulsoup4 flask flask-cors
```

---

## Local Testing

### 1. Start the Server

```bash
python server.py
```

Server runs on `http://localhost:5000`

### 2. Run the CLI

In a new terminal:

```bash
python literary_voice.py
```

### 3. Create an Account

- Sign up with email/password
- You'll start with 15 free credits!

---

## Deploying to Railway.app

### Step 1: Prepare Your Project

Create these files in your project directory:

**`requirements.txt`:**
```
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
gunicorn==21.2.0
```

**`Procfile`:**
```
web: gunicorn server:app
```

**`.gitignore`:**
```
*.db
__pycache__/
*.pyc
.env
.literary-voice
