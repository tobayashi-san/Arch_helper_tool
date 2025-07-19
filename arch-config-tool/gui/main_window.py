"""
Main Window
Primary Qt6 application window with unified modern design
"""

import sys
import os
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QListWidget, QListWidgetItem,
    QSplitter, QGroupBox, QProgressBar, QLineEdit, QComboBox,
    QMessageBox, QDialog, QDialogButtonBox, QCheckBox, QScrollArea,
    QFrame, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor

# Import our backend modules
try:
    from core.dependency_check import DependencyChecker
    from core.config_manager import ConfigManager, ConfigCategory, ConfigItem
    from core.command_executor import CommandExecutor, CommandResult, CommandStatus
except ImportError:
    # Fallback für relative imports
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from core.dependency_check import DependencyChecker
    from core.config_manager import ConfigManager, ConfigCategory, ConfigItem
    from core.command_executor import CommandExecutor, CommandResult, CommandStatus

class ModernTheme:
    """Zentrale Design-Konstanten für einheitliches Styling"""

    # Farbschema
    PRIMARY = "#2196F3"
    PRIMARY_DARK = "#1976D2"
    PRIMARY_LIGHT = "#BBDEFB"

    SECONDARY = "#FF5722"
    SECONDARY_DARK = "#D84315"
    SECONDARY_LIGHT = "#FFCCBC"

    SUCCESS = "#4CAF50"
    SUCCESS_DARK = "#388E3C"
    WARNING = "#FF9800"
    ERROR = "#F44336"

    # Neutral Colors
    BACKGROUND = "#FAFAFA"
    SURFACE = "#FFFFFF"
    SURFACE_DARK = "#F5F5F5"

    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_DISABLED = "#BDBDBD"

    BORDER = "#E0E0E0"
    BORDER_DARK = "#BDBDBD"

    # Shadows & Effects
    SHADOW_LIGHT = "0px 2px 4px rgba(0,0,0,0.1)"
    SHADOW_MEDIUM = "0px 4px 8px rgba(0,0,0,0.15)"
    SHADOW_HEAVY = "0px 8px 16px rgba(0,0,0,0.2)"

    # Radii
    RADIUS_SMALL = "6px"
    RADIUS_MEDIUM = "12px"
    RADIUS_LARGE = "16px"

    # Spacing
    SPACING_XS = "4px"
    SPACING_SM = "8px"
    SPACING_MD = "16px"
    SPACING_LG = "24px"
    SPACING_XL = "32px"

    # Fonts
    FONT_FAMILY = "Segoe UI, Arial, sans-serif"
    FONT_SIZE_SM = "11px"
    FONT_SIZE_MD = "12px"
    FONT_SIZE_LG = "14px"
    FONT_SIZE_XL = "16px"
    FONT_SIZE_XXL = "20px"

    @classmethod
    def get_button_style(cls, variant="primary", size="medium"):
        """Einheitliche Button-Styles"""
        base_style = f"""
            QPushButton {{
                font-family: {cls.FONT_FAMILY};
                font-weight: 600;
                border: none;
                border-radius: {cls.RADIUS_SMALL};
            }}
            QPushButton:disabled {{
                background-color: {cls.TEXT_DISABLED};
                color: white;
            }}
        """

        # Size variants
        if size == "small":
            base_style += f"""
            QPushButton {{
                padding: {cls.SPACING_XS} {cls.SPACING_SM};
                font-size: {cls.FONT_SIZE_SM};
                min-height: 28px;
            }}
            """
        elif size == "large":
            base_style += f"""
            QPushButton {{
                padding: {cls.SPACING_MD} {cls.SPACING_LG};
                font-size: {cls.FONT_SIZE_LG};
                min-height: 44px;
            }}
            """
        else:  # medium
            base_style += f"""
            QPushButton {{
                padding: {cls.SPACING_SM} {cls.SPACING_MD};
                font-size: {cls.FONT_SIZE_MD};
                min-height: 36px;
            }}
            """

        # Color variants
        if variant == "primary":
            base_style += f"""
            QPushButton {{
                background-color: {cls.PRIMARY};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {cls.PRIMARY_DARK};
            }}
            """
        elif variant == "secondary":
            base_style += f"""
            QPushButton {{
                background-color: {cls.SECONDARY};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {cls.SECONDARY_DARK};
            }}
            """
        elif variant == "success":
            base_style += f"""
            QPushButton {{
                background-color: {cls.SUCCESS};
                color: white;
            }}
            QPushButton:hover {{
                background-color: {cls.SUCCESS_DARK};
            }}
            """
        elif variant == "outline":
            base_style += f"""
            QPushButton {{
                background-color: transparent;
                color: {cls.PRIMARY};
                border: 2px solid {cls.PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {cls.PRIMARY};
                color: white;
            }}
            """
        elif variant == "ghost":
            base_style += f"""
            QPushButton {{
                background-color: {cls.SURFACE_DARK};
                color: {cls.TEXT_PRIMARY};
                border: 1px solid {cls.BORDER};
            }}
            QPushButton:hover {{
                background-color: {cls.BORDER};
                border-color: {cls.BORDER_DARK};
            }}
            """

        return base_style

    @classmethod
    def get_card_style(cls, elevated=True):
        """Einheitliche Card-Styles"""
        return f"""
            QWidget {{
                background-color: {cls.SURFACE};
                border: 1px solid {cls.BORDER};
                border-radius: {cls.RADIUS_MEDIUM};
            }}
            QWidget:hover {{
                border-color: {cls.PRIMARY_LIGHT};
            }}
        """

    @classmethod
    def get_input_style(cls):
        """Einheitliche Input-Styles"""
        return f"""
            QLineEdit, QTextEdit, QComboBox {{
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MD};
                padding: {cls.SPACING_SM} {cls.SPACING_MD};
                border: 2px solid {cls.BORDER};
                border-radius: {cls.RADIUS_SMALL};
                background-color: {cls.SURFACE};
                color: {cls.TEXT_PRIMARY};
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border-color: {cls.PRIMARY};
                outline: none;
            }}
            QLineEdit:hover, QTextEdit:hover, QComboBox:hover {{
                border-color: {cls.BORDER_DARK};
            }}
        """

class DependencyCheckDialog(QDialog):
    """Moderner Dialog für Dependency-Check"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System-Abhängigkeiten prüfen")
        self.setModal(True)
        self.setFixedSize(600, 450)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
                font-family: {ModernTheme.FONT_FAMILY};
            }}
        """)

        self.dependency_checker = DependencyChecker(self)
        self.setup_ui()
        self.run_check()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(int(ModernTheme.SPACING_LG.replace('px', '')))
        layout.setContentsMargins(32, 32, 32, 32)

        # Header Card
        header_card = QWidget()
        header_card.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {ModernTheme.PRIMARY}, stop:1 {ModernTheme.PRIMARY_DARK});
                border-radius: {ModernTheme.RADIUS_LARGE};
                padding: {ModernTheme.SPACING_LG};
            }}
        """)

        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon
        icon_label = QLabel("🔍")
        icon_label.setFont(QFont(ModernTheme.FONT_FAMILY, 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(icon_label)

        # Title
        title = QLabel("System-Abhängigkeiten werden überprüft")
        title.setFont(QFont(ModernTheme.FONT_FAMILY, 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; background: transparent;")
        header_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Bitte warten, während alle benötigten Komponenten geprüft werden...")
        subtitle.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: rgba(255,255,255,0.9); background: transparent;")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)

        header_card.setLayout(header_layout)
        layout.addWidget(header_card)

        # Progress
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setFixedHeight(8)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {ModernTheme.BORDER};
            }}
            QProgressBar::chunk {{
                border-radius: 4px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ModernTheme.PRIMARY}, stop:1 {ModernTheme.PRIMARY_DARK});
            }}
        """)
        layout.addWidget(self.progress)

        # Output Card
        output_card = QWidget()
        output_card.setStyleSheet(ModernTheme.get_card_style())

        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(20, 20, 20, 20)

        output_header = QLabel("Prüfungsdetails")
        output_header.setFont(QFont(ModernTheme.FONT_FAMILY, 14, QFont.Weight.Bold))
        output_header.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        output_layout.addWidget(output_header)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("JetBrains Mono, Consolas, monospace", 10))
        self.output.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.TEXT_PRIMARY};
                color: #00FF41;
                border: none;
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: {ModernTheme.SPACING_MD};
                font-family: 'JetBrains Mono', 'Consolas', monospace;
            }}
        """)
        output_layout.addWidget(self.output)

        output_card.setLayout(output_layout)
        layout.addWidget(output_card)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setText("Weiter")
        ok_button.setEnabled(False)
        ok_button.setStyleSheet(ModernTheme.get_button_style("primary", "large"))
        self.button_box.accepted.connect(self.accept)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def run_check(self):
        """Run dependency check in background"""
        self.output.append("🚀 <span style='color: #00BFFF;'>Starte Dependency Check...</span>\n")

        # Run check (this should be moved to a worker thread in production)
        success = self.dependency_checker.run_startup_check()

        if success:
            self.output.append("\n<span style='color: #00FF41; font-weight: bold;'>✅ Dependency Check erfolgreich abgeschlossen!</span>")
            self.progress.setRange(0, 1)
            self.progress.setValue(1)
        else:
            self.output.append("\n<span style='color: #FF6B6B; font-weight: bold;'>❌ Dependency Check fehlgeschlagen!</span>")

        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(True)

class PasswordDialog(QDialog):
    """Moderner Dialog für Passwort-Eingabe"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Administrator-Berechtigung erforderlich")
        self.setModal(True)
        self.setFixedSize(450, 200)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
                font-family: {ModernTheme.FONT_FAMILY};
            }}
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(int(ModernTheme.SPACING_LG.replace('px', '')))
        layout.setContentsMargins(32, 32, 32, 32)

        # Header
        header_layout = QHBoxLayout()

        icon_label = QLabel("🔐")
        icon_label.setFont(QFont(ModernTheme.FONT_FAMILY, 32))
        icon_label.setStyleSheet(f"color: {ModernTheme.WARNING};")
        header_layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        title = QLabel("Sudo-Passwort erforderlich")
        title.setFont(QFont(ModernTheme.FONT_FAMILY, 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY};")
        text_layout.addWidget(title)

        subtitle = QLabel("Geben Sie Ihr Passwort ein, um fortzufahren:")
        subtitle.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        subtitle.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY};")
        text_layout.addWidget(subtitle)

        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Passwort eingeben...")
        self.password_input.setStyleSheet(ModernTheme.get_input_style())
        self.password_input.returnPressed.connect(self.accept)
        layout.addWidget(self.password_input)

        # Buttons
        button_layout = QHBoxLayout()

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(ModernTheme.get_button_style("ghost"))
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        ok_btn = QPushButton("Bestätigen")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        ok_btn.setStyleSheet(ModernTheme.get_button_style("primary"))
        button_layout.addWidget(ok_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Focus on password input
        self.password_input.setFocus()

    def get_password(self):
        """Get the entered password"""
        return self.password_input.text()

class CommandWorker(QThread):
    """Worker thread für Befehlsausführung"""

    output_ready = pyqtSignal(str, str)  # output_type, text
    finished = pyqtSignal(int, str, str)  # return_code, stdout, stderr

    def __init__(self, command, sudo_password=None):
        super().__init__()
        self.command = command
        self.sudo_password = sudo_password
        self.should_stop = False

    def run(self):
        """Execute command in worker thread"""
        try:
            import subprocess
            import os
            import tempfile

            if 'sudo' in self.command and self.sudo_password:
                # Create temporary script for sudo
                with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                    f.write(f"#!/bin/bash\necho '{self.sudo_password}' | sudo -S {self.command.replace('sudo ', '')}")
                    script_path = f.name

                os.chmod(script_path, 0o755)

                # Execute script
                process = subprocess.Popen(
                    ['bash', script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Read output line by line
                for line in iter(process.stdout.readline, ''):
                    if self.should_stop:
                        process.terminate()
                        break
                    if line:
                        clean_line = line.rstrip()
                        if clean_line and self.sudo_password not in clean_line:
                            self.output_ready.emit('stdout', clean_line)

                # Read stderr
                for line in iter(process.stderr.readline, ''):
                    if self.should_stop:
                        break
                    if line:
                        clean_line = line.rstrip()
                        if clean_line and self.sudo_password not in clean_line:
                            self.output_ready.emit('stderr', clean_line)

                return_code = process.wait()

                # Clean up
                try:
                    os.unlink(script_path)
                except:
                    pass

            else:
                # Regular command
                process = subprocess.Popen(
                    self.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                stdout, stderr = process.communicate()
                return_code = process.returncode

                # Emit line by line
                if stdout:
                    for line in stdout.split('\n'):
                        if line.strip():
                            self.output_ready.emit('stdout', line)

                if stderr:
                    for line in stderr.split('\n'):
                        if line.strip():
                            self.output_ready.emit('stderr', line)

            self.finished.emit(return_code, '', '')

        except Exception as e:
            self.output_ready.emit('stderr', f"Fehler: {str(e)}")
            self.finished.emit(-1, '', str(e))

    def stop(self):
        """Stop the worker thread"""
        self.should_stop = True

class CommandExecutionDialog(QDialog):
    """Moderner Dialog für Befehlsausführung"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Befehl wird ausgeführt")
        self.setModal(True)
        self.resize(800, 600)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
                font-family: {ModernTheme.FONT_FAMILY};
            }}
        """)

        self.sudo_password = None
        self.worker = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(int(ModernTheme.SPACING_LG.replace('px', '')))
        layout.setContentsMargins(32, 32, 32, 32)

        # Header Card
        header_card = QWidget()
        header_card.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                padding: {ModernTheme.SPACING_LG};
            }}
        """)

        header_layout = QVBoxLayout()

        # Command info
        self.command_label = QLabel()
        self.command_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        self.command_label.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        self.command_label.setWordWrap(True)
        header_layout.addWidget(self.command_label)

        # Progress info
        progress_layout = QHBoxLayout()

        self.progress_label = QLabel("Bereit...")
        self.progress_label.setFont(QFont(ModernTheme.FONT_FAMILY, 11))
        self.progress_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        progress_layout.addWidget(self.progress_label)

        progress_layout.addStretch()

        # Progress indicator
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate during execution
        self.progress.setFixedHeight(6)
        self.progress.setFixedWidth(200)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: {ModernTheme.BORDER};
            }}
            QProgressBar::chunk {{
                border-radius: 3px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ModernTheme.PRIMARY}, stop:1 {ModernTheme.PRIMARY_DARK});
            }}
        """)
        progress_layout.addWidget(self.progress)

        header_layout.addLayout(progress_layout)
        header_card.setLayout(header_layout)
        layout.addWidget(header_card)

        # Output Card
        output_card = QWidget()
        output_card.setStyleSheet(ModernTheme.get_card_style())

        output_layout = QVBoxLayout()
        output_layout.setContentsMargins(0, 0, 0, 0)

        # Output header
        output_header_widget = QWidget()
        output_header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE_DARK};
                border: none;
                border-radius: {ModernTheme.RADIUS_MEDIUM} {ModernTheme.RADIUS_MEDIUM} 0 0;
                padding: {ModernTheme.SPACING_MD};
            }}
        """)

        output_header_layout = QHBoxLayout()
        output_header_layout.setContentsMargins(0, 0, 0, 0)

        output_title = QLabel("💻 Terminal-Ausgabe")
        output_title.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        output_title.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        output_header_layout.addWidget(output_title)

        output_header_layout.addStretch()

        # Terminal indicators
        indicators_layout = QHBoxLayout()
        indicators_layout.setSpacing(6)

        for color in ["#FF5F57", "#FFBD2E", "#28CA42"]:
            indicator = QLabel("●")
            indicator.setStyleSheet(f"color: {color}; font-size: 14px; background: transparent;")
            indicators_layout.addWidget(indicator)

        output_header_layout.addLayout(indicators_layout)
        output_header_widget.setLayout(output_header_layout)
        output_layout.addWidget(output_header_widget)

        # Terminal output
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("JetBrains Mono, Consolas, monospace", 10))
        self.output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1E1E1E;
                color: #D4D4D4;
                border: none;
                border-radius: 0 0 {ModernTheme.RADIUS_MEDIUM} {ModernTheme.RADIUS_MEDIUM};
                padding: {ModernTheme.SPACING_MD};
                font-family: 'JetBrains Mono', 'Consolas', monospace;
                selection-background-color: {ModernTheme.PRIMARY};
            }}
        """)
        output_layout.addWidget(self.output)

        output_card.setLayout(output_layout)
        layout.addWidget(output_card)

        # Action Buttons
        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("🛑 Abbrechen")
        self.cancel_button.clicked.connect(self.cancel_command)
        self.cancel_button.setStyleSheet(ModernTheme.get_button_style("outline"))
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        self.close_button = QPushButton("✅ Schließen")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setEnabled(False)
        self.close_button.setStyleSheet(ModernTheme.get_button_style("success"))
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def execute_command(self, command: str, description: str = ""):
        """Execute a command with GUI sudo password"""
        self.current_command = command  # Store for history

        if description:
            self.command_label.setText(f"📋 {description}\n💻 {command}")
        else:
            self.command_label.setText(f"💻 {command}")

        self.output.clear()
        self.cancel_button.setEnabled(True)
        self.close_button.setEnabled(False)

        # Check if command needs sudo
        if 'sudo' in command:
            if not self.sudo_password:
                # Ask for password
                password_dialog = PasswordDialog(self)
                if password_dialog.exec() == QDialog.DialogCode.Accepted:
                    self.sudo_password = password_dialog.get_password()
                else:
                    self.output.append("<span style='color: #FF6B6B;'>❌ Abgebrochen - Sudo-Passwort erforderlich</span>")
                    self.close_button.setEnabled(True)
                    self.cancel_button.setEnabled(False)
                    return

        # Start worker thread
        self.progress_label.setText("🚀 Führe Befehl aus...")
        self.worker = CommandWorker(command, self.sudo_password)
        self.worker.output_ready.connect(self.on_output_received)
        self.worker.finished.connect(self.on_command_finished)
        self.worker.start()

    def on_output_received(self, output_type: str, text: str):
        """Handle real-time output from worker"""
        if output_type == 'stdout':
            self.output.append(f"<span style='color: #4FC1E9;'>{text}</span>")
        else:  # stderr
            self.output.append(f"<span style='color: #FF6B6B;'>{text}</span>")

        # Scroll to bottom
        scrollbar = self.output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_command_finished(self, return_code: int, stdout: str, stderr: str):
        """Handle command completion"""
        self.progress.setRange(0, 1)
        self.progress.setValue(1)

        if return_code == 0:
            self.progress_label.setText("✅ Erfolgreich abgeschlossen")
            self.output.append(f"\n<span style='color: #4CAF50; font-weight: bold; font-size: 14px;'>✅ Befehl erfolgreich ausgeführt</span>")
            status = "SUCCESS"
        else:
            self.progress_label.setText("❌ Fehlgeschlagen")
            self.output.append(f"\n<span style='color: #FF6B6B; font-weight: bold; font-size: 14px;'>❌ Befehl fehlgeschlagen (Exit Code: {return_code})</span>")
            status = "FAILED"

        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)

        # Add to history (emit signal to parent)
        if hasattr(self.parent(), 'add_command_to_history'):
            from datetime import datetime
            command_data = {
                'time': datetime.now().strftime("%H:%M:%S"),
                'command': getattr(self, 'current_command', 'Unknown'),
                'status': status,
                'return_code': return_code,
                'execution_time': getattr(self.worker, 'execution_time', 0.0)
            }
            self.parent().add_command_to_history(command_data)

        # Clean up worker
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

    def cancel_command(self):
        """Cancel the running command"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.terminate()
            self.worker.wait(1000)  # Wait up to 1 second

        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
        self.output.append("<span style='color: #FF9800; font-weight: bold;'>⚠️ Befehl abgebrochen</span>")
        self.progress_label.setText("⚠️ Abgebrochen")

class CategoryWidget(QWidget):
    """Modernes Widget für Kategorie-Tools mit Multi-Selection"""

    tool_selected = pyqtSignal(object)  # ConfigItem

    def __init__(self, category: ConfigCategory):
        super().__init__()
        self.category = category
        self.selected_tools = {}  # Dict instead of set: {tool_name: ConfigItem}
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(int(ModernTheme.SPACING_LG.replace('px', '')))
        layout.setContentsMargins(0, 0, 0, 0)

        # Beautiful category header with modern gradient
        header_card = QWidget()
        header_card.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {ModernTheme.PRIMARY},
                    stop:0.5 {ModernTheme.PRIMARY_DARK},
                    stop:1 #1565C0);
                border-radius: {ModernTheme.RADIUS_LARGE};
                border: none;
            }}
        """)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(32, 24, 32, 24)
        header_layout.setSpacing(20)

        # Icon
        if self.category.icon:
            icon_label = QLabel(self.category.icon)
            icon_label.setFont(QFont(ModernTheme.FONT_FAMILY, 32))
            icon_label.setStyleSheet("color: white; background: transparent;")
            icon_label.setFixedSize(50, 50)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(icon_label)

        # Title and description
        text_layout = QVBoxLayout()
        text_layout.setSpacing(8)

        title = QLabel(self.category.name)
        title.setFont(QFont(ModernTheme.FONT_FAMILY, 22, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        text_layout.addWidget(title)

        if self.category.description:
            desc = QLabel(self.category.description)
            desc.setFont(QFont(ModernTheme.FONT_FAMILY, 13))
            desc.setStyleSheet("color: rgba(255,255,255,0.9); background: transparent;")
            desc.setWordWrap(True)
            text_layout.addWidget(desc)

        header_layout.addLayout(text_layout, 1)

        # Stats badge
        stats_widget = QWidget()
        stats_widget.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(255,255,255,0.15);
                border: 2px solid rgba(255,255,255,0.25);
                border-radius: 20px;
                padding: {ModernTheme.SPACING_SM} {ModernTheme.SPACING_MD};
            }}
        """)

        stats_layout = QVBoxLayout()
        stats_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.setSpacing(4)

        count_label = QLabel(str(len(self.category.items)))
        count_label.setFont(QFont(ModernTheme.FONT_FAMILY, 18, QFont.Weight.Bold))
        count_label.setStyleSheet("color: white; background: transparent;")
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(count_label)

        tools_label = QLabel("Tools")
        tools_label.setFont(QFont(ModernTheme.FONT_FAMILY, 10, QFont.Weight.Bold))
        tools_label.setStyleSheet("color: rgba(255,255,255,0.8); background: transparent;")
        tools_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(tools_label)

        stats_widget.setLayout(stats_layout)
        header_layout.addWidget(stats_widget)

        header_card.setLayout(header_layout)
        layout.addWidget(header_card)

        # Control Panel
        controls_card = QWidget()
        controls_card.setStyleSheet(ModernTheme.get_card_style(elevated=False))

        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(20, 16, 20, 16)
        controls_layout.setSpacing(12)

        # Selection controls
        self.select_all_btn = QPushButton("🔘 Alle auswählen")
        self.select_all_btn.clicked.connect(self.select_all_tools)
        self.select_all_btn.setStyleSheet(ModernTheme.get_button_style("outline", "small"))
        controls_layout.addWidget(self.select_all_btn)

        self.select_none_btn = QPushButton("⭕ Alle abwählen")
        self.select_none_btn.clicked.connect(self.select_no_tools)
        self.select_none_btn.setStyleSheet(ModernTheme.get_button_style("ghost", "small"))
        controls_layout.addWidget(self.select_none_btn)

        controls_layout.addStretch()

        # Selected count badge
        self.selected_count_label = QLabel("0 ausgewählt")
        self.selected_count_label.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        self.selected_count_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.TEXT_SECONDARY};
                background-color: {ModernTheme.SURFACE_DARK};
                padding: {ModernTheme.SPACING_XS} {ModernTheme.SPACING_SM};
                border-radius: {ModernTheme.RADIUS_SMALL};
                border: 1px solid {ModernTheme.BORDER};
            }}
        """)
        controls_layout.addWidget(self.selected_count_label)

        # Install selected button
        self.install_selected_btn = QPushButton("🚀 Ausgewählte installieren")
        self.install_selected_btn.clicked.connect(self.install_selected_tools)
        self.install_selected_btn.setEnabled(False)
        self.install_selected_btn.setStyleSheet(ModernTheme.get_button_style("success"))
        controls_layout.addWidget(self.install_selected_btn)

        controls_card.setLayout(controls_layout)
        layout.addWidget(controls_card)

        # Tools Container
        tools_container = QWidget()
        tools_container.setStyleSheet(f"background-color: transparent;")

        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(12)
        tools_layout.setContentsMargins(0, 0, 0, 0)

        for item in self.category.items:
            tool_widget = self.create_tool_card(item)
            tools_layout.addWidget(tool_widget)

        tools_container.setLayout(tools_layout)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tools_container)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {ModernTheme.SURFACE_DARK};
                width: 8px;
                border-radius: 4px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ModernTheme.BORDER_DARK};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {ModernTheme.TEXT_SECONDARY};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)

        layout.addWidget(scroll, 1)
        self.setLayout(layout)

    def create_tool_card(self, item: ConfigItem) -> QWidget:
        """Create a modern tool card with beautiful styling"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                padding: 0px;
            }}
            QWidget:hover {{
                border-color: {ModernTheme.PRIMARY_LIGHT};
                background-color: {ModernTheme.SURFACE};
            }}
        """)

        # Dynamic height calculation
        base_height = 100
        desc_lines = max(2, len(item.description) // 60 + 1)
        tag_height = 30 if item.tags else 0
        calculated_height = base_height + (desc_lines * 15) + tag_height
        card.setMinimumHeight(max(calculated_height, 120))

        layout = QHBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(20)

        # Selection checkbox
        checkbox = QCheckBox()
        checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {ModernTheme.PRIMARY};
                border-radius: 4px;
                background-color: {ModernTheme.SURFACE};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ModernTheme.PRIMARY};
                border-color: {ModernTheme.PRIMARY};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEwzLjkgOC4xTDEuNCA1LjYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }}
            QCheckBox::indicator:hover {{
                border-color: {ModernTheme.PRIMARY_DARK};
            }}
        """)
        checkbox.toggled.connect(lambda checked: self.on_tool_selection_changed(item, checked))
        layout.addWidget(checkbox, 0, Qt.AlignmentFlag.AlignTop)

        # Main content area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(10)

        # Title and description
        title_label = QLabel(item.name)
        title_label.setFont(QFont(ModernTheme.FONT_FAMILY, 15, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        title_label.setWordWrap(True)
        content_layout.addWidget(title_label)

        desc_label = QLabel(item.description)
        desc_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        desc_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent; line-height: 1.4;")
        desc_label.setWordWrap(True)
        desc_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(desc_label)

        # Tags
        if item.tags:
            tags_widget = QWidget()
            tags_layout = QHBoxLayout()
            tags_layout.setContentsMargins(0, 0, 0, 0)
            tags_layout.setSpacing(8)

            for i, tag in enumerate(item.tags[:4]):  # Max 4 tags
                tag_label = QLabel(tag)
                tag_label.setFont(QFont(ModernTheme.FONT_FAMILY, 10, QFont.Weight.Bold))
                tag_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {ModernTheme.PRIMARY_LIGHT};
                        color: {ModernTheme.PRIMARY_DARK};
                        padding: 4px 10px;
                        border-radius: 12px;
                        border: 1px solid {ModernTheme.PRIMARY};
                    }}
                """)
                tags_layout.addWidget(tag_label)

            if len(item.tags) > 4:
                more_label = QLabel(f"+{len(item.tags)-4}")
                more_label.setFont(QFont(ModernTheme.FONT_FAMILY, 10))
                more_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {ModernTheme.SURFACE_DARK};
                        color: {ModernTheme.TEXT_SECONDARY};
                        padding: 4px 8px;
                        border-radius: 10px;
                        border: 1px solid {ModernTheme.BORDER};
                    }}
                """)
                tags_layout.addWidget(more_label)

            tags_layout.addStretch()
            tags_widget.setLayout(tags_layout)
            content_layout.addWidget(tags_widget)

        layout.addLayout(content_layout, 1)

        # Right side actions
        actions_layout = QVBoxLayout()
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        actions_layout.setSpacing(8)

        # Requirements warning
        if item.requires:
            req_widget = QWidget()
            req_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {ModernTheme.WARNING};
                    border-radius: 6px;
                    padding: 6px;
                }}
            """)
            req_layout = QHBoxLayout()
            req_layout.setContentsMargins(0, 0, 0, 0)

            req_icon = QLabel("⚠️")
            req_icon.setFont(QFont(ModernTheme.FONT_FAMILY, 14))
            req_icon.setStyleSheet("background: transparent; color: white;")
            req_layout.addWidget(req_icon)

            req_widget.setLayout(req_layout)
            req_widget.setToolTip(f"Requires: {', '.join(item.requires)}")
            req_widget.setFixedSize(32, 32)
            actions_layout.addWidget(req_widget)

        # Install button
        install_btn = QPushButton("Installieren")
        install_btn.setFixedSize(100, 36)
        install_btn.clicked.connect(lambda: self.tool_selected.emit(item))
        install_btn.setStyleSheet(ModernTheme.get_button_style("success", "small"))
        actions_layout.addWidget(install_btn)

        actions_layout.addStretch()
        layout.addLayout(actions_layout)

        # Store references
        card.checkbox = checkbox
        card.config_item = item

        return card

    def on_tool_selection_changed(self, item: ConfigItem, checked: bool):
        """Handle tool selection change"""
        if checked:
            self.selected_tools[item.name] = item
        else:
            self.selected_tools.pop(item.name, None)

        self.update_selection_ui()
        self.update_widget_selection_state(item, checked)

    def update_widget_selection_state(self, item: ConfigItem, selected: bool):
        """Update visual state when tool is selected/deselected"""
        # Find the widget for this item
        tools_scroll = self.layout().itemAt(2).widget()  # ScrollArea
        tools_widget = tools_scroll.widget()

        for i in range(tools_widget.layout().count()):
            layout_item = tools_widget.layout().itemAt(i)
            if layout_item and layout_item.widget():
                widget = layout_item.widget()
                if hasattr(widget, 'config_item') and widget.config_item.name == item.name:
                    if selected:
                        widget.setStyleSheet(f"""
                            QWidget {{
                                background-color: {ModernTheme.SURFACE};
                                border: 2px solid {ModernTheme.PRIMARY};
                                border-radius: {ModernTheme.RADIUS_MEDIUM};
                                padding: 0px;
                            }}
                        """)
                    else:
                        widget.setStyleSheet(f"""
                            QWidget {{
                                background-color: {ModernTheme.SURFACE};
                                border: 1px solid {ModernTheme.BORDER};
                                border-radius: {ModernTheme.RADIUS_MEDIUM};
                                padding: 0px;
                            }}
                            QWidget:hover {{
                                border-color: {ModernTheme.PRIMARY_LIGHT};
                                background-color: {ModernTheme.SURFACE};
                            }}
                        """)
                    break

    def update_selection_ui(self):
        """Update selection-related UI elements"""
        count = len(self.selected_tools)
        self.selected_count_label.setText(f"{count} ausgewählt")
        self.install_selected_btn.setEnabled(count > 0)

        if count > 0:
            self.install_selected_btn.setText(f"🚀 {count} Tool{'s' if count != 1 else ''} installieren")
        else:
            self.install_selected_btn.setText("🚀 Ausgewählte installieren")

    def select_all_tools(self):
        """Select all tools"""
        for i in range(self.layout().itemAt(2).widget().widget().layout().count()):
            item = self.layout().itemAt(2).widget().widget().layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'checkbox'):
                    widget.checkbox.setChecked(True)

    def select_no_tools(self):
        """Deselect all tools"""
        for i in range(self.layout().itemAt(2).widget().widget().layout().count()):
            item = self.layout().itemAt(2).widget().widget().layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'checkbox'):
                    widget.checkbox.setChecked(False)

    def install_selected_tools(self):
        """Install all selected tools"""
        if not self.selected_tools:
            return

        # Create batch command
        selected_items = list(self.selected_tools.values())
        commands = [item.command for item in selected_items]
        batch_command = " && ".join(commands)

        # Emit signal with batch command
        from core.config_manager import ConfigItem
        batch_item = ConfigItem(
            name=f"Batch Installation ({len(selected_items)} tools)",
            description=f"Installing: {', '.join(item.name for item in selected_items)}",
            command=batch_command,
            category=self.category.id,
            tags=["batch", "installation"]
        )

        self.tool_selected.emit(batch_item)

class MainWindow(QMainWindow):
    """Moderne Hauptfenster-Klasse mit einheitlichem Design"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔧 Arch Linux Configuration Tool")
        self.setGeometry(100, 100, 1400, 900)

        # Set modern application styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {ModernTheme.BACKGROUND};
                font-family: {ModernTheme.FONT_FAMILY};
            }}
        """)

        # Backend components
        self.config_manager = ConfigManager()
        self.command_executor = CommandExecutor()

        # UI state
        self.categories: Dict[str, ConfigCategory] = {}
        self.current_category: Optional[str] = None
        self.command_history: List[Dict] = []

        # Run dependency check first
        self.run_dependency_check()

        # Initialize UI
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()

        # Load configuration
        self.load_configuration()

    def run_dependency_check(self):
        """Run dependency check dialog"""
        dialog = DependencyCheckDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            sys.exit(1)

    def setup_ui(self):
        """Initialize modern user interface"""
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {ModernTheme.BACKGROUND};")
        self.setCentralWidget(central_widget)

        # Main layout with modern spacing
        main_layout = QHBoxLayout()
        main_layout.setSpacing(int(ModernTheme.SPACING_LG.replace('px', '')))
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Left sidebar
        sidebar = self.create_modern_sidebar()
        main_layout.addWidget(sidebar, 1)

        # Right content area
        content = self.create_modern_content_area()
        main_layout.addWidget(content, 3)

        central_widget.setLayout(main_layout)

    def create_modern_sidebar(self) -> QWidget:
        """Create modern sidebar with categories"""
        sidebar_card = QWidget()
        sidebar_card.setFixedWidth(320)
        sidebar_card.setStyleSheet(ModernTheme.get_card_style())

        layout = QVBoxLayout()
        layout.setSpacing(int(ModernTheme.SPACING_MD.replace('px', '')))
        layout.setContentsMargins(24, 24, 24, 24)

        # Sidebar header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        title = QLabel("🗂️ Kategorien")
        title.setFont(QFont(ModernTheme.FONT_FAMILY, 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        header_layout.addWidget(title)

        subtitle = QLabel("Wählen Sie eine Kategorie aus")
        subtitle.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        subtitle.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Suche nach Tools...")
        self.search_box.textChanged.connect(self.on_search_changed)
        self.search_box.setStyleSheet(ModernTheme.get_input_style())
        layout.addWidget(self.search_box)

        # Categories list
        self.categories_list = QListWidget()
        self.categories_list.itemClicked.connect(self.on_category_selected)
        self.categories_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                background-color: {ModernTheme.SURFACE};
                padding: {ModernTheme.SPACING_XS};
                font-family: {ModernTheme.FONT_FAMILY};
                outline: none;
            }}
            QListWidget::item {{
                padding: {ModernTheme.SPACING_SM} {ModernTheme.SPACING_MD};
                border-radius: {ModernTheme.RADIUS_SMALL};
                margin: 2px 0px;
                color: {ModernTheme.TEXT_PRIMARY};
                font-size: {ModernTheme.FONT_SIZE_MD};
            }}
            QListWidget::item:hover {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                color: {ModernTheme.PRIMARY_DARK};
            }}
            QListWidget::item:selected {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                font-weight: 600;
            }}
        """)
        layout.addWidget(self.categories_list, 1)

        # Refresh button
        refresh_button = QPushButton("🔄 Konfiguration aktualisieren")
        refresh_button.clicked.connect(self.refresh_configuration)
        refresh_button.setStyleSheet(ModernTheme.get_button_style("outline"))
        layout.addWidget(refresh_button)

        sidebar_card.setLayout(layout)
        return sidebar_card

    def create_modern_content_area(self) -> QWidget:
        """Create modern main content area"""
        content_card = QWidget()
        content_card.setStyleSheet(ModernTheme.get_card_style())

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Tab widget with modern styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: {ModernTheme.SURFACE};
                border-radius: 0 0 {ModernTheme.RADIUS_MEDIUM} {ModernTheme.RADIUS_MEDIUM};
            }}
            QTabBar::tab {{
                background-color: {ModernTheme.SURFACE_DARK};
                color: {ModernTheme.TEXT_SECONDARY};
                padding: {ModernTheme.SPACING_SM} {ModernTheme.SPACING_LG};
                margin-right: 2px;
                border-top-left-radius: {ModernTheme.RADIUS_SMALL};
                border-top-right-radius: {ModernTheme.RADIUS_SMALL};
                font-family: {ModernTheme.FONT_FAMILY};
                font-size: {ModernTheme.FONT_SIZE_MD};
                font-weight: 600;
                min-width: 120px;
            }}
            QTabBar::tab:hover {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QTabBar::tab:selected {{
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.PRIMARY};
                border-bottom: 3px solid {ModernTheme.PRIMARY};
            }}
        """)

        # Tools tab
        self.tools_tab = QScrollArea()
        self.tools_tab.setWidgetResizable(True)
        self.tools_tab.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.tools_tab.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {ModernTheme.BACKGROUND};
            }}
        """)

        self.tools_content = QWidget()
        self.tools_content.setStyleSheet(f"background-color: {ModernTheme.BACKGROUND};")
        self.tools_layout = QVBoxLayout()
        self.tools_layout.setContentsMargins(24, 24, 24, 24)
        self.tools_layout.setSpacing(int(ModernTheme.SPACING_LG.replace('px', '')))
        self.tools_content.setLayout(self.tools_layout)
        self.tools_tab.setWidget(self.tools_content)
        self.tab_widget.addTab(self.tools_tab, "🛠️ Tools")

        # History tab
        self.history_tab = self.create_modern_history_tab()
        self.tab_widget.addTab(self.history_tab, "📋 Verlauf")

        # Stats tab
        self.stats_tab = self.create_modern_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "📊 Statistiken")

        layout.addWidget(self.tab_widget)
        content_card.setLayout(layout)
        return content_card

    def create_modern_history_tab(self) -> QWidget:
        """Create modern command history tab"""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {ModernTheme.BACKGROUND};")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(int(ModernTheme.SPACING_LG.replace('px', '')))

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("📋 Befehlsverlauf")
        title.setFont(QFont(ModernTheme.FONT_FAMILY, 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Clear button
        clear_button = QPushButton("🗑️ Verlauf löschen")
        clear_button.clicked.connect(self.clear_history)
        clear_button.setStyleSheet(ModernTheme.get_button_style("outline"))
        header_layout.addWidget(clear_button)

        layout.addLayout(header_layout)

        # History table card
        table_card = QWidget()
        table_card.setStyleSheet(ModernTheme.get_card_style())

        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)

        # Table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Zeit", "Befehl", "Status", "Exit Code", "Ausführungszeit"
        ])

        # Modern table styling
        self.history_table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                background-color: {ModernTheme.SURFACE};
                gridline-color: {ModernTheme.BORDER};
                font-family: {ModernTheme.FONT_FAMILY};
                font-size: {ModernTheme.FONT_SIZE_MD};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
            }}
            QTableWidget::item {{
                padding: {ModernTheme.SPACING_SM};
                border-bottom: 1px solid {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QTableWidget::item:selected {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                color: {ModernTheme.PRIMARY_DARK};
            }}
            QHeaderView::section {{
                background-color: {ModernTheme.SURFACE_DARK};
                color: {ModernTheme.TEXT_PRIMARY};
                padding: {ModernTheme.SPACING_SM} {ModernTheme.SPACING_MD};
                border: none;
                border-bottom: 2px solid {ModernTheme.PRIMARY};
                font-weight: bold;
                font-size: {ModernTheme.FONT_SIZE_MD};
            }}
        """)

        # Configure table
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        table_layout.addWidget(self.history_table)
        table_card.setLayout(table_layout)
        layout.addWidget(table_card)

        widget.setLayout(layout)
        return widget

    def create_modern_stats_tab(self) -> QWidget:
        """Create modern statistics tab"""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {ModernTheme.BACKGROUND};")

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(int(ModernTheme.SPACING_LG.replace('px', '')))

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("📊 Statistiken & Übersicht")
        title.setFont(QFont(ModernTheme.FONT_FAMILY, 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Refresh button
        refresh_stats_btn = QPushButton("🔄 Aktualisieren")
        refresh_stats_btn.clicked.connect(self.update_stats)
        refresh_stats_btn.setStyleSheet(ModernTheme.get_button_style("primary"))
        header_layout.addWidget(refresh_stats_btn)

        layout.addLayout(header_layout)

        # Stats content card
        stats_card = QWidget()
        stats_card.setStyleSheet(ModernTheme.get_card_style())

        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(32, 32, 32, 32)

        self.stats_content = QLabel()
        self.stats_content.setFont(QFont(ModernTheme.FONT_FAMILY, 13))
        self.stats_content.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stats_content.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.TEXT_PRIMARY};
                background: transparent;
                line-height: 1.6;
            }}
        """)
        self.stats_content.setWordWrap(True)
        stats_layout.addWidget(self.stats_content)

        stats_card.setLayout(stats_layout)
        layout.addWidget(stats_card)

        # Initial stats update
        self.update_stats()

        widget.setLayout(layout)
        return widget

    def setup_menu_bar(self):
        """Setup modern menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.TEXT_PRIMARY};
                border-bottom: 1px solid {ModernTheme.BORDER};
                font-family: {ModernTheme.FONT_FAMILY};
                font-size: {ModernTheme.FONT_SIZE_MD};
                padding: {ModernTheme.SPACING_XS};
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: {ModernTheme.SPACING_SM} {ModernTheme.SPACING_MD};
                border-radius: {ModernTheme.RADIUS_SMALL};
            }}
            QMenuBar::item:selected {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                color: {ModernTheme.PRIMARY_DARK};
            }}
            QMenu {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: {ModernTheme.SPACING_XS};
            }}
            QMenu::item {{
                padding: {ModernTheme.SPACING_SM} {ModernTheme.SPACING_MD};
                border-radius: {ModernTheme.RADIUS_SMALL};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QMenu::item:selected {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
            }}
        """)

        # File menu
        file_menu = menubar.addMenu("📁 Datei")
        file_menu.addAction("🔄 Konfiguration aktualisieren", self.refresh_configuration)
        file_menu.addSeparator()
        file_menu.addAction("❌ Beenden", self.close)

        # Tools menu
        tools_menu = menubar.addMenu("🔧 Tools")
        tools_menu.addAction("🔍 Dependency Check", self.run_dependency_check)
        tools_menu.addAction("🗑️ Verlauf löschen", self.clear_history)

        # Help menu
        help_menu = menubar.addMenu("❓ Hilfe")
        help_menu.addAction("ℹ️ Über", self.show_about)

    def setup_status_bar(self):
        """Setup modern status bar"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {ModernTheme.SURFACE_DARK};
                color: {ModernTheme.TEXT_SECONDARY};
                border-top: 1px solid {ModernTheme.BORDER};
                font-family: {ModernTheme.FONT_FAMILY};
                font-size: {ModernTheme.FONT_SIZE_SM};
                padding: {ModernTheme.SPACING_XS} {ModernTheme.SPACING_MD};
            }}
        """)
        status_bar.showMessage("🚀 Bereit für Konfiguration")

    def load_configuration(self):
        """Load configuration from ConfigManager"""
        self.statusBar().showMessage("⏳ Lade Konfiguration...")

        try:
            self.categories = self.config_manager.get_config()
            self.populate_categories()
            self.statusBar().showMessage(f"✅ Konfiguration geladen: {len(self.categories)} Kategorien")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Konfiguration:\n{e}")
            self.statusBar().showMessage("❌ Fehler beim Laden der Konfiguration")

    def populate_categories(self):
        """Populate the categories list with modern styling"""
        self.categories_list.clear()

        for category in self.config_manager.get_categories():
            item = QListWidgetItem()
            item.setText(f"{category.icon} {category.name}")
            item.setData(Qt.ItemDataRole.UserRole, category.id)

            # Add tool count as tooltip
            item.setToolTip(f"{category.description}\n\n📊 {len(category.items)} Tools verfügbar")

            self.categories_list.addItem(item)

        # Select first category by default
        if self.categories_list.count() > 0:
            self.categories_list.setCurrentRow(0)
            self.on_category_selected(self.categories_list.item(0))

    def on_category_selected(self, item: QListWidgetItem):
        """Handle category selection"""
        category_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_category = category_id

        if category_id in self.categories:
            self.show_category_tools(self.categories[category_id])
            self.statusBar().showMessage(f"📂 Kategorie: {self.categories[category_id].name}")

    def show_category_tools(self, category: ConfigCategory):
        """Show tools for selected category"""
        # Clear current content safely
        while self.tools_layout.count():
            child = self.tools_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Add category widget
        category_widget = CategoryWidget(category)
        category_widget.tool_selected.connect(self.on_tool_selected)
        self.tools_layout.addWidget(category_widget)

        # Add stretch to push content to top
        self.tools_layout.addStretch()

    def on_tool_selected(self, item: ConfigItem):
        """Handle tool selection and execution"""
        # Modern confirmation dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Befehl ausführen")
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {ModernTheme.SURFACE};
                font-family: {ModernTheme.FONT_FAMILY};
            }}
            QMessageBox QLabel {{
                color: {ModernTheme.TEXT_PRIMARY};
                font-size: {ModernTheme.FONT_SIZE_MD};
            }}
        """)

        msg_box.setText(f"🚀 Tool ausführen")
        msg_box.setInformativeText(
            f"📋 <b>{item.name}</b><br><br>"
            f"📝 {item.description}<br><br>"
            f"💻 <code>{item.command}</code><br><br>"
            f"Möchten Sie dieses Tool jetzt ausführen?"
        )

        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        # Style buttons
        yes_btn = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_btn.setText("✅ Ausführen")
        yes_btn.setStyleSheet(ModernTheme.get_button_style("success"))

        no_btn = msg_box.button(QMessageBox.StandardButton.No)
        no_btn.setText("❌ Abbrechen")
        no_btn.setStyleSheet(ModernTheme.get_button_style("ghost"))

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            # Execute command
            dialog = CommandExecutionDialog(self)
            dialog.execute_command(item.command, item.description)
            dialog.exec()

    def on_search_changed(self, text: str):
        """Handle search input with modern results display"""
        if not text.strip():
            self.populate_categories()
            return

        # Search for tools
        results = self.config_manager.search_tools(text)

        # Clear current content safely
        while self.tools_layout.count():
            child = self.tools_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if results:
            # Add search header
            search_header = QWidget()
            search_header.setStyleSheet(f"""
                QWidget {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {ModernTheme.SUCCESS}, stop:1 {ModernTheme.SUCCESS_DARK});
                    border-radius: {ModernTheme.RADIUS_MEDIUM};
                    padding: {ModernTheme.SPACING_MD};
                }}
            """)

            header_layout = QHBoxLayout()

            search_icon = QLabel("🔍")
            search_icon.setFont(QFont(ModernTheme.FONT_FAMILY, 24))
            search_icon.setStyleSheet("color: white; background: transparent;")
            header_layout.addWidget(search_icon)

            search_info = QLabel(f"Suchergebnisse für '{text}' ({len(results)} gefunden)")
            search_info.setFont(QFont(ModernTheme.FONT_FAMILY, 16, QFont.Weight.Bold))
            search_info.setStyleSheet("color: white; background: transparent;")
            header_layout.addWidget(search_info)

            header_layout.addStretch()
            search_header.setLayout(header_layout)
            self.tools_layout.addWidget(search_header)

            # Group results by category
            category_results = {}
            for item in results:
                if item.category not in category_results:
                    category_results[item.category] = []
                category_results[item.category].append(item)

            # Show results
            for category_id, items in category_results.items():
                if category_id in self.categories:
                    category = self.categories[category_id]
                    # Create a filtered category
                    filtered_category = ConfigCategory(
                        id=category.id,
                        name=f"🔍 {category.name}",
                        description=f"Suchergebnisse in {category.name}",
                        order=category.order,
                        icon=category.icon,
                        items=items
                    )

                    category_widget = CategoryWidget(filtered_category)
                    category_widget.tool_selected.connect(self.on_tool_selected)
                    self.tools_layout.addWidget(category_widget)
        else:
            # No results
            no_results_card = QWidget()
            no_results_card.setStyleSheet(f"""
                QWidget {{
                    background-color: {ModernTheme.SURFACE};
                    border: 2px dashed {ModernTheme.BORDER};
                    border-radius: {ModernTheme.RADIUS_LARGE};
                    padding: {ModernTheme.SPACING_XL};
                }}
            """)

            no_results_layout = QVBoxLayout()
            no_results_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon_label = QLabel("🔍")
            icon_label.setFont(QFont(ModernTheme.FONT_FAMILY, 48))
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet(f"color: {ModernTheme.TEXT_DISABLED}; background: transparent;")
            no_results_layout.addWidget(icon_label)

            title_label = QLabel("Keine Ergebnisse gefunden")
            title_label.setFont(QFont(ModernTheme.FONT_FAMILY, 16, QFont.Weight.Bold))
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
            no_results_layout.addWidget(title_label)

            desc_label = QLabel(f"Keine Tools für '{text}' gefunden. Versuchen Sie andere Suchbegriffe.")
            desc_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setStyleSheet(f"color: {ModernTheme.TEXT_DISABLED}; background: transparent;")
            desc_label.setWordWrap(True)
            no_results_layout.addWidget(desc_label)

            no_results_card.setLayout(no_results_layout)
            self.tools_layout.addWidget(no_results_card)

        self.tools_layout.addStretch()

    def refresh_configuration(self):
        """Refresh configuration from GitHub"""
        self.statusBar().showMessage("🔄 Aktualisiere Konfiguration...")

        try:
            self.categories = self.config_manager.get_config(force_update=True)
            self.populate_categories()
            self.statusBar().showMessage("✅ Konfiguration aktualisiert")

            # Modern success message
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Erfolg")
            msg_box.setText("✅ Konfiguration erfolgreich aktualisiert!")
            msg_box.setInformativeText(f"📊 {len(self.categories)} Kategorien geladen")
            msg_box.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {ModernTheme.SURFACE};
                    font-family: {ModernTheme.FONT_FAMILY};
                }}
            """)
            ok_btn = msg_box.addButton(QMessageBox.StandardButton.Ok)
            ok_btn.setStyleSheet(ModernTheme.get_button_style("success"))
            msg_box.exec()

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Aktualisieren:\n{e}")
            self.statusBar().showMessage("❌ Fehler beim Aktualisieren")

    def add_command_to_history(self, command_data: Dict):
        """Add a command to the history"""
        self.command_history.append(command_data)

        # Keep only last 100 commands
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]

        # Update history table
        self.update_history_table()

    def update_history_table(self):
        """Update the command history table with modern styling"""
        self.history_table.setRowCount(len(self.command_history))

        for row, cmd_data in enumerate(reversed(self.command_history)):  # Latest first
            # Time
            time_item = QTableWidgetItem(cmd_data.get('time', 'N/A'))
            time_item.setFont(QFont("JetBrains Mono, Consolas, monospace", 10))
            self.history_table.setItem(row, 0, time_item)

            # Command (truncated)
            command = cmd_data.get('command', '')
            if len(command) > 60:
                command = command[:60] + "..."
            cmd_item = QTableWidgetItem(command)
            cmd_item.setFont(QFont("JetBrains Mono, Consolas, monospace", 10))
            cmd_item.setToolTip(cmd_data.get('command', ''))  # Full command in tooltip
            self.history_table.setItem(row, 1, cmd_item)

            # Status with color
            status = cmd_data.get('status', 'UNKNOWN')
            status_item = QTableWidgetItem(f"{'✅' if status == 'SUCCESS' else '❌'} {status}")
            if status == 'SUCCESS':
                status_item.setForeground(QColor(ModernTheme.SUCCESS))
            elif status == 'FAILED':
                status_item.setForeground(QColor(ModernTheme.ERROR))
            self.history_table.setItem(row, 2, status_item)

            # Exit code
            exit_code = str(cmd_data.get('return_code', 'N/A'))
            code_item = QTableWidgetItem(exit_code)
            code_item.setFont(QFont("JetBrains Mono, Consolas, monospace", 10))
            self.history_table.setItem(row, 3, code_item)

            # Execution time
            exec_time = cmd_data.get('execution_time', 0)
            time_item = QTableWidgetItem(f"{exec_time:.2f}s")
            time_item.setFont(QFont("JetBrains Mono, Consolas, monospace", 10))
            self.history_table.setItem(row, 4, time_item)

    def clear_history(self):
        """Clear command history with modern confirmation"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Verlauf löschen")
        msg_box.setText("🗑️ Verlauf löschen")
        msg_box.setInformativeText("Möchten Sie den gesamten Befehlsverlauf unwiderruflich löschen?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        # Style buttons
        yes_btn = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_btn.setText("✅ Löschen")
        yes_btn.setStyleSheet(ModernTheme.get_button_style("secondary"))

        no_btn = msg_box.button(QMessageBox.StandardButton.No)
        no_btn.setText("❌ Abbrechen")
        no_btn.setStyleSheet(ModernTheme.get_button_style("ghost"))

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            self.command_history.clear()
            self.update_history_table()
            self.statusBar().showMessage("🗑️ Verlauf gelöscht")

    def update_stats(self):
        """Update statistics display with modern formatting"""
        total_commands = len(self.command_history)

        if total_commands == 0:
            self.stats_content.setText(f"""
<div style="text-align: center; padding: 20px;">
<h2 style="color: {ModernTheme.TEXT_PRIMARY}; margin-bottom: 16px;">📊 Befehls-Statistiken</h2>
<p style="color: {ModernTheme.TEXT_SECONDARY}; font-size: 14px;">Noch keine Befehle ausgeführt.</p>
<p style="color: {ModernTheme.TEXT_DISABLED}; font-size: 12px;">Führe einige Tools aus, um Statistiken zu sehen!</p>
</div>

<div style="margin-top: 24px;">
<h3 style="color: {ModernTheme.PRIMARY}; margin-bottom: 12px;">📋 System-Informationen</h3>
<p style="color: {ModernTheme.TEXT_PRIMARY};"><strong>Kategorien geladen:</strong> <span style="color: {ModernTheme.PRIMARY};">{len(self.categories)}</span></p>
<p style="color: {ModernTheme.TEXT_PRIMARY};"><strong>Tools verfügbar:</strong> <span style="color: {ModernTheme.SUCCESS};">{sum(len(cat.items) for cat in self.categories.values())}</span></p>
</div>
            """)
            return

        # Calculate stats
        successful = sum(1 for cmd in self.command_history if cmd.get('status') == 'SUCCESS')
        failed = sum(1 for cmd in self.command_history if cmd.get('status') == 'FAILED')
        success_rate = (successful / total_commands) * 100 if total_commands > 0 else 0

        # Get most used commands
        command_counts = {}
        for cmd in self.command_history:
            cmd_name = cmd.get('command', '')[:40] + ('...' if len(cmd.get('command', '')) > 40 else '')
            command_counts[cmd_name] = command_counts.get(cmd_name, 0) + 1

        most_used = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        # Recent activity
        recent_commands = self.command_history[-5:] if len(self.command_history) >= 5 else self.command_history

        stats_html = f"""
<div style="margin-bottom: 24px;">
<h2 style="color: {ModernTheme.PRIMARY}; margin-bottom: 16px;">📊 Befehls-Statistiken</h2>
<div style="display: flex; gap: 16px; margin-bottom: 16px;">
    <div style="background-color: {ModernTheme.SURFACE_DARK}; padding: 12px; border-radius: 8px; flex: 1;">
        <div style="font-size: 24px; font-weight: bold; color: {ModernTheme.PRIMARY};">{total_commands}</div>
        <div style="color: {ModernTheme.TEXT_SECONDARY}; font-size: 12px;">Gesamt</div>
    </div>
    <div style="background-color: {ModernTheme.SURFACE_DARK}; padding: 12px; border-radius: 8px; flex: 1;">
        <div style="font-size: 24px; font-weight: bold; color: {ModernTheme.SUCCESS};">{successful}</div>
        <div style="color: {ModernTheme.TEXT_SECONDARY}; font-size: 12px;">Erfolgreich</div>
    </div>
    <div style="background-color: {ModernTheme.SURFACE_DARK}; padding: 12px; border-radius: 8px; flex: 1;">
        <div style="font-size: 24px; font-weight: bold; color: {ModernTheme.ERROR};">{failed}</div>
        <div style="color: {ModernTheme.TEXT_SECONDARY}; font-size: 12px;">Fehlgeschlagen</div>
    </div>
    <div style="background-color: {ModernTheme.SURFACE_DARK}; padding: 12px; border-radius: 8px; flex: 1;">
        <div style="font-size: 24px; font-weight: bold; color: {ModernTheme.WARNING};">{success_rate:.1f}%</div>
        <div style="color: {ModernTheme.TEXT_SECONDARY}; font-size: 12px;">Erfolgsrate</div>
    </div>
</div>
</div>

<div style="margin-bottom: 24px;">
<h3 style="color: {ModernTheme.PRIMARY}; margin-bottom: 12px;">🏆 Meist verwendete Befehle</h3>
"""

        for i, (cmd, count) in enumerate(most_used, 1):
            stats_html += f"""
<div style="background-color: {ModernTheme.SURFACE_DARK}; padding: 8px 12px; border-radius: 6px; margin-bottom: 8px;">
    <span style="color: {ModernTheme.PRIMARY}; font-weight: bold;">{i}.</span>
    <code style="color: {ModernTheme.TEXT_PRIMARY}; background-color: {ModernTheme.BACKGROUND}; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{cmd}</code>
    <span style="color: {ModernTheme.TEXT_SECONDARY}; float: right;">({count}x)</span>
</div>
"""

        if not most_used:
            stats_html += f"<p style='color: {ModernTheme.TEXT_DISABLED}; font-style: italic;'>Noch keine Befehle ausgeführt</p>"

        stats_html += f"""
</div>

<div style="margin-bottom: 24px;">
<h3 style="color: {ModernTheme.PRIMARY}; margin-bottom: 12px;">📋 System-Informationen</h3>
<div style="background-color: {ModernTheme.SURFACE_DARK}; padding: 16px; border-radius: 8px;">
    <p style="color: {ModernTheme.TEXT_PRIMARY}; margin: 4px 0;"><strong>Kategorien geladen:</strong> <span style="color: {ModernTheme.PRIMARY};">{len(self.categories)}</span></p>
    <p style="color: {ModernTheme.TEXT_PRIMARY}; margin: 4px 0;"><strong>Tools verfügbar:</strong> <span style="color: {ModernTheme.SUCCESS};">{sum(len(cat.items) for cat in self.categories.values())}</span></p>
</div>
</div>

<div>
<h3 style="color: {ModernTheme.PRIMARY}; margin-bottom: 12px;">🕒 Letzte Aktivität</h3>
"""

        for cmd in reversed(recent_commands):
            status_icon = '✅' if cmd.get('status') == 'SUCCESS' else '❌'
            status_color = ModernTheme.SUCCESS if cmd.get('status') == 'SUCCESS' else ModernTheme.ERROR
            cmd_short = cmd.get('command', '')[:50] + ('...' if len(cmd.get('command', '')) > 50 else '')

            stats_html += f"""
<div style="background-color: {ModernTheme.SURFACE_DARK}; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px;">
    <span style="color: {status_color}; font-size: 14px;">{status_icon}</span>
    <span style="color: {ModernTheme.TEXT_SECONDARY}; font-size: 11px; margin-left: 8px;">{cmd.get('time', 'N/A')}</span>
    <br>
    <code style="color: {ModernTheme.TEXT_PRIMARY}; background-color: {ModernTheme.BACKGROUND}; padding: 2px 6px; border-radius: 3px; font-size: 11px; margin-left: 24px;">{cmd_short}</code>
</div>
"""

        stats_html += "</div>"
        self.stats_content.setText(stats_html)

    def show_about(self):
        """Show modern about dialog"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Über Arch Config Tool")
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {ModernTheme.SURFACE};
                font-family: {ModernTheme.FONT_FAMILY};
            }}
            QMessageBox QLabel {{
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)

        msg_box.setText("🔧 Arch Linux Configuration Tool")
        msg_box.setInformativeText(f"""
<div style="text-align: center;">
<h3 style="color: {ModernTheme.PRIMARY};">Version 2.0</h3>
<p style="color: {ModernTheme.TEXT_SECONDARY};">Ein modernes GUI-Tool für die Systemkonfiguration<br>
und -wartung von Arch-basierten Linux-Distributionen.</p>

<div style="margin: 20px 0; padding: 16px; background-color: {ModernTheme.SURFACE_DARK}; border-radius: 8px;">
<h4 style="color: {ModernTheme.PRIMARY}; margin: 8px 0;">✨ Features</h4>
<ul style="text-align: left; color: {ModernTheme.TEXT_PRIMARY};">
<li>🔍 Intelligenter Dependency-Check</li>
<li>📡 GitHub-basierte Konfiguration</li>
<li>🔒 Sichere Befehlsausführung mit GUI-Sudo</li>
<li>⚡ Real-time Terminal-Output</li>
<li>📊 Detaillierte Statistiken & Verlauf</li>
<li>🎨 Modernes Material Design</li>
<li>🔍 Leistungsstarke Suchfunktion</li>
<li>📦 Batch-Installation von Tools</li>
</ul>
</div>

<p style="color: {ModernTheme.TEXT_DISABLED}; font-size: 11px;">
Entwickelt mit Qt6 & Python<br>
© 2024 - Arch Configuration Tool
</p>
</div>
        """)

        ok_btn = msg_box.addButton(QMessageBox.StandardButton.Ok)
        ok_btn.setText("✨ Großartig!")
        ok_btn.setStyleSheet(ModernTheme.get_button_style("primary"))
        msg_box.exec()

    def closeEvent(self, event):
        """Handle application close event"""
        if self.command_history:
            # Ask if user wants to save history (could be implemented later)
            pass

        # Clean up any running workers
        for widget in self.findChildren(CommandExecutionDialog):
            if hasattr(widget, 'worker') and widget.worker:
                widget.worker.stop()
                widget.worker.terminate()
                widget.worker.wait(1000)

        event.accept()


# Additional helper functions for the main window

def apply_modern_theme_to_app(app):
    """Apply modern theme to the entire application"""
    app.setStyleSheet(f"""
        * {{
            font-family: {ModernTheme.FONT_FAMILY};
        }}

        QToolTip {{
            background-color: {ModernTheme.TEXT_PRIMARY};
            color: white;
            border: none;
            border-radius: {ModernTheme.RADIUS_SMALL};
            padding: {ModernTheme.SPACING_SM};
            font-size: {ModernTheme.FONT_SIZE_SM};
        }}

        QScrollBar:vertical {{
            background-color: {ModernTheme.SURFACE_DARK};
            width: 8px;
            border-radius: 4px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background-color: {ModernTheme.BORDER_DARK};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {ModernTheme.TEXT_SECONDARY};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}

        QScrollBar:horizontal {{
            background-color: {ModernTheme.SURFACE_DARK};
            height: 8px;
            border-radius: 4px;
            border: none;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {ModernTheme.BORDER_DARK};
            border-radius: 4px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {ModernTheme.TEXT_SECONDARY};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
        }}
    """)


# Example usage and main function
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont

    # Enable high DPI scaling
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Arch Linux Configuration Tool")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Arch Config Tools")

    # Apply modern theme
    apply_modern_theme_to_app(app)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Center window on screen
    screen = app.primaryScreen().geometry()
    window_rect = window.geometry()
    x = (screen.width() - window_rect.width()) // 2
    y = (screen.height() - window_rect.height()) // 2
    window.move(x, y)

    sys.exit(app.exec())
