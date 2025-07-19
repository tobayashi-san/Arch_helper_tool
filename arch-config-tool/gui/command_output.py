"""
Command Output Widget
Displays real-time command output with advanced features
"""

from PyQt6.QtWidgets import (
    QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QProgressBar, QCheckBox, QComboBox, QSplitter
)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPalette

class CommandOutputWidget(QWidget):
    """Advanced widget for displaying command output"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.auto_scroll = True
        self.max_lines = 1000
        self.line_count = 0

    def setup_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()

        # Control bar
        control_layout = QHBoxLayout()

        # Auto-scroll checkbox
        self.auto_scroll_cb = QCheckBox("Auto-scroll")
        self.auto_scroll_cb.setChecked(True)
        self.auto_scroll_cb.toggled.connect(self.on_auto_scroll_toggled)
        control_layout.addWidget(self.auto_scroll_cb)

        # Line limit
        control_layout.addWidget(QLabel("Max lines:"))
        self.line_limit_combo = QComboBox()
        self.line_limit_combo.addItems(["100", "500", "1000", "5000", "Unlimited"])
        self.line_limit_combo.setCurrentText("1000")
        self.line_limit_combo.currentTextChanged.connect(self.on_line_limit_changed)
        control_layout.addWidget(self.line_limit_combo)

        control_layout.addStretch()

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_output)
        control_layout.addWidget(self.clear_button)

        # Save button
        self.save_button = QPushButton("Save Log")
        self.save_button.clicked.connect(self.save_output)
        control_layout.addWidget(self.save_button)

        layout.addLayout(control_layout)

        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.setup_output_styling()
        layout.addWidget(self.output)

        # Status bar
        status_layout = QHBoxLayout()

        self.line_count_label = QLabel("Lines: 0")
        status_layout.addWidget(self.line_count_label)

        status_layout.addStretch()

        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)

        layout.addLayout(status_layout)

        self.setLayout(layout)

    def setup_output_styling(self):
        """Setup the output text area styling"""
        # Terminal-like appearance
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Monaco", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)

        self.output.setFont(font)

        # Dark theme
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
        """)

    def append_output(self, text: str, output_type: str = "stdout"):
        """Append text to output with color coding"""
        if not text.strip():
            return

        # Color coding based on output type
        if output_type == "stderr":
            color = "#ff6b6b"  # Red for errors
        elif output_type == "stdout":
            color = "#51cf66"  # Green for normal output
        elif output_type == "info":
            color = "#74c0fc"  # Blue for info
        elif output_type == "warning":
            color = "#ffd43b"  # Yellow for warnings
        else:
            color = "#ffffff"  # White for default

        # Format text with color
        formatted_text = f'<span style="color: {color};">{self.escape_html(text)}</span>'

        # Append to output
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(formatted_text + "<br>")

        # Update line count
        self.line_count += 1
        self.line_count_label.setText(f"Lines: {self.line_count}")

        # Enforce line limit
        self.enforce_line_limit()

        # Auto-scroll if enabled
        if self.auto_scroll:
            self.scroll_to_bottom()

    def escape_html(self, text: str) -> str:
        """Escape HTML characters in text"""
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&#x27;"))

    def enforce_line_limit(self):
        """Enforce maximum line limit"""
        if self.max_lines <= 0:  # Unlimited
            return

        if self.line_count > self.max_lines:
            # Remove lines from the beginning
            cursor = self.output.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)

            # Select and delete excess lines
            lines_to_remove = self.line_count - self.max_lines
            for _ in range(lines_to_remove):
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                cursor.movePosition(QTextCursor.MoveOperation.Down)

            cursor.removeSelectedText()
            self.line_count = self.max_lines

    def scroll_to_bottom(self):
        """Scroll to bottom of output"""
        scrollbar = self.output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_output(self):
        """Clear all output"""
        self.output.clear()
        self.line_count = 0
        self.line_count_label.setText("Lines: 0")
        self.status_label.setText("Output cleared")

    def save_output(self):
        """Save output to file"""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Command Output",
            f"command_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    # Get plain text (without HTML formatting)
                    plain_text = self.output.toPlainText()
                    f.write(plain_text)

                self.status_label.setText(f"Saved to {filename}")

                # Clear status after 3 seconds
                QTimer.singleShot(3000, lambda: self.status_label.setText("Ready"))

            except Exception as e:
                self.status_label.setText(f"Save failed: {e}")

    def on_auto_scroll_toggled(self, checked: bool):
        """Handle auto-scroll toggle"""
        self.auto_scroll = checked
        if checked:
            self.scroll_to_bottom()

    def on_line_limit_changed(self, text: str):
        """Handle line limit change"""
        if text == "Unlimited":
            self.max_lines = 0
        else:
            self.max_lines = int(text)

        # Enforce new limit immediately
        self.enforce_line_limit()

    def append_command_start(self, command: str):
        """Append command start message"""
        self.append_output(f"\n{'='*60}", "info")
        self.append_output(f"Executing: {command}", "info")
        self.append_output(f"{'='*60}", "info")
        self.status_label.setText("Command running...")

    def append_command_end(self, command: str, success: bool, execution_time: float):
        """Append command completion message"""
        status = "SUCCESS" if success else "FAILED"
        output_type = "stdout" if success else "stderr"

        self.append_output(f"\n{'='*60}", "info")
        self.append_output(f"Command {status} (took {execution_time:.2f}s)", output_type)
        self.append_output(f"{'='*60}", "info")

        self.status_label.setText(f"Command {status.lower()}")

    def append_separator(self):
        """Append a visual separator"""
        self.append_output(f"\n{'-'*80}\n", "info")


# Test widget for standalone testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Command Output Widget Test")
            self.setGeometry(100, 100, 800, 600)

            central_widget = QWidget()
            layout = QVBoxLayout()

            # Add command output widget
            self.output_widget = CommandOutputWidget()
            layout.addWidget(self.output_widget)

            # Add test buttons
            button_layout = QHBoxLayout()

            test_stdout = QPushButton("Test STDOUT")
            test_stdout.clicked.connect(lambda: self.output_widget.append_output("This is normal output", "stdout"))
            button_layout.addWidget(test_stdout)

            test_stderr = QPushButton("Test STDERR")
            test_stderr.clicked.connect(lambda: self.output_widget.append_output("This is an error message", "stderr"))
            button_layout.addWidget(test_stderr)

            test_info = QPushButton("Test INFO")
            test_info.clicked.connect(lambda: self.output_widget.append_output("This is info message", "info"))
            button_layout.addWidget(test_info)

            test_command = QPushButton("Test Command")
            test_command.clicked.connect(self.test_command_simulation)
            button_layout.addWidget(test_command)

            layout.addLayout(button_layout)

            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)

        def test_command_simulation(self):
            """Simulate a command execution"""
            self.output_widget.append_command_start("sudo pacman -Syu")
            self.output_widget.append_output("Synchronizing package databases...", "stdout")
            self.output_widget.append_output("core is up to date", "stdout")
            self.output_widget.append_output("extra is up to date", "stdout")
            self.output_widget.append_output("Some warning message", "warning")
            self.output_widget.append_command_end("sudo pacman -Syu", True, 15.3)

    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
