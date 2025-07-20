"""
Tool card components - Simplified
Basic tool display and interaction widgets
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QMessageBox, QTextEdit, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class ToolCard(QWidget):
    """Simple tool card widget"""

    tool_selected = pyqtSignal(object)
    selection_changed = pyqtSignal(object, bool)

    def __init__(self, tool):
        super().__init__()
        self.tool = tool
        self.is_selected = False
        self.setup_ui()

    def setup_ui(self):
        """Setup tool card UI"""
        self.setFixedHeight(120)
        self.setProperty("class", "tool-card")

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Header with checkbox and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Selection checkbox
        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.on_selection_changed)
        header_layout.addWidget(self.checkbox)

        # Tool name
        self.title_label = QLabel(self.tool.name)
        self.title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.title_label.setWordWrap(True)
        header_layout.addWidget(self.title_label, 1)

        # Info button
        info_btn = QPushButton("ℹ️")
        info_btn.setFixedSize(24, 24)
        info_btn.setProperty("class", "secondary")
        info_btn.clicked.connect(self.show_tool_info)
        header_layout.addWidget(info_btn)

        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(self.tool.description)
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(35)
        layout.addWidget(desc_label)

        # Footer with tags and execute button
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(6)

        # Tags (show max 2)
        if hasattr(self.tool, 'tags') and self.tool.tags:
            for i, tag in enumerate(self.tool.tags[:2]):
                tag_label = QLabel(f"#{tag}")
                tag_label.setProperty("class", "tag")
                footer_layout.addWidget(tag_label)

            if len(self.tool.tags) > 2:
                more_label = QLabel(f"+{len(self.tool.tags) - 2}")
                footer_layout.addWidget(more_label)

        footer_layout.addStretch()

        # Execute button
        exec_btn = QPushButton("Execute")
        exec_btn.setProperty("class", "success")
        exec_btn.setFixedSize(70, 28)
        exec_btn.clicked.connect(lambda: self.tool_selected.emit(self.tool))
        footer_layout.addWidget(exec_btn)

        layout.addLayout(footer_layout)
        self.setLayout(layout)

    def on_selection_changed(self, state):
        """Handle selection state change"""
        self.is_selected = state == Qt.CheckState.Checked.value

        if self.is_selected:
            self.setProperty("class", "tool-card-selected")
        else:
            self.setProperty("class", "tool-card")

        # Refresh styling
        self.style().unpolish(self)
        self.style().polish(self)

        self.selection_changed.emit(self.tool, self.is_selected)

    def set_selected(self, selected):
        """Programmatically set selection state"""
        self.checkbox.setChecked(selected)

    def show_tool_info(self):
        """Show tool information dialog"""
        dialog = ToolInfoDialog(self.tool, self)
        dialog.exec()

class ToolInfoDialog(QDialog):
    """Simple tool information dialog"""

    def __init__(self, tool, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle(f"Tool Information")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(f"🔧 {self.tool.name}")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Description
        desc_label = QLabel("Description:")
        desc_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(desc_label)

        desc_text = QLabel(self.tool.description)
        desc_text.setWordWrap(True)
        layout.addWidget(desc_text)

        # Command
        cmd_label = QLabel("Command:")
        cmd_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(cmd_label)

        cmd_text = QTextEdit()
        cmd_text.setPlainText(self.tool.command)
        cmd_text.setReadOnly(True)
        cmd_text.setMaximumHeight(80)
        cmd_text.setFont(QFont("Consolas", 10))
        cmd_text.setProperty("class", "command-display")
        layout.addWidget(cmd_text)

        # Tags (if available)
        if hasattr(self.tool, 'tags') and self.tool.tags:
            tags_label = QLabel("Tags:")
            tags_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            layout.addWidget(tags_label)

            tags_layout = QHBoxLayout()
            for tag in self.tool.tags:
                tag_widget = QLabel(f"#{tag}")
                tag_widget.setProperty("class", "tag")
                tags_layout.addWidget(tag_widget)

            tags_layout.addStretch()
            layout.addLayout(tags_layout)

        # Requirements (if available)
        if hasattr(self.tool, 'requires') and self.tool.requires:
            req_label = QLabel("Requirements:")
            req_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            layout.addWidget(req_label)

            req_text = QLabel(", ".join(self.tool.requires))
            req_text.setProperty("class", "warning")
            layout.addWidget(req_text)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Execute button
        execute_btn = QPushButton("Execute Tool")
        execute_btn.setProperty("class", "success")
        execute_btn.clicked.connect(self.execute_tool)
        button_layout.addWidget(execute_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setProperty("class", "secondary")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def execute_tool(self):
        """Execute the tool"""
        reply = QMessageBox.question(
            self,
            "Execute Tool",
            f"Execute '{self.tool.name}'?\n\nCommand: {self.tool.command}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Emit signal to parent or execute directly
            self.accept()
            QMessageBox.information(self, "Execution", f"Tool '{self.tool.name}' would be executed.")

class SimpleToolCard(QWidget):
    """Even simpler tool card for minimal displays"""

    tool_selected = pyqtSignal(object)

    def __init__(self, tool):
        super().__init__()
        self.tool = tool
        self.setup_ui()

    def setup_ui(self):
        """Setup minimal tool card"""
        self.setFixedHeight(60)
        self.setProperty("class", "tool-card")

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)

        # Tool name
        name_label = QLabel(self.tool.name)
        name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(name_label, 1)

        # Command type indicator
        cmd_type = self.get_command_type()
        type_label = QLabel(cmd_type)
        type_label.setProperty("class", "tag")
        layout.addWidget(type_label)

        # Execute button
        exec_btn = QPushButton("▶")
        exec_btn.setProperty("class", "success")
        exec_btn.setFixedSize(30, 30)
        exec_btn.clicked.connect(lambda: self.tool_selected.emit(self.tool))
        layout.addWidget(exec_btn)

        self.setLayout(layout)

    def get_command_type(self):
        """Get simple command type"""
        command = self.tool.command.lower()

        if 'pacman' in command:
            return 'PAC'
        elif 'flatpak' in command:
            return 'FLAT'
        elif 'yay' in command or 'paru' in command:
            return 'AUR'
        elif 'sudo' in command:
            return 'SUDO'
        else:
            return 'CMD'

class ToolListWidget(QWidget):
    """Simple list widget for tools"""

    tool_selected = pyqtSignal(object)

    def __init__(self, tools):
        super().__init__()
        self.tools = tools
        self.setup_ui()

    def setup_ui(self):
        """Setup tool list"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        for tool in self.tools:
            tool_card = SimpleToolCard(tool)
            tool_card.tool_selected.connect(self.tool_selected.emit)
            layout.addWidget(tool_card)

        layout.addStretch()
        self.setLayout(layout)

# Export classes
__all__ = ['ToolCard', 'ToolInfoDialog', 'SimpleToolCard', 'ToolListWidget']
