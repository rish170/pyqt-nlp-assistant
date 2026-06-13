from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QLineEdit, QFileDialog, QMessageBox, QDialog, 
                             QFormLayout, QLabel, QComboBox)
from PyQt6.QtCore import Qt
from services.faq_service import FAQService
from ui.components.toast import show_toast
from assets.icons import get_icon
from database.database import get_connection

class FAQDialog(QDialog):
    def __init__(self, parent=None, faq=None):
        super().__init__(parent)
        self.setWindowTitle("Edit FAQ" if faq else "Add FAQ")
        self.setMinimumWidth(400)
        self.faq = faq
        
        layout = QFormLayout(self)
        
        self.q_input = QLineEdit()
        self.a_input = QLineEdit()
        self.c_input = QComboBox()
        self.c_input.addItems(["Account", "Billing", "Technical Support", "Orders", "General", "Products"])
        self.c_input.setEditable(True)
        
        if faq:
            self.q_input.setText(faq.question)
            self.a_input.setText(faq.answer)
            self.c_input.setCurrentText(faq.category)
            
        layout.addRow("Question:", self.q_input)
        layout.addRow("Answer:", self.a_input)
        layout.addRow("Category:", self.c_input)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def get_data(self):
        return self.q_input.text(), self.a_input.text(), self.c_input.currentText()

class FAQManagerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.faq_service = FAQService()
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search FAQs...")
        self.search_input.textChanged.connect(self.filter_table)
        
        self.add_btn = QPushButton("Add FAQ")
        self.add_btn.clicked.connect(self.add_faq)
        
        self.import_btn = QPushButton("Import")
        self.import_btn.clicked.connect(self.import_faqs)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_faqs)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_data)
        
        self.update_icons()
        
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.import_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addWidget(self.refresh_btn)
        
        layout.addLayout(toolbar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Question", "Answer", "Category", "Usage", "Actions"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
        
    def load_data(self):
        self.faqs = self.faq_service.get_all_faqs()
        self.table.setRowCount(len(self.faqs))
        
        for i, faq in enumerate(self.faqs):
            self.table.setItem(i, 0, QTableWidgetItem(str(faq.id)))
            self.table.setItem(i, 1, QTableWidgetItem(faq.question))
            self.table.setItem(i, 2, QTableWidgetItem(faq.answer))
            self.table.setItem(i, 3, QTableWidgetItem(faq.category))
            self.table.setItem(i, 4, QTableWidgetItem(str(faq.usage_count)))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton()
            edit_btn.setIcon(get_icon("edit", "#007acc"))
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, f=faq: self.edit_faq(f))
            
            del_btn = QPushButton()
            del_btn.setIcon(get_icon("delete", "#f44336"))
            del_btn.setFixedSize(30, 30)
            del_btn.clicked.connect(lambda checked, f_id=faq.id: self.delete_faq(f_id))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(del_btn)
            self.table.setCellWidget(i, 5, actions_widget)

    def filter_table(self, text):
        for i in range(self.table.rowCount()):
            match = False
            for j in range(1, 4):
                item = self.table.item(i, j)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(i, not match)

    def add_faq(self):
        dialog = FAQDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            q, a, c = dialog.get_data()
            if q and a:
                self.faq_service.add_faq(q, a, c)
                from services.nlp_engine import NLPEngine
                NLPEngine().mark_dirty()
                self.load_data()
                show_toast(self.window(), "Success", "FAQ added successfully.", notification_type="success")

    def edit_faq(self, faq):
        dialog = FAQDialog(self, faq)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            q, a, c = dialog.get_data()
            if q and a:
                self.faq_service.update_faq(faq.id, q, a, c)
                from services.nlp_engine import NLPEngine
                NLPEngine().mark_dirty()
                self.load_data()
                show_toast(self.window(), "Success", "FAQ updated successfully.", notification_type="success")

    def delete_faq(self, faq_id):
        reply = QMessageBox.question(self, 'Confirm', 'Are you sure you want to delete this FAQ?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.faq_service.delete_faq(faq_id)
            from services.nlp_engine import NLPEngine
            NLPEngine().mark_dirty()
            self.load_data()
            show_toast(self.window(), "Success", "FAQ deleted.", notification_type="info")

    def import_faqs(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import FAQs", "", "CSV Files (*.csv);;JSON Files (*.json);;Excel Files (*.xlsx *.xls)")
        if file_path:
            success, msg = self.faq_service.import_faqs(file_path)
            if success:
                from services.nlp_engine import NLPEngine
                NLPEngine().mark_dirty()
                self.load_data()
                show_toast(self.window(), "Import Successful", msg, notification_type="success")
            else:
                show_toast(self.window(), "Import Error", msg, notification_type="error")

    def export_faqs(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export FAQs", "faqs.csv", "CSV Files (*.csv);;JSON Files (*.json);;Excel Files (*.xlsx)")
        if file_path:
            success, msg = self.faq_service.export_faqs(file_path)
            if success:
                show_toast(self.window(), "Export Successful", msg, notification_type="success")
            else:
                show_toast(self.window(), "Export Error", msg, notification_type="error")

    def update_icons(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key='theme'")
        row = cursor.fetchone()
        conn.close()
        theme = row[0] if row else 'dark'
        color = "#1c1c1c" if theme == 'light' else "#ffffff"
        
        self.add_btn.setIcon(get_icon("add", color))
        self.import_btn.setIcon(get_icon("import", color))
        self.export_btn.setIcon(get_icon("export", color))
