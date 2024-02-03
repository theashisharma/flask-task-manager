from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)

# Configuration
DATABASE = 'database.db'
TABLE_NAME = 'tasks'
SECRET_KEY = 'your-secret-key'

# Set the secret key for session management
app.config['SECRET_KEY'] = SECRET_KEY

# Create tables for tasks and users if they don't exist
def create_tables():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status INTEGER DEFAULT 0,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.close()



create_tables()

# Home page — Display tasks
@app.route('/task')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {TABLE_NAME} WHERE user_id = (SELECT id FROM users WHERE username=?)', (session['username'],))
    tasks = cursor.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

# Login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', message='Invalid credentials. Please try again.')

    return render_template('login.html', message='')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Registration page
# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''  # Initialize an empty message

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute('SELECT * FROM users WHERE username=?', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            message = 'Username already exists. Please choose another username.'
        else:
            # If username is unique, insert the new user
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))

    return render_template('register.html', message=message)


# Create a new task
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        if 'username' in session:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO tasks (title, description, user_id) VALUES (?, ?, (SELECT id FROM users WHERE username=?))', (title, description, session['username']))
            conn.commit()
            conn.close()

        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/delete/<int:task_id>', methods=['GET'])
def delete(task_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM {TABLE_NAME} WHERE id=?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run(debug=True)
