import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from database.database import init_db
from ui.main_window import MainWindow
from services.theme_manager import ThemeManager
import logging
from assets.icons import get_icon

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    # Initialize DB
    init_db()
    
    app = QApplication(sys.argv)
    app.setApplicationName("FAQ Intelligence Assistant")
    app.setWindowIcon(get_icon("database"))
    
    # Init theme manager
    theme_manager = ThemeManager(app)
    theme_manager.apply_theme()
    
    window = MainWindow(theme_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
