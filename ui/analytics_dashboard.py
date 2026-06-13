from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
from PyQt6.QtCore import Qt
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from services.analytics_service import AnalyticsService

class StatCard(QFrame):
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.setStyleSheet("""
            QFrame#StatCard {
                background-color: rgba(128, 128, 128, 0.1);
                border-radius: 8px;
                padding: 15px;
            }
        """)
        layout = QVBoxLayout(self)
        
        t_label = QLabel(title)
        t_label.setStyleSheet("font-size: 14px; color: #888888;")
        layout.addWidget(t_label)
        
        v_label = QLabel(str(value))
        v_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(v_label)

class AnalyticsDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analytics_service = AnalyticsService()
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        
        self.header_label = QLabel("Analytics Dashboard")
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.header_label)
        
        self.stats_grid = QGridLayout()
        self.layout.addLayout(self.stats_grid)
        
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.refresh_data()
        
    def refresh_data(self):
        stats = self.analytics_service.get_dashboard_stats()
        
        # Clear old stats
        for i in reversed(range(self.stats_grid.count())): 
            self.stats_grid.itemAt(i).widget().setParent(None)
            
        # Add new stats
        self.stats_grid.addWidget(StatCard("Total FAQs", stats["total_faqs"]), 0, 0)
        self.stats_grid.addWidget(StatCard("Total Queries", stats["total_queries"]), 0, 1)
        self.stats_grid.addWidget(StatCard("Avg Confidence", f"{stats['avg_confidence']}%"), 0, 2)
        
        # Plot Usage Trends
        self.figure.clear()
        
        # Style based on theme
        # Using a default dark theme style for the chart to match the app
        self.figure.patch.set_facecolor('none')
        
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('none')
        ax.tick_params(colors='#888888')
        for spine in ax.spines.values():
            spine.set_edgecolor('#444444')
            
        trends = stats.get("usage_trends", [])
        if trends:
            dates = [t["date"][-5:] for t in trends] # MM-DD
            counts = [t["count"] for t in trends]
            
            ax.plot(dates, counts, marker='o', linestyle='-', color='#007acc', linewidth=2, markersize=8)
            ax.fill_between(dates, counts, alpha=0.2, color='#007acc')
            ax.set_title("Queries over last 7 days", color='#dddddd')
        else:
            ax.text(0.5, 0.5, "No data available", ha='center', va='center', color='#888888')
            
        self.figure.tight_layout()
        self.canvas.draw()
