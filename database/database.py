import sqlite3
import os
from pathlib import Path

# We store the database in the data directory by default
DB_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DB_DIR / "faq_assistant.db"

def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # FAQs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT NOT NULL,
            created_date TEXT NOT NULL,
            updated_date TEXT NOT NULL,
            usage_count INTEGER DEFAULT 0,
            is_favorite INTEGER DEFAULT 0
        )
    """)
    
    # History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question TEXT NOT NULL,
            bot_answer TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            timestamp TEXT NOT NULL,
            response_time_ms REAL NOT NULL,
            category TEXT NOT NULL
        )
    """)
    
    # Settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    
    # Default settings
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('theme', 'dark')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('confidence_threshold', '70')")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
