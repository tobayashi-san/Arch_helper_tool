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
        header.setStyleSheet("""
            QLabel#statusTitle {
                font-size: 14px;
                font-weight: 600;
                color: #495057;
                margin: 8px 0px 4px 0px;
            }
        """)
        layout.addWidget(header)

        # Status container
        self.status_container = QFrame()
        self.status_container.setObjectName("statusContainer")
        self.status_container.setStyleSheet("""
            QFrame#statusContainer {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        self.status_layout = QVBoxLayout()
        self.status_layout.setSpacing(8)
        self.status_container.setLayout(self.status_layout)

        layout.addWidget(self.status_container)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.setStyleSheet("""
            QPushButton#refreshButton {
                background-color: #f8f9fa;
                color: #495057;
                border: 1px solid #dee2e6;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#refreshButton:hover {
                background-color: #e9ecef;
            }
        """)
        refresh_btn.clicked.connect(self.update_status)
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_btn)

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

        # Disk space (simple check)
        self.add_disk_space_status()

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

    def add_disk_space_status(self):
        """Add disk space status (simplified)"""
        try:
            import os
            statvfs = os.statvfs('/')
            free_bytes = statvfs.f_frsize * statvfs.f_available
            total_bytes = statvfs.f_frsize * statvfs.f_blocks

            free_gb = free_bytes / (1024**3)
            total_gb = total_bytes / (1024**3)
            used_percent = ((total_bytes - free_bytes) / total_bytes) * 100

            status_color = "#28a745" if used_percent < 80 else "#ffc107" if used_percent < 90 else "#dc3545"

            self.add_status_item("💾", "Disk Space", f"{free_gb:.1f}GB free", status_color)

        except Exception:
            self.add_status_item("💾", "Disk Space", "Unknown", "#6c757d")

class QuickActionsWidget(QWidget):
    """Quick actions widget for common tasks"""

    action_triggered = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup quick actions UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header
        header = QLabel("⚡ Quick Actions")
        header.setObjectName("quickActionsTitle")
        header.setStyleSheet("""
            QLabel#quickActionsTitle {
                font-size: 14px;
                font-weight: 600;
                color: #495057;
                margin: 8px 0px 4px 0px;
            }
        """)
        layout.addWidget(header)

        # Actions container
        actions_container = QFrame()
        actions_container.setObjectName("actionsContainer")
        actions_container.setStyleSheet("""
            QFrame#actionsContainer {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 8px;
            }
        """)

        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(6)

        # Quick action buttons
        actions = [
            ("🔄", "System Update", "system_update"),
            ("🧹", "Clean Cache", "clean_cache"),
            ("🔍", "Check Deps", "check_deps"),
            ("📊", "Show Stats", "show_stats")
        ]

        for icon, text, action in actions:
            btn = self.create_quick_action_button(icon, text, action)
            actions_layout.addWidget(btn)

        actions_container.setLayout(actions_layout)
        layout.addWidget(actions_container)

        self.setLayout(layout)

    def create_quick_action_button(self, icon, text, action):
        """Create a quick action button"""
        btn = QPushButton(f"{icon} {text}")
        btn.setObjectName("quickActionButton")
        btn.setStyleSheet("""
            QPushButton#quickActionButton {
                background-color: #f8f9fa;
                color: #495057;
                border: 1px solid #dee2e6;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                text-align: left;
            }
            QPushButton#quickActionButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            QPushButton#quickActionButton:pressed {
                background-color: #dee2e6;
            }
        """)

        btn.clicked.connect(lambda: self.action_triggered.emit(action))
        return btn

class SystemInfoWidget(QWidget):
    """Detailed system information widget"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_system_info()

    def setup_ui(self):
        """Setup system info UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header
        header = QLabel("ℹ️ System Information")
        header.setObjectName("systemInfoTitle")
        header.setStyleSheet("""
            QLabel#systemInfoTitle {
                font-size: 14px;
                font-weight: 600;
                color: #495057;
                margin: 8px 0px 4px 0px;
            }
        """)
        layout.addWidget(header)

        # Info container
        self.info_container = QFrame()
        self.info_container.setObjectName("infoContainer")
        self.info_container.setStyleSheet("""
            QFrame#infoContainer {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        self.info_layout = QVBoxLayout()
        self.info_layout.setSpacing(6)
        self.info_container.setLayout(self.info_layout)

        layout.addWidget(self.info_container)
        self.setLayout(layout)

    def load_system_info(self):
        """Load and display system information"""
        info_items = [
            ("OS", self.get_os_info()),
            ("Kernel", platform.release()),
            ("Python", platform.python_version()),
            ("Architecture", platform.machine()),
            ("Processor", platform.processor() or "Unknown")
        ]

        for label, value in info_items:
            self.add_info_item(label, value)

    def get_os_info(self):
        """Get OS information"""
        try:
            # Try to read from /etc/os-release
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('PRETTY_NAME='):
                        return line.split('=')[1].strip().strip('"')
        except:
            pass

        return f"{platform.system()} {platform.release()}"

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
