"""
Modern dialog components
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QLineEdit, QProgressBar, QDialogButtonBox, QCheckBox, QScrollArea,
    QWidget, QFrame, QGroupBox, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QTextCursor
from ..styles.modern_theme import ModernTheme
import subprocess
import sys
import os
import shutil


class DependencyCheckDialog(QDialog):
    """Moderner Dialog für Dependency-Check"""

    dependencies_checked = pyqtSignal(dict)  # Results of dependency check

    def __init__(self, parent=None):
        super().__init__(parent)
        self.check_results = {}
        self.setup_ui()
        self.start_dependency_check()

    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("🔍 System-Abhängigkeiten prüfen")
        self.setFixedSize(700, 600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        # Icon and title
        title_label = QLabel("🔍 System-Abhängigkeiten")
        title_label.setFont(QFont(ModernTheme.FONT_FAMILY, 20, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ModernTheme.PRIMARY}; background: transparent;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Status indicator
        self.status_label = QLabel("⏳ Prüfung läuft...")
        self.status_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_SECONDARY};
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
            }}
        """)
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel("Überprüfung der erforderlichen Systemkomponenten und Paketmanager.")
        desc_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        desc_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {ModernTheme.BORDER};
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: {ModernTheme.PRIMARY};
                border-radius: 6px;
            }}
        """)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate
        layout.addWidget(self.progress_bar)

        # Results area
        results_group = QGroupBox("📋 Prüfungsergebnisse")
        results_group.setFont(QFont(ModernTheme.FONT_FAMILY, 14, QFont.Weight.Bold))
        results_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                margin-top: 16px;
                padding-top: 16px;
                background-color: {ModernTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                background-color: {ModernTheme.BACKGROUND};
            }}
        """)

        results_layout = QVBoxLayout()

        # Scroll area for results
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)

        self.results_widget = QWidget()
        self.results_widget.setStyleSheet("background-color: transparent;")
        self.results_layout = QVBoxLayout()
        self.results_layout.setSpacing(8)
        self.results_layout.setContentsMargins(12, 12, 12, 12)

        # Add initial loading message
        loading_label = QLabel("🔄 Überprüfung wird durchgeführt...")
        loading_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        loading_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; padding: 20px; background: transparent;")
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.addWidget(loading_label)

        self.results_widget.setLayout(self.results_layout)
        self.results_scroll.setWidget(self.results_widget)
        results_layout.addWidget(self.results_scroll)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group, 1)

        # Auto-install checkbox
        self.auto_install_checkbox = QCheckBox("🚀 Fehlende Komponenten automatisch installieren")
        self.auto_install_checkbox.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        self.auto_install_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {ModernTheme.TEXT_PRIMARY};
                background: transparent;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: 4px;
                background-color: {ModernTheme.SURFACE};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ModernTheme.PRIMARY};
                border-color: {ModernTheme.PRIMARY};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }}
        """)
        self.auto_install_checkbox.setChecked(True)
        layout.addWidget(self.auto_install_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.install_btn = QPushButton("🔧 Installieren")
        self.install_btn.setEnabled(False)
        self.install_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        self.install_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover:enabled {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_DISABLED};
            }}
        """)
        self.install_btn.clicked.connect(self.install_missing_dependencies)
        button_layout.addWidget(self.install_btn)

        self.close_btn = QPushButton("❌ Schließen")
        self.close_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ModernTheme.TEXT_SECONDARY};
                border: 2px solid {ModernTheme.BORDER};
                padding: 12px 24px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.SURFACE_DARK};
                border-color: {ModernTheme.TEXT_SECONDARY};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def start_dependency_check(self):
        """Start the dependency check process"""
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.perform_dependency_check)
        self.check_timer.setSingleShot(True)
        self.check_timer.start(1000)  # Start after 1 second

    def perform_dependency_check(self):
        """Perform the actual dependency check"""
        dependencies = {
            'pacman': {'name': 'Pacman Package Manager', 'command': 'pacman'},
            'flatpak': {'name': 'Flatpak Package Manager', 'command': 'flatpak'},
            'yay': {'name': 'Yay AUR Helper', 'command': 'yay'},
            'paru': {'name': 'Paru AUR Helper', 'command': 'paru'},
            'git': {'name': 'Git Version Control', 'command': 'git'},
            'curl': {'name': 'Curl HTTP Client', 'command': 'curl'},
            'wget': {'name': 'Wget Downloader', 'command': 'wget'},
            'reflector': {'name': 'Reflector Mirror Tool', 'command': 'reflector'}
        }

        # Clear loading message
        self.clear_results_layout()

        missing_deps = []

        for dep_id, dep_info in dependencies.items():
            is_available = shutil.which(dep_info['command']) is not None
            self.check_results[dep_id] = {
                'name': dep_info['name'],
                'command': dep_info['command'],
                'available': is_available,
                'required': dep_id in ['pacman', 'git']  # Mark required dependencies
            }

            if not is_available:
                missing_deps.append(dep_id)

            self.add_dependency_result(dep_info['name'], dep_info['command'], is_available, dep_id in ['pacman', 'git'])

        # Update progress and status
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)

        if missing_deps:
            self.status_label.setText(f"⚠️ {len(missing_deps)} fehlen")
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {ModernTheme.WARNING_LIGHT if ModernTheme.WARNING_LIGHT else '#FFF3CD'};
                    color: {ModernTheme.WARNING_DARK if ModernTheme.WARNING_DARK else '#856404'};
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: 600;
                }}
            """)
            self.install_btn.setEnabled(True)
        else:
            self.status_label.setText("✅ Alle verfügbar")
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {ModernTheme.SUCCESS_LIGHT if ModernTheme.SUCCESS_LIGHT else '#D4EDDA'};
                    color: {ModernTheme.SUCCESS_DARK if ModernTheme.SUCCESS_DARK else '#155724'};
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: 600;
                }}
            """)

        self.dependencies_checked.emit(self.check_results)

    def clear_results_layout(self):
        """Clear the results layout"""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add_dependency_result(self, name, command, available, required):
        """Add a dependency check result to the UI"""
        result_widget = QWidget()
        result_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE_LIGHT};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                margin: 2px 0px;
                padding: 8px;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Status icon
        status_icon = QLabel("✅" if available else "❌")
        status_icon.setFont(QFont(ModernTheme.FONT_FAMILY, 16))
        status_icon.setFixedWidth(30)
        layout.addWidget(status_icon)

        # Name and command
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        name_label = QLabel(name)
        name_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        info_layout.addWidget(name_label)

        cmd_label = QLabel(f"Befehl: {command}")
        cmd_label.setFont(QFont("Consolas", 10))
        cmd_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        info_layout.addWidget(cmd_label)

        layout.addLayout(info_layout, 1)

        # Required badge
        if required:
            req_label = QLabel("ERFORDERLICH")
            req_label.setFont(QFont(ModernTheme.FONT_FAMILY, 8, QFont.Weight.Bold))
            req_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {ModernTheme.ERROR if ModernTheme.ERROR else '#DC3545'};
                    color: white;
                    padding: 3px 8px;
                    border-radius: 8px;
                    font-weight: 600;
                }}
            """)
            layout.addWidget(req_label)

        # Status text
        status_text = QLabel("Verfügbar" if available else "Nicht gefunden")
        status_text.setFont(QFont(ModernTheme.FONT_FAMILY, 10, QFont.Weight.Bold))
        if available:
            status_text.setStyleSheet(f"color: {ModernTheme.SUCCESS if ModernTheme.SUCCESS else '#28A745'}; background: transparent;")
        else:
            status_text.setStyleSheet(f"color: {ModernTheme.ERROR if ModernTheme.ERROR else '#DC3545'}; background: transparent;")
        layout.addWidget(status_text)

        result_widget.setLayout(layout)
        self.results_layout.addWidget(result_widget)

    def install_missing_dependencies(self):
        """Install missing dependencies"""
        missing_deps = [dep for dep, info in self.check_results.items() if not info['available']]

        if not missing_deps:
            QMessageBox.information(self, "Keine Installation nötig", "Alle Abhängigkeiten sind bereits verfügbar.")
            return

        # Show installation dialog
        install_dialog = DependencyInstallDialog(missing_deps, self.check_results, self)
        install_dialog.exec()


class DependencyInstallDialog(QDialog):
    """Dialog for installing missing dependencies"""

    def __init__(self, missing_deps, check_results, parent=None):
        super().__init__(parent)
        self.missing_deps = missing_deps
        self.check_results = check_results
        self.setup_ui()

    def setup_ui(self):
        """Setup installation dialog UI"""
        self.setWindowTitle("🔧 Abhängigkeiten installieren")
        self.setFixedSize(600, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header_label = QLabel("🔧 Installation fehlender Abhängigkeiten")
        header_label.setFont(QFont(ModernTheme.FONT_FAMILY, 18, QFont.Weight.Bold))
        header_label.setStyleSheet(f"color: {ModernTheme.PRIMARY}; background: transparent;")
        layout.addWidget(header_label)

        # Installation commands
        commands_text = QTextEdit()
        commands_text.setReadOnly(True)
        commands_text.setMaximumHeight(200)
        commands_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.SURFACE_DARK};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)

        install_commands = self.generate_install_commands()
        commands_text.setPlainText(install_commands)
        layout.addWidget(commands_text)

        # Warning
        warning_label = QLabel("⚠️ Diese Befehle erfordern Administrator-Rechte (sudo).")
        warning_label.setFont(QFont(ModernTheme.FONT_FAMILY, 11))
        warning_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.WARNING_DARK if ModernTheme.WARNING_DARK else '#856404'};
                background-color: {ModernTheme.WARNING_LIGHT if ModernTheme.WARNING_LIGHT else '#FFF3CD'};
                padding: 12px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                border: 1px solid {ModernTheme.WARNING_DARK if ModernTheme.WARNING_DARK else '#856404'};
            }}
        """)
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        install_btn = QPushButton("🚀 Installieren")
        install_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        install_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
        """)
        install_btn.clicked.connect(self.start_installation)
        button_layout.addWidget(install_btn)

        cancel_btn = QPushButton("❌ Abbrechen")
        cancel_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ModernTheme.TEXT_SECONDARY};
                border: 2px solid {ModernTheme.BORDER};
                padding: 12px 24px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.SURFACE_DARK};
                border-color: {ModernTheme.TEXT_SECONDARY};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def generate_install_commands(self):
        """Generate installation commands for missing dependencies"""
        commands = []

        for dep in self.missing_deps:
            if dep == 'flatpak':
                commands.append("sudo pacman -S flatpak")
            elif dep == 'yay':
                commands.append("sudo pacman -S --needed base-devel git")
                commands.append("git clone https://aur.archlinux.org/yay.git")
                commands.append("cd yay && makepkg -si")
            elif dep == 'paru':
                commands.append("sudo pacman -S --needed base-devel git")
                commands.append("git clone https://aur.archlinux.org/paru.git")
                commands.append("cd paru && makepkg -si")
            elif dep in ['git', 'curl', 'wget', 'reflector']:
                commands.append(f"sudo pacman -S {dep}")

        return "\n".join(commands)

    def start_installation(self):
        """Start the installation process"""
        QMessageBox.information(self, "Installation", "Die Installation wird gestartet...\n\nDieser Vorgang kann einige Minuten dauern.")
        self.close()


class PasswordDialog(QDialog):
    """Moderner Dialog für Passwort-Eingabe"""

    password_entered = pyqtSignal(str)

    def __init__(self, title="Passwort eingeben", message="Bitte geben Sie Ihr Passwort ein:", parent=None):
        super().__init__(parent)
        self.title = title
        self.message = message
        self.setup_ui()

    def setup_ui(self):
        """Setup password dialog UI"""
        self.setWindowTitle(self.title)
        self.setFixedSize(450, 300)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header with icon
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        icon_label = QLabel("🔐")
        icon_label.setFont(QFont(ModernTheme.FONT_FAMILY, 32))
        icon_label.setFixedSize(50, 50)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                border-radius: 25px;
                border: 2px solid {ModernTheme.PRIMARY};
            }}
        """)
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title_label = QLabel(self.title)
        title_label.setFont(QFont(ModernTheme.FONT_FAMILY, 18, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("Administrator-Berechtigung erforderlich")
        subtitle_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        subtitle_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        title_layout.addWidget(subtitle_label)

        header_layout.addLayout(title_layout, 1)
        layout.addLayout(header_layout)

        # Message
        message_label = QLabel(self.message)
        message_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        message_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        # Password input
        input_group = QGroupBox("🔑 Passwort")
        input_group.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        input_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                margin-top: 12px;
                padding-top: 12px;
                background-color: {ModernTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: {ModernTheme.BACKGROUND};
            }}
        """)

        input_layout = QVBoxLayout()
        input_layout.setContentsMargins(16, 16, 16, 16)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Passwort eingeben...")
        self.password_input.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        self.password_input.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: 12px 16px;
                background-color: {ModernTheme.SURFACE_LIGHT};
                color: {ModernTheme.TEXT_PRIMARY};
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {ModernTheme.PRIMARY};
                background-color: white;
            }}
        """)
        self.password_input.returnPressed.connect(self.accept_password)
        input_layout.addWidget(self.password_input)

        # Show password checkbox
        self.show_password_checkbox = QCheckBox("👁️ Passwort anzeigen")
        self.show_password_checkbox.setFont(QFont(ModernTheme.FONT_FAMILY, 10))
        self.show_password_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {ModernTheme.TEXT_SECONDARY};
                background: transparent;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: 3px;
                background-color: {ModernTheme.SURFACE};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ModernTheme.PRIMARY};
                border-color: {ModernTheme.PRIMARY};
            }}
        """)
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        input_layout.addWidget(self.show_password_checkbox)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_btn = QPushButton("✅ OK")
        ok_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: {ModernTheme.PRIMARY_DARK};
                transform: translateY(1px);
            }}
        """)
        ok_btn.clicked.connect(self.accept_password)
        button_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("❌ Abbrechen")
        cancel_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ModernTheme.TEXT_SECONDARY};
                border: 2px solid {ModernTheme.BORDER};
                padding: 12px 24px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.SURFACE_DARK};
                border-color: {ModernTheme.TEXT_SECONDARY};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Focus on password input
        self.password_input.setFocus()

    def toggle_password_visibility(self, state):
        """Toggle password visibility"""
        if state == Qt.CheckState.Checked.value:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def accept_password(self):
        """Accept password and emit signal"""
        password = self.password_input.text()
        if password.strip():
            self.password_entered.emit(password)
            self.accept()
        else:
            # Show error for empty password
            self.password_input.setStyleSheet(f"""
                QLineEdit {{
                    border: 2px solid {ModernTheme.ERROR if ModernTheme.ERROR else '#DC3545'};
                    border-radius: {ModernTheme.RADIUS_SMALL};
                    padding: 12px 16px;
                    background-color: {ModernTheme.SURFACE_LIGHT};
                    color: {ModernTheme.TEXT_PRIMARY};
                    font-size: 12px;
                }}
            """)
            self.password_input.setPlaceholderText("Passwort darf nicht leer sein!")

    def get_password(self):
        """Get the entered password"""
        return self.password_input.text()


class CommandExecutionDialog(QDialog):
    """Moderner Dialog für Befehlsausführung"""

    execution_finished = pyqtSignal(bool, str)  # success, output

    def __init__(self, commands, title="Befehle ausführen", parent=None):
        super().__init__(parent)
        self.commands = commands if isinstance(commands, list) else [commands]
        self.title = title
        self.current_command_index = 0
        self.execution_success = True
        self.full_output = ""
        self.process = None
        self.setup_ui()

    def setup_ui(self):
        """Setup command execution dialog UI"""
        self.setWindowTitle(self.title)
        self.setFixedSize(800, 600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        title_label = QLabel(f"⚡ {self.title}")
        title_label.setFont(QFont(ModernTheme.FONT_FAMILY, 20, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ModernTheme.PRIMARY}; background: transparent;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Status indicator
        self.status_label = QLabel("⏳ Bereit")
        self.status_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_SECONDARY};
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
            }}
        """)
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

        # Command info
        info_group = QGroupBox(f"📋 Befehle ({len(self.commands)} Gesamt)")
        info_group.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        info_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                margin-top: 12px;
                padding-top: 12px;
                background-color: {ModernTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: {ModernTheme.BACKGROUND};
            }}
        """)

        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(16, 16, 16, 16)

        # Commands preview
        commands_text = QTextEdit()
        commands_text.setReadOnly(True)
        commands_text.setMaximumHeight(120)
        commands_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.SURFACE_DARK};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)
        commands_text.setPlainText("\n".join(self.commands))
        info_layout.addWidget(commands_text)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Progress section
        progress_group = QGroupBox("⚡ Ausführung")
        progress_group.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        progress_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                margin-top: 12px;
                padding-top: 12px;
                background-color: {ModernTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: {ModernTheme.BACKGROUND};
            }}
        """)

        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(16, 16, 16, 16)
        progress_layout.setSpacing(12)

        # Current command
        self.current_command_label = QLabel("Bereit zum Start...")
        self.current_command_label.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        self.current_command_label.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        self.current_command_label.setWordWrap(True)
        progress_layout.addWidget(self.current_command_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {ModernTheme.BORDER};
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.TEXT_PRIMARY};
                min-height: 24px;
            }}
            QProgressBar::chunk {{
                background-color: {ModernTheme.PRIMARY};
                border-radius: 6px;
            }}
        """)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(len(self.commands))
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Output section
        output_group = QGroupBox("📄 Ausgabe")
        output_group.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        output_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                margin-top: 12px;
                padding-top: 12px;
                background-color: {ModernTheme.SURFACE};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background-color: {ModernTheme.BACKGROUND};
            }}
        """)

        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(16, 16, 16, 16)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.SURFACE_DARK};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)
        self.output_text.setPlainText("Bereit für Ausgabe...")
        output_layout.addWidget(self.output_text)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group, 1)

        # Buttons
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("🚀 Starten")
        self.start_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover:enabled {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_DISABLED};
            }}
        """)
        self.start_btn.clicked.connect(self.start_execution)
        button_layout.addWidget(self.start_btn)

        button_layout.addStretch()

        self.stop_btn = QPushButton("⏹️ Stoppen")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.ERROR if ModernTheme.ERROR else '#DC3545'};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover:enabled {{
                background-color: {ModernTheme.ERROR_DARK if ModernTheme.ERROR_DARK else '#C82333'};
            }}
            QPushButton:disabled {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_DISABLED};
            }}
        """)
        self.stop_btn.clicked.connect(self.stop_execution)
        button_layout.addWidget(self.stop_btn)

        self.close_btn = QPushButton("❌ Schließen")
        self.close_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ModernTheme.TEXT_SECONDARY};
                border: 2px solid {ModernTheme.BORDER};
                padding: 12px 24px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.SURFACE_DARK};
                border-color: {ModernTheme.TEXT_SECONDARY};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def start_execution(self):
        """Start command execution"""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.current_command_index = 0
        self.execution_success = True
        self.full_output = ""

        self.status_label.setText("🔄 Läuft...")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                color: {ModernTheme.PRIMARY_DARK};
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 600;
            }}
        """)

        self.output_text.clear()
        self.execute_next_command()

    def execute_next_command(self):
        """Execute the next command in the queue"""
        if self.current_command_index >= len(self.commands):
            self.execution_finished_handler()
            return

        command = self.commands[self.current_command_index]
        self.current_command_label.setText(f"Befehl {self.current_command_index + 1}/{len(self.commands)}: {command}")

        # Update progress
        self.progress_bar.setValue(self.current_command_index)

        # Add command to output
        self.add_output(f"\n{'='*50}")
        self.add_output(f"BEFEHL {self.current_command_index + 1}: {command}")
        self.add_output(f"{'='*50}\n")

        # Start execution
        try:
            self.process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Create a timer to read output
            self.output_timer = QTimer()
            self.output_timer.timeout.connect(self.read_process_output)
            self.output_timer.start(100)  # Read every 100ms

        except Exception as e:
            self.add_output(f"FEHLER: {str(e)}\n")
            self.execution_success = False
            self.current_command_index += 1
            QTimer.singleShot(500, self.execute_next_command)

    def read_process_output(self):
        """Read output from the running process"""
        if self.process is None:
            return

        # Check if process is still running
        if self.process.poll() is None:
            # Process is still running, read available output
            try:
                output = self.process.stdout.readline()
                if output:
                    self.add_output(output.rstrip())
            except:
                pass
        else:
            # Process finished
            self.output_timer.stop()

            # Read remaining output
            try:
                remaining_output = self.process.stdout.read()
                if remaining_output:
                    self.add_output(remaining_output.rstrip())
            except:
                pass

            # Check return code
            if self.process.returncode != 0:
                self.add_output(f"\nBEFEHL FEHLGESCHLAGEN (Exit Code: {self.process.returncode})")
                self.execution_success = False
            else:
                self.add_output("\nBEFEHL ERFOLGREICH")

            # Move to next command
            self.current_command_index += 1
            self.process = None
            QTimer.singleShot(1000, self.execute_next_command)

    def add_output(self, text):
        """Add text to output area"""
        self.output_text.append(text)
        self.full_output += text + "\n"

        # Auto-scroll to bottom
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)

    def stop_execution(self):
        """Stop command execution"""
        if self.process:
            try:
                self.process.terminate()
                QTimer.singleShot(3000, lambda: self.process.kill() if self.process.poll() is None else None)
            except:
                pass

        if hasattr(self, 'output_timer'):
            self.output_timer.stop()

        self.add_output("\n\n>>> AUSFÜHRUNG GESTOPPT <<<")
        self.execution_success = False
        self.execution_finished_handler()

    def execution_finished_handler(self):
        """Handle execution completion"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.progress_bar.setValue(len(self.commands))

        if self.execution_success:
            self.status_label.setText("✅ Erfolgreich")
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {ModernTheme.SUCCESS_LIGHT if ModernTheme.SUCCESS_LIGHT else '#D4EDDA'};
                    color: {ModernTheme.SUCCESS_DARK if ModernTheme.SUCCESS_DARK else '#155724'};
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: 600;
                }}
            """)
            self.current_command_label.setText("Alle Befehle erfolgreich ausgeführt!")
        else:
            self.status_label.setText("❌ Fehler")
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {ModernTheme.ERROR_LIGHT if ModernTheme.ERROR_LIGHT else '#F8D7DA'};
                    color: {ModernTheme.ERROR_DARK if ModernTheme.ERROR_DARK else '#721C24'};
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: 600;
                }}
            """)
            self.current_command_label.setText("Ausführung mit Fehlern beendet.")

        self.add_output(f"\n{'='*50}")
        self.add_output("AUSFÜHRUNG BEENDET")
        self.add_output(f"Status: {'ERFOLGREICH' if self.execution_success else 'MIT FEHLERN'}")
        self.add_output(f"{'='*50}")

        # Emit finished signal
        self.execution_finished.emit(self.execution_success, self.full_output)

    def closeEvent(self, event):
        """Handle dialog close event"""
        if self.process and self.process.poll() is None:
            reply = QMessageBox.question(
                self,
                "Ausführung läuft",
                "Ein Befehl wird noch ausgeführt. Möchten Sie die Ausführung stoppen und schließen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.stop_execution()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


# Export all dialog classes
__all__ = [
    'DependencyCheckDialog',
    'DependencyInstallDialog',
    'PasswordDialog',
    'CommandExecutionDialog'
]
