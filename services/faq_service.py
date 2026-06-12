import sqlite3
import pandas as pd
from datetime import datetime
from database.database import get_connection
from models.schemas import FAQ
import json
import logging

logger = logging.getLogger(__name__)

class FAQService:
    def __init__(self):
        # Notify mechanism for cache invalidation or UI updates could go here
        pass
        
    def get_all_faqs(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM faqs ORDER BY usage_count DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [FAQ(**dict(row)) for row in rows]

    def add_faq(self, question: str, answer: str, category: str):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO faqs (question, answer, category, created_date, updated_date, usage_count, is_favorite)
            VALUES (?, ?, ?, ?, ?, 0, 0)
        """, (question, answer, category, now, now))
        conn.commit()
        conn.close()

    def update_faq(self, faq_id: int, question: str, answer: str, category: str):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE faqs
            SET question = ?, answer = ?, category = ?, updated_date = ?
            WHERE id = ?
        """, (question, answer, category, now, faq_id))
        conn.commit()
        conn.close()

    def delete_faq(self, faq_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
        conn.commit()
        conn.close()

    def increment_usage(self, faq_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE faqs SET usage_count = usage_count + 1 WHERE id = ?", (faq_id,))
        conn.commit()
        conn.close()
        
    def toggle_favorite(self, faq_id: int, is_favorite: bool):
        conn = get_connection()
        cursor = conn.cursor()
        val = 1 if is_favorite else 0
        cursor.execute("UPDATE faqs SET is_favorite = ? WHERE id = ?", (val, faq_id))
        conn.commit()
        conn.close()

    def import_faqs(self, file_path: str):
        # Support CSV, JSON, Excel
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            elif file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError("Unsupported file format")

            # Validate columns
            required_cols = {'Question', 'Answer', 'Category'}
            if not required_cols.issubset(set(df.columns)):
                raise ValueError(f"File must contain columns: {', '.join(required_cols)}")
                
            conn = get_connection()
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            # Efficient bulk insert
            records = []
            for _, row in df.iterrows():
                records.append((
                    str(row['Question']),
                    str(row['Answer']),
                    str(row['Category']),
                    now, now, 0, 0
                ))
                
            cursor.executemany("""
                INSERT INTO faqs (question, answer, category, created_date, updated_date, usage_count, is_favorite)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, records)
            
            conn.commit()
            conn.close()
            return True, f"Successfully imported {len(records)} FAQs."
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return False, str(e)

    def export_faqs(self, file_path: str):
        faqs = self.get_all_faqs()
        data = [{
            "Question": f.question,
            "Answer": f.answer,
            "Category": f.category,
            "Usage Count": f.usage_count,
            "Is Favorite": bool(f.is_favorite)
        } for f in faqs]
        df = pd.DataFrame(data)
        
        try:
            if file_path.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif file_path.endswith('.json'):
                df.to_json(file_path, orient='records', indent=4)
            elif file_path.endswith(('.xls', '.xlsx')):
                df.to_excel(file_path, index=False)
            else:
                return False, "Unsupported file format"
            return True, "Export successful."
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False, str(e)
