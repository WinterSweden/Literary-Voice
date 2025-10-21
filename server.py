"""
Literary Voice API Server
Handles authentication and credit management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE = 'literary_voice.db'

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database with tables"""
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            credits INTEGER DEFAULT 15,
            plan TEXT DEFAULT 'commoner',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    db.commit()
    db.close()

def hash_password(password):
    """Hash password with SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key():
    """Generate secure API key"""
    return secrets.token_urlsafe(32)

@app.route('/signup', methods=['POST'])
def signup():
    """Register new user"""
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    db = get_db()
    
    # Check if user exists
    existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    if existing:
        db.close()
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    password_hash = hash_password(password)
    api_key = generate_api_key()
    
    try:
        cursor = db.execute(
            'INSERT INTO users (email, password_hash, api_key, credits) VALUES (?, ?, ?, ?)',
            (email, password_hash, api_key, 15)
        )
        db.commit()
        
        return jsonify({
            'api_key': api_key,
            'credits': 15,
            'message': 'Account created successfully'
        }), 201
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/login', methods=['POST'])
def login():
    """Login existing user"""
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    db = get_db()
    password_hash = hash_password(password)
    
    user = db.execute(
        'SELECT api_key, credits FROM users WHERE email = ? AND password_hash = ?',
        (email, password_hash)
    ).fetchone()
    
    db.close()
    
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    return jsonify({
        'api_key': user['api_key'],
        'credits': user['credits'],
        'message': 'Login successful'
    }), 200

@app.route('/balance', methods=['GET'])
def get_balance():
    """Get user credit balance"""
    api_key = request.headers.get('X-API-Key')
    
    if not api_key:
        return jsonify({'error': 'API key required'}), 401
    
    db = get_db()
    user = db.execute('SELECT credits FROM users WHERE api_key = ?', (api_key,)).fetchone()
    db.close()
    
    if not user:
        return jsonify({'error': 'Invalid API key'}), 401
    
    return jsonify({'credits': user['credits']}), 200

@app.route('/deduct', methods=['POST'])
def deduct_credits():
    """Deduct credits from user account"""
    api_key = request.headers.get('X-API-Key')
    data = request.json
    amount = data.get('amount', 0)
    action = data.get('action', 'unknown')
    
    if not api_key:
        return jsonify({'error': 'API key required'}), 401
    
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    db = get_db()
    
    # Get user
    user = db.execute('SELECT id, credits FROM users WHERE api_key = ?', (api_key,)).fetchone()
    
    if not user:
        db.close()
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Check sufficient credits
    if user['credits'] < amount:
        db.close()
        return jsonify({'error': 'Insufficient credits'}), 402
    
    # Deduct credits
    new_balance = user['credits'] - amount
    db.execute('UPDATE users SET credits = ? WHERE id = ?', (new_balance, user['id']))
    
    # Log transaction
    db.execute(
        'INSERT INTO transactions (user_id, amount, action) VALUES (?, ?, ?)',
        (user['id'], -amount, action)
    )
    
    db.commit()
    db.close()
    
    return jsonify({
        'credits': new_balance,
        'message': f'{amount} credits deducted'
    }), 200

@app.route('/add_credits', methods=['POST'])
def add_credits():
    """Add credits to user account (for admin/payment processing)"""
    data = request.json
    email = data.get('email', '').strip().lower()
    amount = data.get('amount', 0)
    admin_key = data.get('admin_key', '')
    
    # Simple admin authentication (change this!)
    if admin_key != os.environ.get('ADMIN_KEY', 'change_me_in_production'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    if amount <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    db = get_db()
    
    user = db.execute('SELECT id, credits FROM users WHERE email = ?', (email,)).fetchone()
    
    if not user:
        db.close()
        return jsonify({'error': 'User not found'}), 404
    
    new_balance = user['credits'] + amount
    db.execute('UPDATE users SET credits = ? WHERE id = ?', (new_balance, user['id']))
    
    db.execute(
        'INSERT INTO transactions (user_id, amount, action) VALUES (?, ?, ?)',
        (user['id'], amount, 'admin_add')
    )
    
    db.commit()
    db.close()
    
    return jsonify({
        'credits': new_balance,
        'message': f'{amount} credits added'
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Literary Voice API'}), 200

if __name__ == '__main__':
    # Initialize database
    if not os.path.exists(DATABASE):
        init_db()
        print("✅ Database initialized")
    
    # Run server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
