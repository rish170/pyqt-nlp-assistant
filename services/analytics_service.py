import sqlite3
import pandas as pd
from database.database import get_connection

class AnalyticsService:
    def get_dashboard_stats(self):
        conn = get_connection()
        
        stats = {
            "total_faqs": 0,
            "total_queries": 0,
            "avg_confidence": 0.0,
            "top_categories": [],
            "usage_trends": [],
            "most_asked": []
        }
        
        try:
            cursor = conn.cursor()
            
            # Total FAQs
            cursor.execute("SELECT COUNT(*) FROM faqs")
            stats["total_faqs"] = cursor.fetchone()[0]
            
            # Total Queries
            cursor.execute("SELECT COUNT(*) FROM history")
            stats["total_queries"] = cursor.fetchone()[0]
            
            # Average Confidence
            cursor.execute("SELECT AVG(confidence_score) FROM history")
            avg_conf = cursor.fetchone()[0]
            stats["avg_confidence"] = round(avg_conf, 2) if avg_conf else 0.0
            
            # Top Categories
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM history 
                GROUP BY category 
                ORDER BY count DESC 
                LIMIT 5
            """)
            stats["top_categories"] = [dict(row) for row in cursor.fetchall()]
            
            # Most Asked Questions (from FAQs usage count)
            cursor.execute("""
                SELECT question, usage_count 
                FROM faqs 
                ORDER BY usage_count DESC 
                LIMIT 5
            """)
            stats["most_asked"] = [dict(row) for row in cursor.fetchall()]
            
            # Usage Trends (queries per day for last 7 days)
            cursor.execute("""
                SELECT substr(timestamp, 1, 10) as date, COUNT(*) as count
                FROM history
                GROUP BY date
                ORDER BY date DESC
                LIMIT 7
            """)
            # Reverse to be chronological
            stats["usage_trends"] = [dict(row) for row in cursor.fetchall()][::-1]
            
        except Exception as e:
            pass
        finally:
            conn.close()
            
        return stats
