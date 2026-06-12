from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
                             QScrollArea, QLabel, QFrame, QListWidget, QListWidgetItem, QGraphicsOpacityEffect, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QTimer, QThreadPool, pyqtSignal, QPropertyAnimation
from PyQt6.QtGui import QFont, QCursor
from assets.icons import get_icon
from services.nlp_engine import NLPQueryWorker, NLPEngine
import logging
from datetime import datetime
from services.history_service import HistoryService
from services.faq_service import FAQService
from database.database import get_connection

logger = logging.getLogger(__name__)

class BubbleWidget(QFrame):
    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        layout.addWidget(self.label)
        
        if is_user:
            self.setObjectName("UserBubble")
        else:
            self.setObjectName("BotBubble")
            
        # Animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()



class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nlp_engine = NLPEngine()
        self.history_service = HistoryService()
        self.faq_service = FAQService()
        self.threadpool = QThreadPool()
        
        self.setup_ui()
        self.setup_suggestions_popup()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Chat History Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("ChatScrollArea")
        self.scroll_area.verticalScrollBar().setSingleStep(15) # Smoother scrolling
        
        # Fix for scrolling glitch and smearing:
        # We must use strict child selectors (>) so the transparency doesn't cascade
        # down and erase the backgrounds of the chat bubbles!
        self.scroll_area.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget { background: transparent; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ChatScrollAreaWidget")
        self.chat_layout = QVBoxLayout(self.scroll_content)
        self.chat_layout.addStretch() # Push messages to bottom initially
        
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area, 1) # Stretch factor 1
        
        # Input Area
        input_container = QWidget()
        input_container.setObjectName("InputArea")
        input_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(20, 10, 20, 10)
        
        self.text_input = QTextEdit()
        self.text_input.setObjectName("ChatInput")
        self.text_input.setPlaceholderText("Ask a question...")
        self.text_input.setMaximumHeight(80)
        self.text_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.text_input.installEventFilter(self)
        self.text_input.textChanged.connect(self.on_text_changed)
        
        self.send_button = QPushButton()
        self.send_button.setObjectName("SendButton")
        self.send_button.setIcon(get_icon("send"))
        self.send_button.setIconSize(QSize(20, 20))
        self.send_button.setFixedSize(40, 40)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(self.send_button)
        
        main_layout.addWidget(input_container, 0) # Stretch factor 0

    def setup_suggestions_popup(self):
        self.suggestions_list = QListWidget(self)
        self.suggestions_list.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.suggestions_list.hide()
        self.suggestions_list.itemClicked.connect(self.on_suggestion_clicked)
        
    def eventFilter(self, obj, event):
        if obj is self.text_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def on_text_changed(self):
        text = self.text_input.toPlainText()
        if len(text) > 2:
            suggestions = self.nlp_engine.get_suggestions(text, limit=3)
            if suggestions:
                self.suggestions_list.clear()
                for faq in suggestions:
                    item = QListWidgetItem(faq.question)
                    item.setData(Qt.ItemDataRole.UserRole, faq)
                    self.suggestions_list.addItem(item)
                
                # Position popup
                pos = self.text_input.mapToGlobal(self.text_input.rect().topLeft())
                self.suggestions_list.move(pos.x(), pos.y() - self.suggestions_list.sizeHint().height() - 10)
                self.suggestions_list.show()
            else:
                self.suggestions_list.hide()
        else:
            self.suggestions_list.hide()

    def on_suggestion_clicked(self, item):
        faq = item.data(Qt.ItemDataRole.UserRole)
        self.text_input.setPlainText(faq.question)
        self.suggestions_list.hide()
        self.send_message()

    def add_message(self, text, is_user=False):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 0, 10, 0)
        
        bubble = BubbleWidget(text, is_user=is_user)
        
        if is_user:
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            layout.addWidget(bubble)
            layout.addStretch()
            
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
        
        # Auto scroll to bottom
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum()))

    def get_threshold(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key='confidence_threshold'")
        row = cursor.fetchone()
        conn.close()
        try:
            return float(row[0]) if row else 70.0
        except ValueError:
            return 70.0

    def send_message(self):
        text = self.text_input.toPlainText().strip()
        if not text: return
        
        self.text_input.clear()
        self.suggestions_list.hide()
        self.add_message(text, is_user=True)
        
        # Show loading indicator
        self.add_message("Thinking...", is_user=False)
        self.loading_widget = self.chat_layout.itemAt(self.chat_layout.count() - 2).widget()
        
        # Start NLP worker
        self.start_time = datetime.now()
        worker = NLPQueryWorker(text, threshold=self.get_threshold())
        worker.signals.finished.connect(lambda res: self.on_nlp_finished(text, res))
        worker.signals.error.connect(lambda err: self.on_nlp_error(text, err))
        self.threadpool.start(worker)

    def on_nlp_finished(self, user_question, result):
        # Remove loading
        self.loading_widget.setParent(None)
        
        resp_time = (datetime.now() - self.start_time).total_seconds() * 1000
        
        if result['status'] == 'success':
            faq = result['faq']
            score = result['score']
            self.add_message(f"{faq.answer}\n\n[Confidence: {score:.1f}%]")
            self.faq_service.increment_usage(faq.id)
            self.history_service.log_interaction(user_question, faq.answer, score, resp_time, faq.category)
            
        elif result['status'] == 'low_confidence':
            score = result['score']
            suggestions = result.get('suggestions', [])
            msg = "I couldn't find a reliable answer to your question.\n"
            if suggestions:
                msg += "\nDid you mean:\n"
                for s in suggestions:
                    msg += f"- {s.question}\n"
                    
            self.add_message(msg)
            self.history_service.log_interaction(user_question, "Low confidence fallback", score, resp_time, "Unresolved")
            
        elif result['status'] == 'error':
            self.add_message(f"Error: {result.get('message', 'Unknown error')}")

    def on_nlp_error(self, user_question, err):
        self.loading_widget.setParent(None)
        self.add_message("An error occurred while processing your request.")
        logger.error(err)
