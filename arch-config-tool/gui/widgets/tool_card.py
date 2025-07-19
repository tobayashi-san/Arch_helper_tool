"""
Tool card components
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QFrame, QMessageBox, QDialog, QTextEdit, QGroupBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from ..styles.modern_theme import ModernTheme


class ToolCard(QWidget):
    """Individual tool card widget"""

    tool_selected = pyqtSignal(object)
    selection_changed = pyqtSignal(object, bool)

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.is_selected = False
        self.hover_animation = None
        self.setup_ui()

    def setup_ui(self):
        """Setup tool card UI"""
        self.setFixedHeight(140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Initial styling
        self.update_card_style()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 14, 16, 14)
        main_layout.setSpacing(10)

        # Header section
        header_section = self.create_header_section()
        main_layout.addLayout(header_section)

        # Description section
        description_section = self.create_description_section()
        main_layout.addWidget(description_section)

        # Footer section (tags/metadata)
        footer_section = self.create_footer_section()
        main_layout.addLayout(footer_section)

        self.setLayout(main_layout)

    def create_header_section(self):
        """Create header with checkbox, title and info button"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Selection checkbox
        self.selection_checkbox = QCheckBox()
        self.selection_checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {ModernTheme.BORDER};
                border-radius: 6px;
                background-color: {ModernTheme.SURFACE};
            }}
            QCheckBox::indicator:hover {{
                border-color: {ModernTheme.PRIMARY};
                background-color: {ModernTheme.PRIMARY_LIGHT};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ModernTheme.PRIMARY};
                border-color: {ModernTheme.PRIMARY};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTQiIGhlaWdodD0iMTEiIHZpZXdCb3g9IjAgMCAxNCAxMSIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEuNSA1LjVMNS41IDkuNUwxMi41IDEuNSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
                border-color: {ModernTheme.PRIMARY_DARK};
            }}
        """)
        self.selection_checkbox.stateChanged.connect(self.on_selection_changed)
        header_layout.addWidget(self.selection_checkbox)

        # Tool title
        self.title_label = QLabel(self.item.name)
        self.title_label.setFont(QFont(ModernTheme.FONT_FAMILY, 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.TEXT_PRIMARY};
                background: transparent;
                padding: 0px;
            }}
        """)
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(40)
        header_layout.addWidget(self.title_label, 1)

        # Info button
        self.info_button = QPushButton("ℹ️")
        self.info_button.setFixedSize(28, 28)
        self.info_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 14px;
                color: {ModernTheme.TEXT_SECONDARY};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_LIGHT};
                border-color: {ModernTheme.PRIMARY};
                color: {ModernTheme.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
            }}
        """)
        self.info_button.clicked.connect(self.show_tool_info)
        header_layout.addWidget(self.info_button)

        return header_layout

    def create_description_section(self):
        """Create description area"""
        self.description_label = QLabel(self.item.description)
        self.description_label.setFont(QFont(ModernTheme.FONT_FAMILY, 11))
        self.description_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernTheme.TEXT_SECONDARY};
                background: transparent;
                padding: 0px;
                line-height: 1.4;
            }}
        """)
        self.description_label.setWordWrap(True)
        self.description_label.setMaximumHeight(44)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignTop)

        return self.description_label

    def create_footer_section(self):
        """Create footer with tags and metadata"""
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(6)

        # Tags section
        if hasattr(self.item, 'tags') and self.item.tags:
            tags_added = 0
            for tag in self.item.tags:
                if tags_added >= 3:  # Limit to 3 tags
                    break

                tag_label = QLabel(f"#{tag}")
                tag_label.setFont(QFont(ModernTheme.FONT_FAMILY, 9, QFont.Weight.Bold))
                tag_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {ModernTheme.PRIMARY_LIGHT};
                        color: {ModernTheme.PRIMARY_DARK};
                        padding: 3px 8px;
                        border-radius: 10px;
                        font-weight: 600;
                        border: none;
                    }}
                """)
                footer_layout.addWidget(tag_label)
                tags_added += 1

            if len(self.item.tags) > 3:
                more_label = QLabel(f"+{len(self.item.tags) - 3}")
                more_label.setFont(QFont(ModernTheme.FONT_FAMILY, 9))
                more_label.setStyleSheet(f"""
                    QLabel {{
                        color: {ModernTheme.TEXT_DISABLED};
                        background: transparent;
                        font-style: italic;
                        padding: 3px 4px;
                    }}
                """)
                footer_layout.addWidget(more_label)

        footer_layout.addStretch()

        # Command type indicator
        command_type = self.get_command_type()
        if command_type:
            type_label = QLabel(command_type)
            type_label.setFont(QFont(ModernTheme.FONT_FAMILY, 8, QFont.Weight.Bold))
            type_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {ModernTheme.SURFACE_DARK};
                    color: {ModernTheme.TEXT_SECONDARY};
                    padding: 2px 6px;
                    border-radius: 8px;
                    border: 1px solid {ModernTheme.BORDER};
                }}
            """)
            footer_layout.addWidget(type_label)

        return footer_layout

    def get_command_type(self):
        """Determine command type from the command string"""
        command = self.item.command.lower()

        if 'pacman' in command:
            return 'PACMAN'
        elif 'flatpak' in command:
            return 'FLATPAK'
        elif 'yay' in command or 'paru' in command:
            return 'AUR'
        elif 'systemctl' in command:
            return 'SYSTEMD'
        elif 'sudo' in command:
            return 'ADMIN'
        else:
            return 'SHELL'

    def update_card_style(self):
        """Update card visual style based on state"""
        if self.is_selected:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {ModernTheme.PRIMARY_LIGHT};
                    border: 2px solid {ModernTheme.PRIMARY};
                    border-radius: {ModernTheme.RADIUS_MEDIUM};
                    margin: 3px;
                }}
                QWidget:hover {{
                    background-color: {ModernTheme.PRIMARY_LIGHT};
                    border-color: {ModernTheme.PRIMARY_DARK};
                    transform: translateY(-1px);
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {ModernTheme.SURFACE};
                    border: 2px solid {ModernTheme.BORDER};
                    border-radius: {ModernTheme.RADIUS_MEDIUM};
                    margin: 3px;
                }}
                QWidget:hover {{
                    background-color: {ModernTheme.SURFACE_LIGHT};
                    border-color: {ModernTheme.PRIMARY_LIGHT};
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
            """)

    def on_selection_changed(self, state):
        """Handle selection state change"""
        self.is_selected = state == Qt.CheckState.Checked.value
        self.update_card_style()
        self.selection_changed.emit(self.item, self.is_selected)

    def set_selected(self, selected):
        """Programmatically set selection state"""
        self.selection_checkbox.setChecked(selected)

    def show_tool_info(self):
        """Show detailed tool information dialog"""
        dialog = ToolInfoDialog(self.item, self)
        dialog.exec()

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to show info"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.show_tool_info()
        super().mouseDoubleClickEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter for hover effects"""
        super().enterEvent(event)
        # Add subtle animation or effects here if needed

    def leaveEvent(self, event):
        """Handle mouse leave"""
        super().leaveEvent(event)
        # Reset hover effects here if needed


class DebugToolCard(QWidget):
    """Simplified tool card for debugging"""

    tool_selected = pyqtSignal(object)
    selection_changed = pyqtSignal(object, bool)

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.is_selected = False
        self.setup_ui()

    def setup_ui(self):
        """Setup debug tool card UI"""
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE_DARK};
                border: 1px dashed {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                margin: 2px;
            }}
            QWidget:hover {{
                border-color: {ModernTheme.PRIMARY};
                background-color: {ModernTheme.SURFACE};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Header with checkbox and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Simple checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 3px;
                background-color: {ModernTheme.SURFACE};
            }}
            QCheckBox::indicator:checked {{
                background-color: {ModernTheme.PRIMARY};
                border-color: {ModernTheme.PRIMARY};
            }}
        """)
        self.checkbox.stateChanged.connect(self.on_selection_changed)
        header_layout.addWidget(self.checkbox)

        # Title
        title_label = QLabel(self.item.name)
        title_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        header_layout.addWidget(title_label, 1)

        # Debug info button
        debug_btn = QPushButton("🔍")
        debug_btn.setFixedSize(20, 20)
        debug_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.BORDER};
                border: none;
                border-radius: 10px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
            }}
        """)
        debug_btn.clicked.connect(self.show_debug_info)
        header_layout.addWidget(debug_btn)

        layout.addLayout(header_layout)

        # Simplified description
        desc_label = QLabel(self.item.description[:80] + "..." if len(self.item.description) > 80 else self.item.description)
        desc_label.setFont(QFont(ModernTheme.FONT_FAMILY, 10))
        desc_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Debug information
        debug_info_layout = QHBoxLayout()
        debug_info_layout.setSpacing(8)

        # Item ID
        id_label = QLabel(f"ID: {id(self.item)}")
        id_label.setFont(QFont(ModernTheme.FONT_FAMILY, 8))
        id_label.setStyleSheet(f"color: {ModernTheme.TEXT_DISABLED}; background: transparent;")
        debug_info_layout.addWidget(id_label)

        debug_info_layout.addStretch()

        # Command preview
        cmd_preview = self.item.command[:20] + "..." if len(self.item.command) > 20 else self.item.command
        cmd_label = QLabel(f"CMD: {cmd_preview}")
        cmd_label.setFont(QFont("Consolas", 8))
        cmd_label.setStyleSheet(f"color: {ModernTheme.TEXT_DISABLED}; background: transparent;")
        debug_info_layout.addWidget(cmd_label)

        layout.addLayout(debug_info_layout)
        self.setLayout(layout)

    def on_selection_changed(self, state):
        """Handle selection change"""
        self.is_selected = state == Qt.CheckState.Checked.value
        self.update_appearance()
        self.selection_changed.emit(self.item, self.is_selected)

    def update_appearance(self):
        """Update visual appearance"""
        if self.is_selected:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {ModernTheme.PRIMARY_LIGHT};
                    border: 2px solid {ModernTheme.PRIMARY};
                    border-radius: {ModernTheme.RADIUS_SMALL};
                    margin: 2px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {ModernTheme.SURFACE_DARK};
                    border: 1px dashed {ModernTheme.BORDER};
                    border-radius: {ModernTheme.RADIUS_SMALL};
                    margin: 2px;
                }}
                QWidget:hover {{
                    border-color: {ModernTheme.PRIMARY};
                    background-color: {ModernTheme.SURFACE};
                }}
            """)

    def set_selected(self, selected):
        """Set selection state"""
        self.checkbox.setChecked(selected)

    def show_debug_info(self):
        """Show debug information"""
        debug_msg = f"""
🔍 Debug Information

📝 Tool: {self.item.name}
🆔 Object ID: {id(self.item)}
📋 Description: {self.item.description}
💻 Command: {self.item.command}
🏷️ Tags: {getattr(self.item, 'tags', 'None')}
📊 Selected: {self.is_selected}
🎯 Type: {type(self.item).__name__}
        """

        QMessageBox.information(self, "Debug Info", debug_msg.strip())


class ToolInfoDialog(QDialog):
    """Detailed tool information dialog"""

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle(f"Tool Information - {self.item.name}")
        self.setFixedSize(600, 500)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernTheme.BACKGROUND};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)

        title_label = QLabel(f"🔧 {self.item.name}")
        title_label.setFont(QFont(ModernTheme.FONT_FAMILY, 20, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {ModernTheme.PRIMARY}; background: transparent;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Command type badge
        cmd_type = self.get_command_type()
        type_badge = QLabel(cmd_type)
        type_badge.setFont(QFont(ModernTheme.FONT_FAMILY, 10, QFont.Weight.Bold))
        type_badge.setStyleSheet(f"""
            QLabel {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                padding: 6px 12px;
                border-radius: 12px;
                font-weight: 600;
            }}
        """)
        header_layout.addWidget(type_badge)

        layout.addLayout(header_layout)

        # Description section
        desc_group = QGroupBox("📝 Beschreibung")
        desc_group.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        desc_group.setStyleSheet(f"""
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

        desc_layout = QVBoxLayout()
        desc_text = QLabel(self.item.description)
        desc_text.setFont(QFont(ModernTheme.FONT_FAMILY, 11))
        desc_text.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; border: none; padding: 12px; background: transparent;")
        desc_text.setWordWrap(True)
        desc_layout.addWidget(desc_text)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)

        # Command section
        cmd_group = QGroupBox("💻 Befehl")
        cmd_group.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
        cmd_group.setStyleSheet(f"""
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

        cmd_layout = QVBoxLayout()
        cmd_text = QTextEdit()
        cmd_text.setPlainText(self.item.command)
        cmd_text.setReadOnly(True)
        cmd_text.setMaximumHeight(100)
        cmd_text.setFont(QFont("Consolas", 10))
        cmd_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.SURFACE_DARK};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                padding: 12px;
                color: {ModernTheme.TEXT_PRIMARY};
                selection-background-color: {ModernTheme.PRIMARY_LIGHT};
            }}
        """)
        cmd_layout.addWidget(cmd_text)
        cmd_group.setLayout(cmd_layout)
        layout.addWidget(cmd_group)

        # Tags section (if available)
        if hasattr(self.item, 'tags') and self.item.tags:
            tags_group = QGroupBox("🏷️ Tags")
            tags_group.setFont(QFont(ModernTheme.FONT_FAMILY, 12, QFont.Weight.Bold))
            tags_group.setStyleSheet(f"""
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

            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(8)
            tags_layout.setContentsMargins(12, 12, 12, 12)

            for tag in self.item.tags:
                tag_label = QLabel(f"#{tag}")
                tag_label.setFont(QFont(ModernTheme.FONT_FAMILY, 10, QFont.Weight.Bold))
                tag_label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {ModernTheme.PRIMARY_LIGHT};
                        color: {ModernTheme.PRIMARY_DARK};
                        padding: 6px 12px;
                        border-radius: 15px;
                        font-weight: 600;
                        border: 1px solid {ModernTheme.PRIMARY};
                    }}
                """)
                tags_layout.addWidget(tag_label)

            tags_layout.addStretch()
            tags_group.setLayout(tags_layout)
            layout.addWidget(tags_group)

        # Button section
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Execute button
        execute_btn = QPushButton("🚀 Ausführen")
        execute_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        execute_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: {ModernTheme.PRIMARY_DARK};
                transform: translateY(1px);
            }}
        """)
        execute_btn.clicked.connect(self.execute_tool)
        button_layout.addWidget(execute_btn)

        # Close button
        close_btn = QPushButton("❌ Schließen")
        close_btn.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ModernTheme.TEXT_SECONDARY};
                border: 2px solid {ModernTheme.BORDER};
                padding: 10px 20px;
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
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_command_type(self):
        """Get command type for badge"""
        command = self.item.command.lower()

        if 'pacman' in command:
            return 'PACMAN'
        elif 'flatpak' in command:
            return 'FLATPAK'
        elif 'yay' in command or 'paru' in command:
            return 'AUR'
        elif 'systemctl' in command:
            return 'SYSTEMD'
        elif 'sudo' in command:
            return 'ADMIN'
        else:
            return 'SHELL'

    def execute_tool(self):
        """Handle tool execution"""
        reply = QMessageBox.question(
            self,
            "Tool ausführen",
            f"Möchten Sie '{self.item.name}' wirklich ausführen?\n\nBefehl: {self.item.command}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Here you would typically emit a signal or call the execution logic
            QMessageBox.information(self, "Ausführung", f"Tool '{self.item.name}' wird ausgeführt...")
            self.close()


# Export all classes
__all__ = ['ToolCard', 'DebugToolCard', 'ToolInfoDialog']
