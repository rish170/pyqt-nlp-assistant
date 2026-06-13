from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout
from services.history_service import HistoryService
from assets.icons import get_icon

class HistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_service = HistoryService()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        toolbar = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        
        clear_btn = QPushButton("Clear History")
        clear_btn.setObjectName("PrimaryButton")
        clear_btn.clicked.connect(self.clear_data)
        
        toolbar.addWidget(refresh_btn)
        toolbar.addStretch()
        toolbar.addWidget(clear_btn)
        layout.addLayout(toolbar)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Question", "Answer", "Confidence", "Category"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.table)
        self.load_data()
        
    def load_data(self):
        records = self.history_service.get_recent_history()
        self.table.setRowCount(len(records))
        for i, r in enumerate(records):
            time_str = r.timestamp[:19].replace('T', ' ')
            self.table.setItem(i, 0, QTableWidgetItem(time_str))
            self.table.setItem(i, 1, QTableWidgetItem(r.user_question))
            self.table.setItem(i, 2, QTableWidgetItem(r.bot_answer))
            self.table.setItem(i, 3, QTableWidgetItem(f"{r.confidence_score:.1f}%"))
            self.table.setItem(i, 4, QTableWidgetItem(r.category))
            
    def clear_data(self):
        self.history_service.clear_history()
        self.load_data()
