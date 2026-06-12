from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QStackedWidget, QLabel)
from PyQt6.QtCore import Qt, QSize
from ui.chat_widget import ChatWidget
from ui.faq_manager import FAQManagerWidget
from ui.analytics_dashboard import AnalyticsDashboard
from ui.history_widget import HistoryWidget
from ui.settings_dialog import SettingsDialog
from assets.icons import get_icon

class MainWindow(QMainWindow):
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self.setWindowTitle("FAQ Intelligence Assistant")
        self.resize(1200, 800)
        
        self.setup_ui()
        
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        title = QLabel("FAQ Assistant")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 0 20px 20px 20px;")
        sidebar_layout.addWidget(title)
        
        self.nav_buttons = {}
        self.nav_items = [
            ("Home", "home"),
            ("FAQ Database", "database"),
            ("History", "history"),
            ("Analytics", "analytics")
        ]
        
        for name, icon in self.nav_items:
            btn = QPushButton(f"  {name}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name: self.switch_page(n))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[name] = btn
            
        sidebar_layout.addStretch()
        
        self.settings_btn = QPushButton("  Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        sidebar_layout.addWidget(self.settings_btn)
        
        layout.addWidget(self.sidebar)
        
        # Right Side
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setObjectName("Header")
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        self.header_title = QLabel("Home")
        self.header_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.theme_btn = QPushButton()
        self.update_theme_icon()
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.setStyleSheet("border-radius: 20px; background-color: transparent;")
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        header_layout.addWidget(self.header_title)
        header_layout.addStretch()
        header_layout.addWidget(self.theme_btn)
        
        right_layout.addWidget(header)
        
        # Stacked Widget
        self.stack = QStackedWidget()
        
        self.pages = {
            "Home": ChatWidget(),
            "FAQ Database": FAQManagerWidget(),
            "History": HistoryWidget(),
            "Analytics": AnalyticsDashboard()
        }
        
        for widget in self.pages.values():
            self.stack.addWidget(widget)
            
        right_layout.addWidget(self.stack)
        layout.addWidget(right_widget)
        
        # Init state
        self.update_icons()
        self.switch_page("Home")

    def switch_page(self, name):
        # Update buttons
        for btn_name, btn in self.nav_buttons.items():
            btn.setChecked(btn_name == name)
            
        # Update Header
        self.header_title.setText(name)
        
        # Switch stack
        widget = self.pages[name]
        self.stack.setCurrentWidget(widget)
        
        # Refresh data if needed
        if hasattr(widget, 'load_data'):
            widget.load_data()
        elif hasattr(widget, 'refresh_data'):
            widget.refresh_data()

    def update_icons(self):
        theme = self.theme_manager.get_current_theme()
        color = "#1c1c1c" if theme == 'light' else "#ffffff"
        
        # Update sidebar icons
        for name, icon in self.nav_items:
            self.nav_buttons[name].setIcon(get_icon(icon, color))
            
        self.settings_btn.setIcon(get_icon("settings", color))
        
        # Update children icons
        if "FAQ Database" in self.pages:
            self.pages["FAQ Database"].update_icons()

    def update_theme_icon(self):
        theme = self.theme_manager.get_current_theme()
        if theme == 'dark':
            self.theme_btn.setIcon(get_icon("theme_light", "#ffffff"))
        else:
            self.theme_btn.setIcon(get_icon("theme_dark", "#1c1c1c"))

    def toggle_theme(self):
        self.theme_manager.toggle_theme()
        self.update_theme_icon()
        self.update_icons()
        
    def open_settings(self):
        dialog = SettingsDialog(self, self.theme_manager)
        dialog.exec()
