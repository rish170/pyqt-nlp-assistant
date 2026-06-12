from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QColor
import logging

logger = logging.getLogger(__name__)

class ToastNotification(QWidget):
    def __init__(self, parent=None, title="Notification", message="", duration=3000, notification_type="info"):
        super().__init__(parent)
        self.duration = duration
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setup_ui(title, message, notification_type)
        
        # Opacity effect for fade in/out
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)

    def setup_ui(self, title, message, notification_type):
        self.setFixedWidth(300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        bg_widget = QWidget(self)
        bg_layout = QVBoxLayout(bg_widget)
        
        # Set colors based on type
        if notification_type == "success":
            color = "#4caf50"
        elif notification_type == "error":
            color = "#f44336"
        else:
            color = "#2196f3"
            
        bg_widget.setStyleSheet(f"""
            QWidget {{
                background-color: #2e2e2e;
                border-left: 4px solid {color};
                border-radius: 6px;
                color: #ffffff;
            }}
        """)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
        
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 12px; border: none; color: #bbbbbb;")
        
        bg_layout.addWidget(title_label)
        bg_layout.addWidget(msg_label)
        layout.addWidget(bg_widget)

    def show_toast(self):
        if self.parent():
            parent_rect = self.parent().geometry()
            # Position bottom right
            x = parent_rect.x() + parent_rect.width() - self.width() - 20
            y = parent_rect.y() + parent_rect.height() - self.height() - 20
            self.move(x, y)
        
        self.show()
        
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        
        QTimer.singleShot(self.duration, self.hide_toast)
        
    def hide_toast(self):
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.close)
        self.animation.start()

def show_toast(parent, title, message, duration=3000, notification_type="info"):
    toast = ToastNotification(parent, title, message, duration, notification_type)
    toast.show_toast()
