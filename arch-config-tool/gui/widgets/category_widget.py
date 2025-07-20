"""
Category widget - With multi-selection and control buttons
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QScrollArea, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class ToolCard(QWidget):
    """Tool card with checkbox for selection"""

    tool_selected = pyqtSignal(object)
    selection_changed = pyqtSignal(object, bool)

    def __init__(self, tool):
        super().__init__()
        self.tool = tool
        self.is_selected = False
        self.setup_ui()

    def setup_ui(self):
        """Setup tool card UI with checkbox"""
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
        title_label = QLabel(self.tool.name)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setWordWrap(True)
        header_layout.addWidget(title_label, 1)

        # Individual execute button
        exec_btn = QPushButton("▶")
        exec_btn.setProperty("class", "success")
        exec_btn.setFixedSize(30, 30)
        exec_btn.setToolTip("Execute this tool individually")
        exec_btn.clicked.connect(lambda: self.tool_selected.emit(self.tool))
        header_layout.addWidget(exec_btn)

        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(self.tool.description)
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(35)
        desc_label.setProperty("class", "tool-description")
        layout.addWidget(desc_label)

        # Command preview
        cmd_preview = self.tool.command
        if len(cmd_preview) > 80:
            cmd_preview = cmd_preview[:77] + "..."

        cmd_label = QLabel(f"💻 {cmd_preview}")
        cmd_label.setFont(QFont("Consolas", 9))
        cmd_label.setProperty("class", "command-display")
        layout.addWidget(cmd_label)

        # Tags (if available)
        if hasattr(self.tool, 'tags') and self.tool.tags:
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(4)

            for tag in self.tool.tags[:3]:  # Show max 3 tags
                tag_label = QLabel(f"#{tag}")
                tag_label.setStyleSheet("""
                    QLabel {
                        background-color: #e3f2fd;
                        color: #1976d2;
                        padding: 2px 6px;
                        border-radius: 8px;
                        font-size: 9px;
                        font-weight: bold;
                    }
                """)
                tags_layout.addWidget(tag_label)

            if len(self.tool.tags) > 3:
                more_label = QLabel(f"+{len(self.tool.tags) - 3}")
                more_label.setStyleSheet("font-size: 9px; color: #666;")
                tags_layout.addWidget(more_label)

            tags_layout.addStretch()
            layout.addLayout(tags_layout)

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

class CategoryWidget(QWidget):
    """Category widget with multi-selection controls"""

    tool_selected = pyqtSignal(object)
    tools_selected = pyqtSignal(list)

    def __init__(self, category):
        super().__init__()
        self.category = category
        self.selected_tools = {}
        self.tool_cards = []
        self.setup_ui()

    def setup_ui(self):
        """Setup category widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Control panel
        controls = self.create_control_panel()
        layout.addWidget(controls)

        # Tools area
        tools_area = self.create_tools_area()
        layout.addWidget(tools_area, 1)

        self.setLayout(layout)

    def create_header(self):
        """Create category header"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 16px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Title
        title = QLabel(f"{self.category.icon} {self.category.name}")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2196F3; background: transparent;")
        layout.addWidget(title)

        # Description
        if self.category.description:
            desc = QLabel(self.category.description)
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #666; background: transparent;")
            layout.addWidget(desc)

        # Stats
        stats = QLabel(f"📦 {len(self.category.items)} tools available")
        stats.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        stats.setStyleSheet("color: #28a745; background: transparent;")
        layout.addWidget(stats)

        header.setLayout(layout)
        return header

    def create_control_panel(self):
        """Create control panel with selection buttons"""
        controls = QFrame()
        controls.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 12px;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Selection controls
        select_all_btn = QPushButton("✅ Select All")
        select_all_btn.setProperty("class", "secondary")
        select_all_btn.clicked.connect(self.select_all_tools)
        layout.addWidget(select_all_btn)

        select_none_btn = QPushButton("❌ Select None")
        select_none_btn.setProperty("class", "secondary")
        select_none_btn.clicked.connect(self.select_no_tools)
        layout.addWidget(select_none_btn)

        layout.addStretch()

        # Selected count
        self.selected_count_label = QLabel("0 selected")
        self.selected_count_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.selected_count_label.setStyleSheet("color: #666;")
        layout.addWidget(self.selected_count_label)

        # Execute selected button
        self.execute_selected_btn = QPushButton("🚀 Execute Selected")
        self.execute_selected_btn.setProperty("class", "success")
        self.execute_selected_btn.setEnabled(False)
        self.execute_selected_btn.clicked.connect(self.execute_selected_tools)
        layout.addWidget(self.execute_selected_btn)

        controls.setLayout(layout)
        return controls

    def create_tools_area(self):
        """Create scrollable tools area"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #fafafa;
            }
        """)

        # Tools container
        tools_container = QWidget()
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(8)
        tools_layout.setContentsMargins(12, 12, 12, 12)

        # Add tool cards
        for tool in self.category.items:
            tool_card = ToolCard(tool)
            tool_card.selection_changed.connect(self.on_tool_selection_changed)
            tool_card.tool_selected.connect(self.tool_selected.emit)

            self.tool_cards.append(tool_card)
            tools_layout.addWidget(tool_card)

        tools_layout.addStretch()
        tools_container.setLayout(tools_layout)
        scroll_area.setWidget(tools_container)

        return scroll_area

    def on_tool_selection_changed(self, tool, selected):
        """Handle tool selection change"""
        if selected:
            self.selected_tools[tool.name] = tool
        else:
            self.selected_tools.pop(tool.name, None)

        self.update_selection_ui()

    def update_selection_ui(self):
        """Update selection-related UI elements"""
        count = len(self.selected_tools)
        self.selected_count_label.setText(f"{count} selected")
        self.execute_selected_btn.setEnabled(count > 0)

        if count > 0:
            self.execute_selected_btn.setText(f"🚀 Execute {count} Tools")
            self.selected_count_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        else:
            self.execute_selected_btn.setText("🚀 Execute Selected")
            self.selected_count_label.setStyleSheet("color: #666;")

    def select_all_tools(self):
        """Select all tools"""
        # Find all checkboxes and check them
        tools_container = self.findChild(QScrollArea).widget()
        for i in range(tools_container.layout().count()):
            item = tools_container.layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'checkbox') and hasattr(widget, 'tool'):
                    widget.checkbox.setChecked(True)

    def select_no_tools(self):
        """Deselect all tools"""
        # Find all checkboxes and uncheck them
        tools_container = self.findChild(QScrollArea).widget()
        for i in range(tools_container.layout().count()):
            item = tools_container.layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'checkbox') and hasattr(widget, 'tool'):
                    widget.checkbox.setChecked(False)

    def execute_selected_tools(self):
        """Execute selected tools with confirmation"""
        if not self.selected_tools:
            return

        selected_list = list(self.selected_tools.values())

        # Show confirmation dialog
        msg = QMessageBox(self)
        msg.setWindowTitle("Execute Multiple Tools")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(f"🚀 Execute {len(selected_list)} selected tools?")

        # Build detailed info text
        tools_text = "\n".join([f"• {tool.name}" for tool in selected_list[:8]])
        if len(selected_list) > 8:
            tools_text += f"\n... and {len(selected_list) - 8} more tools"

        msg.setInformativeText(f"The following tools will be executed:\n\n{tools_text}")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg.setDefaultButton(QMessageBox.StandardButton.No)

        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.tools_selected.emit(selected_list)

    def get_selected_tools(self):
        """Get list of selected tools"""
        return list(self.selected_tools.values())

    def clear_selection(self):
        """Clear all selections"""
        self.select_no_tools()

# Export
__all__ = ['CategoryWidget', 'ToolCard']
