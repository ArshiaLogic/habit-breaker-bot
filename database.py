import sqlite3
import datetime

DB_FILE = "bot_database.db"

def init_db():
    """Initializes the database and creates the users table if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                start_date TEXT,
                message_count INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

def register_user(user_id: int):
    """Registers a user if they don't exist in the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, message_count)
            VALUES (?, 0)
        ''', (user_id,))
        conn.commit()

def update_start_date(user_id: int):
    """Updates the start_date for the user to the current time."""
    now_str = datetime.datetime.now().isoformat()
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET start_date = ? WHERE user_id = ?
        ''', (now_str, user_id))
        conn.commit()

def get_start_date(user_id: int):
    """Returns the user's start_date as a datetime object, or None if not set."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT start_date FROM users WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        if result and result[0]:
            try:
                return datetime.datetime.fromisoformat(result[0])
            except ValueError:
                return None
        return None

def get_message_count(user_id: int) -> int:
    """Returns the user's current message count."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message_count FROM users WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return 0

def increment_message_count(user_id: int):
    """Increments the user's message count by 1."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET message_count = message_count + 1 WHERE user_id = ?
        ''', (user_id,))
        conn.commit()

def reset_all_message_counts():
    """Resets the message count for all users to 0."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users SET message_count = 0
        ''')
        conn.commit()

def get_all_user_ids():
    """Returns a list of all registered user IDs."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id FROM users
        ''')
        results = cursor.fetchall()
        return [row[0] for row in results]
