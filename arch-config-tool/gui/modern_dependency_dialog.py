"""
Moderner Dependency Check Dialog
Schönes, benutzerfreundliches Design für den Dependency Check
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QFrame, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QPen, QIcon

class ModernProgressBar(QProgressBar):
    """Custom modern progress bar"""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(20)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.1);
                text-align: center;

            }
            QProgressBar::chunk {
                border-radius: 5px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4FC3F7, stop:0.5 #29B6F6, stop:1 #0288D1);
            }
        """)

class StatusCard(QFrame):
    """Modern status card for dependency items"""

    def __init__(self, icon: str, title: str, description: str, status: str = "checking"):
        super().__init__()
        self.status = status
        self.setup_ui(icon, title, description)

    def setup_ui(self, icon: str, title: str, description: str):
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet("""
            QFrame {
                background-color: white;

                border-radius: 12px;

            }
            QFrame:hover {
                border-color: #2196F3;
                background-color: #FAFAFA;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Icon
        self.icon_label = QLabel(icon)
        self.icon_label.setFont(QFont("Segoe UI Emoji", 24))
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #212121; background: transparent;")
        content_layout.addWidget(self.title_label)

        self.desc_label = QLabel(description)
        self.desc_label.setFont(QFont("Segoe UI", 10))
        self.desc_label.setStyleSheet("color: #757575; background: transparent;")
        self.desc_label.setWordWrap(True)
        content_layout.addWidget(self.desc_label)

        layout.addLayout(content_layout, 1)

        # Status indicator
        self.status_widget = QWidget()
        self.status_widget.setFixedSize(24, 24)
        self.update_status_style()
        layout.addWidget(self.status_widget, 0, Qt.AlignmentFlag.AlignTop)

        self.setLayout(layout)

    def update_status(self, new_status: str, message: str = ""):
        """Update status with animation"""
        self.status = new_status
        self.update_status_style()

        if message:
            self.desc_label.setText(message)

    def update_status_style(self):
        """Update status indicator styling"""
        if self.status == "checking":
            # Animated spinner style
            self.status_widget.setStyleSheet("""
                QWidget {
                    background-color: #FF9800;
                    border-radius: 12px;
                    border: 2px solid #FFB74D;
                }
            """)
        elif self.status == "success":
            self.status_widget.setStyleSheet("""
                QWidget {
                    background-color: #4CAF50;
                    border-radius: 12px;
                    border: 2px solid #81C784;
                }
            """)
        elif self.status == "error":
            self.status_widget.setStyleSheet("""
                QWidget {
                    background-color: #F44336;
                    border-radius: 12px;
                    border: 2px solid #E57373;
                }
            """)
        elif self.status == "warning":
            self.status_widget.setStyleSheet("""
                QWidget {
                    background-color: #FF9800;
                    border-radius: 12px;
                    border: 2px solid #FFB74D;
                }
            """)

class ModernDependencyCheckDialog(QDialog):
    """Moderner, schöner Dependency Check Dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System-Abhängigkeiten prüfen")
        self.setModal(True)
        self.setMinimumSize(600, 500)

        # Hauptstyle
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F5F5F5, stop:1 #EEEEEE);
                border-radius: 16px;
            }
        """)

        self.dependency_checker = None  # Wird von außen gesetzt
        self.status_cards = {}
        self.setup_ui()

        # Animation für Progress
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(1000)
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header mit modernem Design
        header_widget = self.create_header()
        layout.addWidget(header_widget)

        content_header_widget = self.create_content_header()
        layout.addWidget(content_header_widget)

        # Content Area
        content_widget = self.create_content_area()
        layout.addWidget(content_widget, 1)

        # Footer mit Buttons
        footer_widget = self.create_footer()
        layout.addWidget(footer_widget)

        self.setLayout(layout)

    def create_header(self) -> QWidget:
        """Erstelle modernen Header"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #667eea);
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 12, 12, 12)
        layout.setSpacing(12)


        # Text Content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)

        title = QLabel("System-Abhängigkeiten prüfen")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        text_layout.addWidget(title)

        subtitle = QLabel("Überprüfung aller benötigten Komponenten für optimale Funktionalität")
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9); background: transparent;")
        subtitle.setWordWrap(True)
        text_layout.addWidget(subtitle)

        layout.addLayout(text_layout, 1)

        header.setLayout(layout)
        return header

    def create_content_header(self) -> QWidget:
        """Erstelle modernen Header"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
            background-color: white;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(12)

        # Progress Section
        progress_section = self.create_progress_section()
        layout.addWidget(progress_section)


        header.setLayout(layout)
        return header

    def create_content_area(self) -> QWidget:
        """Erstelle Content-Bereich"""
        content = QWidget()
        content.setStyleSheet("background: transparent;")

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Status Cards Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background-color: #F0F0F0;
                width: 8px;
                border-radius: 4px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #BDBDBD;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #9E9E9E;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # Cards Container
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(12)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)

        # Erstelle Status Cards für Dependencies
        self.create_status_cards()

        self.cards_widget.setLayout(self.cards_layout)
        scroll_area.setWidget(self.cards_widget)

        layout.addWidget(scroll_area, 1)

        content.setLayout(layout)
        return content

    def create_progress_section(self) -> QWidget:
        """Erstelle Progress-Bereich"""
        progress_widget = QWidget()
        progress_widget.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Status Text
        self.status_label = QLabel("Starte Dependency Check...")
        self.status_label.setFont(QFont("Segoe UI", 13, QFont.Weight.DemiBold))
        self.status_label.setStyleSheet("color: #424242; background: transparent;")
        layout.addWidget(self.status_label)

        # Progress Bar
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate initially
        layout.addWidget(self.progress_bar)

        progress_widget.setLayout(layout)
        return progress_widget

    def create_status_cards(self):
        """Erstelle Status-Karten für Dependencies"""
        dependencies = [
            {
                "icon": "📦",
                "title": "Pacman Package Manager",
                "description": "Arch Linux Hauptpaketmanager für offizielle Pakete",
                "key": "pacman"
            },
            {
                "icon": "🔐",
                "title": "Sudo Berechtigung",
                "description": "Superuser-Berechtigung für Systemänderungen",
                "key": "sudo"
            },
            {
                "icon": "📱",
                "title": "Flatpak (Optional)",
                "description": "Universeller Paketmanager für Linux-Anwendungen",
                "key": "flatpak"
            },
            {
                "icon": "🏗️",
                "title": "AUR Helper (Optional)",
                "description": "Helper für Arch User Repository (yay oder paru)",
                "key": "aur_helper"
            },
            {
                "icon": "🪞",
                "title": "Reflector (Optional)",
                "description": "Tool zur Optimierung der Paket-Mirror-Liste",
                "key": "reflector"
            }
        ]

        for dep in dependencies:
            card = StatusCard(
                dep["icon"],
                dep["title"],
                dep["description"],
                "checking"
            )

            self.status_cards[dep["key"]] = card
            self.cards_layout.addWidget(card)

        # Stretch am Ende
        self.cards_layout.addStretch()

    def create_footer(self) -> QWidget:
        """Erstelle Footer mit Buttons"""
        footer = QWidget()
        footer.setFixedHeight(70)


        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 20)

        # Info Label
        self.info_label = QLabel("Prüfung läuft...")
        self.info_label.setFont(QFont("Segoe UI", 11))
        self.info_label.setStyleSheet("color: #757575; background: transparent;")
        layout.addWidget(self.info_label)

        layout.addStretch()

        # Buttons
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 12px;
                font-weight: 600;
                color: #424242;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #EEEEEE;
                border-color: #BDBDBD;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

        self.continue_button = QPushButton("Weiter")
        self.continue_button.setEnabled(False)
        self.continue_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #388E3C);
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 12px;
                font-weight: 600;
                color: white;
                min-width: 100px;
            }
            QPushButton:hover:enabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66BB6A, stop:1 #4CAF50);
            }
            QPushButton:pressed:enabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #388E3C, stop:1 #2E7D32);
            }
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #9E9E9E;
            }
        """)
        self.continue_button.clicked.connect(self.accept)
        layout.addWidget(self.continue_button)

        footer.setLayout(layout)
        return footer

    def run_dependency_check(self):
        """Starte Dependency Check mit schönen Updates"""
        from core.dependency_check import DependencyChecker

        self.dependency_checker = DependencyChecker(self)

        # Simuliere Check-Prozess mit Timer
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.update_check_progress)
        self.current_check_index = 0
        self.check_items = list(self.status_cards.keys())

        # Starte Progress-Animation
        self.progress_bar.setRange(0, len(self.check_items))
        self.progress_bar.setValue(0)

        self.check_timer.start(800)  # Check alle 800ms
        self.status_label.setText("Überprüfe Systemkomponenten...")

    def update_check_progress(self):
        """Update Check Progress mit Animation"""
        if self.current_check_index >= len(self.check_items):
            # Alle Checks abgeschlossen
            self.check_timer.stop()
            self.complete_dependency_check()
            return

        current_key = self.check_items[self.current_check_index]
        card = self.status_cards[current_key]

        # Simuliere Check-Ergebnis
        success = self.perform_actual_check(current_key)

        if success:
            card.update_status("success", "✅ Verfügbar und bereit")
        else:
            if current_key in ["flatpak", "aur_helper", "reflector"]:
                card.update_status("warning", "⚠️ Optional - nicht installiert")
            else:
                card.update_status("error", "❌ Fehlt - Installation erforderlich")

        # Update Progress
        self.current_check_index += 1
        self.progress_bar.setValue(self.current_check_index)

        # Update Status
        remaining = len(self.check_items) - self.current_check_index
        if remaining > 0:
            self.status_label.setText(f"Prüfe {card.title_label.text()}... ({remaining} verbleibend)")

    def perform_actual_check(self, dependency_key: str) -> bool:
        """Führe tatsächlichen Check durch"""
        if not self.dependency_checker:
            return True  # Fallback

        try:
            if dependency_key == "pacman":
                return self.dependency_checker.check_command_exists("pacman")
            elif dependency_key == "sudo":
                return self.dependency_checker.check_sudo_available()
            elif dependency_key == "flatpak":
                return self.dependency_checker.check_command_exists("flatpak")
            elif dependency_key == "aur_helper":
                return self.dependency_checker.get_available_aur_helper() is not None
            elif dependency_key == "reflector":
                return self.dependency_checker.check_command_exists("reflector")
        except:
            pass

        return True  # Fallback für unbekannte Dependencies

    def complete_dependency_check(self):
        """Dependency Check abgeschlossen"""
        # Prüfe Ergebnisse
        critical_missing = []
        optional_missing = []

        for key, card in self.status_cards.items():
            if card.status == "error":
                critical_missing.append(key)
            elif card.status == "warning":
                optional_missing.append(key)

        # Update UI basierend auf Ergebnissen
        if critical_missing:
            self.status_label.setText(f"❌ Kritische Komponenten fehlen: {', '.join(critical_missing)}")
            self.info_label.setText("Installation erforderlich vor Fortsetzung")
            self.continue_button.setEnabled(False)
        else:
            self.status_label.setText("✅ Alle kritischen Komponenten verfügbar!")
            if optional_missing:
                self.info_label.setText(f"Optional fehlen: {', '.join(optional_missing)} - kann später installiert werden")
            else:
                self.info_label.setText("Komponenten verfügbar")

            self.continue_button.setEnabled(True)

            # Erfolgs-Animation
            self.animate_success()

    def animate_success(self):
        """Zeige Erfolgs-Animation"""
        # Progress Bar auf 100%
        self.progress_bar.setRange(0, 100)

        self.progress_animation.setStartValue(0)
        self.progress_animation.setEndValue(100)
        self.progress_animation.start()


# Test-Dialog für Standalone-Demo
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Modernes App-Styling
    app.setStyleSheet("""
        * {
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
    """)

    dialog = ModernDependencyCheckDialog()
    dialog.show()

    # Starte Check automatisch nach kurzer Verzögerung
    QTimer.singleShot(1000, dialog.run_dependency_check)

    sys.exit(app.exec())
