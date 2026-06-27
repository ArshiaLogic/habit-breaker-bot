import sqlite3
import datetime

DB_FILE = "bot_database.db"


def init_db():
    """Initializes the database and creates the tables if they don't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                start_date TEXT,
                message_count INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        # Insert default setting if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value) VALUES ('auto_post_count', '0')
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auto_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_time TEXT,
                has_image INTEGER
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


def get_setting(key: str) -> str:
    """Returns the value of a setting from the database, or None if not found."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result[0] if result else None

def set_setting(key: str, value: str):
    """Sets a key-value setting in the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        conn.commit()

def get_total_users() -> int:
    """Returns the total number of registered users."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        result = cursor.fetchone()
        return result[0] if result else 0


def add_auto_post(post_time: str, has_image: int):
    """Adds a new scheduled auto post."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO auto_posts (post_time, has_image) VALUES (?, ?)', (post_time, has_image))
        conn.commit()

def get_all_auto_posts() -> list:
    """Returns a list of all scheduled auto posts."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, post_time, has_image FROM auto_posts ORDER BY post_time ASC')
        return cursor.fetchall()

def delete_auto_post(post_id: int):
    """Deletes an auto post schedule by ID."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM auto_posts WHERE id = ?', (post_id,))
        conn.commit()

def get_auto_posts_by_time(current_time: str) -> list:
    """Returns all auto posts scheduled for a specific time (HH:MM)."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, has_image FROM auto_posts WHERE post_time = ?', (current_time,))
        return cursor.fetchall()
