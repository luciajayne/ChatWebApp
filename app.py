from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os
import hashlib
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'

DB_PATH = 'chat_app.db'

ADMIN_USER = 'admin'
ADMIN_PASS = 'password123'

ASSISTANT_RESPONSES = [
    "That's interesting! Tell me more.",
    "I see what you mean.",
    "Have you tried turning it off and on again?",
    "That reminds me of something similar that happened to me.",
    "I couldn't agree more!",
    "Hmm, I'll have to think about that.",
    "Great point!",
    "Thanks for sharing!",
    "I'm not sure I understand. Can you elaborate?",
    "That's a good question. Let me think...",
    "Absolutely!",
    "I hear you.",
    "That makes sense.",
    "Interesting perspective!",
    "I hadn't thought of it that way."
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT, timestamp TEXT)''')
    c.execute(f"INSERT OR IGNORE INTO users (username, password, email) VALUES ('{ADMIN_USER}', '{ADMIN_PASS}', 'admin@vulnerable.com')")
    c.execute("INSERT OR IGNORE INTO users (id, username, password, email) VALUES (999, 'Assistant', 'bot123', 'assistant@chatapp.com')")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/chat')
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"Executing query: {query}")
        c.execute(query)
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/chat')
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        query = f"INSERT INTO users (username, password, email) VALUES ('{username}', '{password}', '{email}')"
        try:
            c.execute(query)
            conn.commit()
            conn.close()
            return redirect('/login')
        except:
            conn.close()
            return render_template('register.html', error='Username already exists')
    
    return render_template('register.html')

@app.route('/chat')
def chat():
    if 'user_id' not in session:
        return redirect('/')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT m.message, u.username, m.timestamp FROM messages m JOIN users u ON m.user_id = u.id ORDER BY m.id DESC")
    messages = c.fetchall()
    conn.close()
    
    return render_template('chat.html', messages=messages, username=session.get('username'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    message = request.form['message']
    user_id = session['user_id']
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = f"INSERT INTO messages (user_id, timestamp, message) VALUES ({user_id}, '{timestamp}', '{message}')"
    c.executescript(query)
    conn.commit()
    
    # Assistant auto-response
    assistant_message = random.choice(ASSISTANT_RESPONSES)
    assistant_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    assistant_query = f"INSERT INTO messages (user_id, timestamp, message) VALUES (999, '{assistant_timestamp}', '{assistant_message}')"
    c.executescript(assistant_query)
    conn.commit()
    
    conn.close()
    
    return jsonify({'success': True})

@app.route('/get_messages')
def get_messages():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT m.message, u.username, m.timestamp FROM messages m JOIN users u ON m.user_id = u.id ORDER BY m.id DESC LIMIT 50")
    messages = c.fetchall()
    conn.close()
    
    message_html = ""
    for msg in messages:
        message_html += f'<div class="message"><strong>{msg[1]}</strong> ({msg[2]}): {msg[0]}</div>'
    
    return message_html

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/admin')
def admin():
    if session.get('username') == ADMIN_USER:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        conn.close()
        return render_template('admin.html', users=users)
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5002)