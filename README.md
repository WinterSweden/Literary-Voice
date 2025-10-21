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

## Deploying to PythonAnywhere (100% FREE!)

### Step 1: Create Account

1. Go to https://www.pythonanywhere.com
2. Sign up for a **free Beginner account** (no credit card needed!)
3. Confirm your email

### Step 2: Upload Your Code

1. Click on **"Files"** tab
2. Navigate to `/home/yourusername/`
3. Create a new directory: `literary-voice`
4. Upload `server.py` to this directory
5. The database will be created automatically on first run

### Step 3: Install Dependencies

1. Click on **"Consoles"** tab
2. Start a new **Bash console**
3. Run these commands:

```bash
cd literary-voice
pip3 install --user flask flask-cors requests beautifulsoup4
```

### Step 4: Set Up Web App

1. Click on **"Web"** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Choose **Python 3.10**
5. Click through the setup

### Step 5: Configure WSGI File

1. On the Web tab, click on **WSGI configuration file** link
2. Delete everything in the file
3. Paste this code:

```python
import sys
import os

# Add your project directory
project_home = '/home/yourusername/literary-voice'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['ADMIN_KEY'] = 'your_secure_admin_key_here'

# Import Flask app
from server import app as application
```

4. **Replace `yourusername` with your actual PythonAnywhere username!**
5. **Replace `your_secure_admin_key_here` with a random secure key**
6. Click **Save**

### Step 6: Reload Web App

1. Go back to **Web** tab
2. Click the big green **"Reload"** button
3. Your API is now live at: `https://yourusername.pythonanywhere.com`

### Step 7: Update CLI Config

In `literary_voice.py`, change line 18:

```python
API_BASE_URL = "https://yourusername.pythonanywhere.com"
```

**Replace `yourusername` with your actual username!**

---

## Testing Your Deployment

```bash
# Test health endpoint
curl https://yourusername.pythonanywhere.com/health

# Should return: {"service":"Literary Voice API","status":"healthy"}
```

If you see that, **you're live!** 🚀

---

## Local Testing (Before Deploying)

### 1. Start the Server Locally

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

## Managing Credits (Admin)

To manually add credits to users (for payments during beta):

```bash
curl -X POST https://yourusername.pythonanywhere.com/add_credits \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "amount": 250,
    "admin_key": "your_secure_admin_key_here"
  }'
```

---

## Files You Need

**`requirements.txt`:**
```
Flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
beautifulsoup4==4.12.2
```

**`.gitignore`:**
```
*.db
__pycache__/
*.pyc
.env
.literary-voice/
