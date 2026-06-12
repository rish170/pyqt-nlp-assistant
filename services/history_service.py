import sqlite3
from datetime import datetime
from database.database import get_connection
from models.schemas import HistoryRecord
import logging

logger = logging.getLogger(__name__)

class HistoryService:
    def log_interaction(self, user_question: str, bot_answer: str, confidence_score: float, response_time_ms: float, category: str):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO history (user_question, bot_answer, confidence_score, timestamp, response_time_ms, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_question, bot_answer, confidence_score, now, response_time_ms, category))
        conn.commit()
        conn.close()

    def get_recent_history(self, limit: int = 100):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [HistoryRecord(**dict(row)) for row in rows]
        
    def clear_history(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history")
        conn.commit()
        conn.close()
