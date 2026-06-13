from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSlider, QFormLayout)
from PyQt6.QtCore import Qt
from database.database import get_connection
from services.theme_manager import ThemeManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None, theme_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowTitle("Settings")
        self.setMinimumWidth(300)
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(10, 100)
        self.threshold_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.threshold_slider.setTickInterval(10)
        
        self.threshold_label = QLabel("70%")
        self.threshold_slider.valueChanged.connect(lambda v: self.threshold_label.setText(f"{v}%"))
        
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.threshold_slider)
        slider_layout.addWidget(self.threshold_label)
        
        form.addRow("Confidence Threshold:", slider_layout)
        
        layout.addLayout(form)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_settings(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key='confidence_threshold'")
        row = cursor.fetchone()
        conn.close()
        
        try:
            val = int(float(row[0])) if row else 70
        except ValueError:
            val = 70
            
        self.threshold_slider.setValue(val)

    def save_settings(self):
        val = self.threshold_slider.value()
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET value=? WHERE key='confidence_threshold'", (str(val),))
        conn.commit()
        conn.close()
        
        self.accept()
