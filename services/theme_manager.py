import os
from pathlib import Path
from database.database import get_connection

class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.styles_dir = Path(__file__).parent.parent / "styles"
        self.current_theme = self._load_theme_preference()

    def _load_theme_preference(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key='theme'")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 'dark'

    def _save_theme_preference(self, theme: str):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET value=? WHERE key='theme'", (theme,))
        conn.commit()
        conn.close()

    def apply_theme(self, theme: str = None):
        if theme:
            self.current_theme = theme
            self._save_theme_preference(theme)
            
        style_file = self.styles_dir / f"{self.current_theme}.qss"
        if style_file.exists():
            with open(style_file, "r") as f:
                self.app.setStyleSheet(f.read())
        else:
            print(f"Warning: Stylesheet {style_file} not found.")

    def toggle_theme(self):
        new_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.apply_theme(new_theme)
        return new_theme

    def get_current_theme(self):
        return self.current_theme
