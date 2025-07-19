"""
Category widget with tool management
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QFrame, QCheckBox, QMessageBox, QProgressBar, QTextEdit, QDialog,
    QDialogButtonBox, QGroupBox, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from ..styles.modern_theme import ModernTheme


class ToolCard(QWidget):
    """Individual tool card widget"""

    tool_selected = pyqtSignal(object)
    selection_changed = pyqtSignal(object, bool)

    def __init__(self, tool, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.is_selected = False
        self.setup_ui()

    def setup_ui(self):
        """Setup tool card UI"""
        self.setFixedHeight(120)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 2px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                margin: 4px;
            }}
            QWidget:hover {{
                border-color: {ModernTheme.PRIMARY_LIGHT};
                background-color: {ModernTheme.SURFACE_LIGHT};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Header with checkbox and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet(f"""
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
        self.checkbox.stateChanged.connect(self.on_selection_changed)
        header_layout.addWidget(self.checkbox)

        # Tool name
        name_label = QLabel(self.tool.name)
        name_label.setFont(QFont(ModernTheme.FONT_FAMILY, 14, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        name_label.setWordWrap(True)
        header_layout.addWidget(name_label, 1)

        # Info button
        info_btn = QPushButton("ℹ️")
        info_btn.setFixedSize(24, 24)
        info_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 12px;
                color: {ModernTheme.TEXT_SECONDARY};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                border-color: {ModernTheme.PRIMARY};
                color: {ModernTheme.PRIMARY_DARK};
            }}
        """)
        info_btn.clicked.connect(self.show_tool_info)
        header_layout.addWidget(info_btn)

        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(self.tool.description)
        desc_label.setFont(QFont(ModernTheme.FONT_FAMILY, 11))
        desc_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(40)
        layout.addWidget(desc_label)

        # Tags
        if hasattr(self.tool, 'tags') and self.tool.tags:
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(4)

            for tag in self.tool.tags[:3]:  # Show max 3 tags
                tag_label = QLabel(f"#{tag}")
                tag_label.setFont(QFont(ModernTheme.FONT_FAMILY, 9))
                tag_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {ModernTheme.PRIMARY_LIGHT};
                        color: {ModernTheme.PRIMARY_DARK};
                        padding: 2px 6px;
                        border-radius: 8px;
                        font-weight: 600;
                    }}
                """)
                tags_layout.addWidget(tag_label)

            tags_layout.addStretch()
            layout.addLayout(tags_layout)

        self.setLayout(layout)

    def on_selection_changed(self, state):
        """Handle selection change"""
        self.is_selected = state == Qt.CheckState.Checked.value
        self.update_appearance()
        self.selection_changed.emit(self.tool, self.is_selected)

    def update_appearance(self):
        """Update visual appearance based on selection"""
        if self.is_selected:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {ModernTheme.PRIMARY_LIGHT};
                    border: 2px solid {ModernTheme.PRIMARY};
                    border-radius: {ModernTheme.RADIUS_MEDIUM};
                    margin: 4px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {ModernTheme.SURFACE};
                    border: 2px solid {ModernTheme.BORDER};
                    border-radius: {ModernTheme.RADIUS_MEDIUM};
                    margin: 4px;
                }}
                QWidget:hover {{
                    border-color: {ModernTheme.PRIMARY_LIGHT};
                    background-color: {ModernTheme.SURFACE_LIGHT};
                }}
            """)

    def set_selected(self, selected):
        """Programmatically set selection state"""
        self.checkbox.setChecked(selected)

    def show_tool_info(self):
        """Show detailed tool information"""
        dialog = ToolInfoDialog(self.tool, self)
        dialog.exec()


class ToolInfoDialog(QDialog):
    """Dialog showing detailed tool information"""

    def __init__(self, tool, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle(f"Tool Information - {self.tool.name}")
        self.setFixedSize(500, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QLabel(f"🔧 {self.tool.name}")
        header.setFont(QFont(ModernTheme.FONT_FAMILY, 18, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {ModernTheme.PRIMARY};")
        layout.addWidget(header)

        # Description
        desc_group = QGroupBox("📝 Beschreibung")
        desc_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                margin-top: 8px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }}
        """)
        desc_layout = QVBoxLayout()
        desc_label = QLabel(self.tool.description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"border: none; padding: 8px;")
        desc_layout.addWidget(desc_label)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)

        # Command
        cmd_group = QGroupBox("💻 Befehl")
        cmd_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                margin-top: 8px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }}
        """)
        cmd_layout = QVBoxLayout()
        cmd_text = QTextEdit()
        cmd_text.setPlainText(self.tool.command)
        cmd_text.setReadOnly(True)
        cmd_text.setMaximumHeight(80)
        cmd_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.SURFACE_DARK};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }}
        """)
        cmd_layout.addWidget(cmd_text)
        cmd_group.setLayout(cmd_layout)
        layout.addWidget(cmd_group)

        # Tags
        if hasattr(self.tool, 'tags') and self.tool.tags:
            tags_group = QGroupBox("🏷️ Tags")
            tags_group.setStyleSheet(f"""
                QGroupBox {{
                    font-weight: bold;
                    border: 2px solid {ModernTheme.BORDER};
                    border-radius: {ModernTheme.RADIUS_SMALL};
                    margin-top: 8px;
                    padding-top: 8px;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 8px;
                    padding: 0 4px 0 4px;
                }}
            """)
            tags_layout = QHBoxLayout()
            for tag in self.tool.tags:
                tag_label = QLabel(f"#{tag}")
                tag_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {ModernTheme.PRIMARY_LIGHT};
                        color: {ModernTheme.PRIMARY_DARK};
                        padding: 4px 8px;
                        border-radius: 12px;
                        font-weight: 600;
                        border: none;
                    }}
                """)
                tags_layout.addWidget(tag_label)
            tags_layout.addStretch()
            tags_group.setLayout(tags_layout)
            layout.addWidget(tags_group)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
        """)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)


class DebugToolCard(ToolCard):
    """Debug version of ToolCard with additional info"""

    def setup_ui(self):
        """Setup debug tool card UI"""
        super().setup_ui()

        # Add debug info
        debug_label = QLabel(f"Debug: {id(self.tool)}")
        debug_label.setFont(QFont(ModernTheme.FONT_FAMILY, 8))
        debug_label.setStyleSheet(f"color: {ModernTheme.TEXT_DISABLED}; background: transparent;")
        self.layout().addWidget(debug_label)


class CategoryWidget(QWidget):
    """Modernes Widget für Kategorie-Tools mit Multi-Selection"""

    tool_selected = pyqtSignal(object)  # ConfigItem
    tools_selected = pyqtSignal(list)   # List of ConfigItems

    def __init__(self, category, parent=None):
        super().__init__(parent)
        self.category = category
        self.selected_tools = {}
        self.tool_cards = []
        self.setup_ui()

    def setup_ui(self):
        """Setup category widget UI"""
        self.setStyleSheet(f"background-color: {ModernTheme.BACKGROUND};")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(20)

        # Header
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)

        # Controls
        controls_widget = self.create_controls()
        main_layout.addWidget(controls_widget)

        # Tools section
        tools_widget = self.create_tools_section()
        main_layout.addWidget(tools_widget, 1)

        self.setLayout(main_layout)

    def create_header(self):
        """Create category header"""
        header_widget = QWidget()
        header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_LARGE};
                padding: {ModernTheme.SPACING_LG};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Title with icon
        title_layout = QHBoxLayout()
        title_layout.setSpacing(16)

        title_label = QLabel(f"{self.category.icon} {self.category.name}")
        title_label.setFont(QFont(ModernTheme.FONT_FAMILY, 24, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Stats
        stats_label = QLabel(f"📦 {len(self.category.items)} Tools")
        stats_label.setFont(QFont(ModernTheme.FONT_FAMILY, 14, QFont.Weight.Bold))
        stats_label.setStyleSheet(f"""
            QLabel {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                color: {ModernTheme.PRIMARY_DARK};
                padding: 6px 12px;
                border-radius: 16px;
                font-weight: 600;
            }}
        """)
        title_layout.addWidget(stats_label)

        layout.addLayout(title_layout)

        # Description
        if self.category.description:
            desc_label = QLabel(self.category.description)
            desc_label.setFont(QFont(ModernTheme.FONT_FAMILY, 13))
            desc_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        header_widget.setLayout(layout)
        return header_widget

    def create_controls(self):
        """Create control panel"""
        controls_widget = QWidget()
        controls_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                padding: {ModernTheme.SPACING_MD};
            }}
        """)

        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Selection controls
        select_all_btn = QPushButton("✅ Alle auswählen")
        select_all_btn.clicked.connect(self.select_all_tools)
        select_all_btn.setStyleSheet(self.get_button_style())
        layout.addWidget(select_all_btn)

        select_none_btn = QPushButton("❌ Auswahl aufheben")
        select_none_btn.clicked.connect(self.select_no_tools)
        select_none_btn.setStyleSheet(self.get_button_style())
        layout.addWidget(select_none_btn)

        layout.addStretch()

        # Selected count
        self.selected_count_label = QLabel("0 ausgewählt")
        self.selected_count_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        self.selected_count_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        layout.addWidget(self.selected_count_label)

        # Execute button
        self.execute_btn = QPushButton("🚀 Ausgewählte ausführen")
        self.execute_btn.clicked.connect(self.execute_selected_tools)
        self.execute_btn.setEnabled(False)
        self.execute_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton:hover:enabled {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_DISABLED};
            }}
        """)
        layout.addWidget(self.execute_btn)

        controls_widget.setLayout(layout)
        return controls_widget

    def create_tools_section(self):
        """Create tools section"""
        tools_widget = QWidget()
        tools_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Tools header
        tools_header = QLabel("🛠️ Verfügbare Tools")
        tools_header.setFont(QFont(ModernTheme.FONT_FAMILY, 16, QFont.Weight.Bold))
        tools_header.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(tools_header)

        # Scroll area for tools
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {ModernTheme.SURFACE_DARK};
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ModernTheme.BORDER_DARK};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {ModernTheme.TEXT_SECONDARY};
            }}
        """)

        # Tools container
        tools_container = QWidget()
        tools_container.setStyleSheet("background-color: transparent;")

        # Grid layout for tools
        tools_layout = QGridLayout()
        tools_layout.setSpacing(12)
        tools_layout.setContentsMargins(8, 8, 8, 8)

        # Add tool cards
        cols = 2  # 2 columns
        for i, tool in enumerate(self.category.items):
            row = i // cols
            col = i % cols

            tool_card = ToolCard(tool)
            tool_card.selection_changed.connect(self.on_tool_selection_changed)
            tool_card.tool_selected.connect(self.tool_selected.emit)

            self.tool_cards.append(tool_card)
            tools_layout.addWidget(tool_card, row, col)

        # Add stretch to fill remaining space
        tools_layout.setRowStretch(tools_layout.rowCount(), 1)
        tools_layout.setColumnStretch(cols, 1)

        tools_container.setLayout(tools_layout)
        scroll_area.setWidget(tools_container)

        layout.addWidget(scroll_area, 1)
        tools_widget.setLayout(layout)
        return tools_widget

    def get_button_style(self):
        """Get standard button style"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {ModernTheme.PRIMARY};
                border: 2px solid {ModernTheme.PRIMARY};
                padding: 6px 12px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
            }}
        """

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
        self.selected_count_label.setText(f"{count} ausgewählt")
        self.execute_btn.setEnabled(count > 0)

        if count > 0:
            self.selected_count_label.setStyleSheet(f"color: {ModernTheme.PRIMARY}; background: transparent; font-weight: bold;")
        else:
            self.selected_count_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")

    def select_all_tools(self):
        """Select all tools"""
        for card in self.tool_cards:
            card.set_selected(True)

    def select_no_tools(self):
        """Deselect all tools"""
        for card in self.tool_cards:
            card.set_selected(False)

    def execute_selected_tools(self):
        """Execute selected tools"""
        if not self.selected_tools:
            return

        selected_list = list(self.selected_tools.values())

        # Show confirmation dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Tools ausführen")
        msg_box.setText(f"🚀 {len(selected_list)} Tools ausführen")
        msg_box.setInformativeText(
            f"Möchten Sie die folgenden {len(selected_list)} Tools ausführen?\n\n" +
            "\n".join([f"• {tool.name}" for tool in selected_list[:5]]) +
            (f"\n... und {len(selected_list) - 5} weitere" if len(selected_list) > 5 else "")
        )
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        # Style the message box
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {ModernTheme.BACKGROUND};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
        """)

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            self.tools_selected.emit(selected_list)

    def get_selected_tools(self):
        """Get list of selected tools"""
        return list(self.selected_tools.values())

    def clear_selection(self):
        """Clear all selections"""
        self.select_no_tools()


# Export classes
__all__ = ['CategoryWidget', 'ToolCard', 'DebugToolCard', 'ToolInfoDialog']
