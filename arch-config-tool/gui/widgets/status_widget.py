"""
Status Widget - Shows system status and quick info
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
import shutil
import platform

class StatusWidget(QWidget):
    """System status and information widget"""

    refresh_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_timer()
        self.update_status()

    def setup_ui(self):
        """Setup status widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header
        header = QLabel("📊 System Status")
        header.setObjectName("statusTitle")

        layout.addWidget(header)

        # Status container
        self.status_container = QFrame()
        self.status_container.setObjectName("statusContainer")


        self.status_layout = QVBoxLayout()
        self.status_layout.setSpacing(8)
        self.status_container.setLayout(self.status_layout)

        layout.addWidget(self.status_container)



        self.setLayout(layout)

    def setup_timer(self):
        """Setup auto-refresh timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(30000)  # Update every 30 seconds

    def update_status(self):
        """Update system status information"""
        # Clear existing status items
        while self.status_layout.count():
            child = self.status_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # System info
        self.add_status_item("💻", "System", platform.system())
        self.add_status_item("🏗️", "Architecture", platform.machine())

        # Package managers
        self.add_package_manager_status()



    def add_status_item(self, icon, label, value, status_color="#28a745"):
        """Add a status item"""
        item_widget = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(8)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setFixedWidth(20)
        item_layout.addWidget(icon_label)

        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-size: 12px; color: #6c757d; font-weight: 600;")
        item_layout.addWidget(label_widget)

        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"font-size: 12px; color: {status_color}; font-weight: 600;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        item_layout.addWidget(value_label, 1)

        item_widget.setLayout(item_layout)
        self.status_layout.addWidget(item_widget)

    def add_package_manager_status(self):
        """Check and display package manager status"""
        managers = {
            "pacman": "📦",
            "flatpak": "📱",
            "yay": "🔧",
            "paru": "🔧"
        }

        for manager, icon in managers.items():
            if shutil.which(manager):
                self.add_status_item(icon, manager.title(), "Available", "#28a745")
            else:
                self.add_status_item(icon, manager.title(), "Missing", "#dc3545")


class QuickActionsWidget(QWidget):
    """Quick actions widget for common tasks"""

    action_triggered = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setup_ui()




    def add_info_item(self, label, value):
        """Add an information item"""
        item_widget = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(8)

        # Label
        label_widget = QLabel(f"{label}:")
        label_widget.setStyleSheet("font-size: 12px; color: #6c757d; font-weight: 600;")
        label_widget.setFixedWidth(80)
        item_layout.addWidget(label_widget)

        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet("font-size: 12px; color: #495057;")
        value_label.setWordWrap(True)
        item_layout.addWidget(value_label, 1)

        item_widget.setLayout(item_layout)
        self.info_layout.addWidget(item_widget)
