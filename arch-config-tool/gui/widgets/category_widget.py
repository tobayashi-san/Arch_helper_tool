"""
Überarbeitete Category Widget - Einheitliches Design mit erweiterte Smart Select
"""

import os
import shutil
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QCheckBox, QScrollArea, QFrame, QMessageBox, QGridLayout,
    QButtonGroup, QToolTip, QSizePolicy, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QCursor

class ToolCard(QWidget):
    """Moderne Tool-Karte mit verbessertem Design"""

    tool_selected = pyqtSignal(object)
    selection_changed = pyqtSignal(object, bool)

    def __init__(self, tool):
        super().__init__()
        self.tool = tool
        self.is_selected = False
        self.is_hovered = False
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        """Setup tool card UI mit modernem Design"""
        self.setFixedHeight(140)
        self.setMinimumWidth(300)
        self.setObjectName("toolCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Header mit Checkbox und Tool-Name
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Selection checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setObjectName("toolCheckbox")
        self.checkbox.stateChanged.connect(self.on_selection_changed)
        header_layout.addWidget(self.checkbox)

        # Tool name
        self.title_label = QLabel(self.tool.name)
        self.title_label.setObjectName("toolTitle")
        self.title_label.setWordWrap(True)
        header_layout.addWidget(self.title_label, 1)

        # Execute button
        self.exec_btn = QPushButton("▶")
        self.exec_btn.setObjectName("executeButton")
        self.exec_btn.setFixedSize(32, 32)
        self.exec_btn.setToolTip("Execute this tool")
        self.exec_btn.clicked.connect(lambda: self.tool_selected.emit(self.tool))
        header_layout.addWidget(self.exec_btn)

        layout.addLayout(header_layout)

        # Description
        self.desc_label = QLabel(self.tool.description)
        self.desc_label.setObjectName("toolDescription")
        self.desc_label.setWordWrap(True)
        self.desc_label.setMaximumHeight(40)
        layout.addWidget(self.desc_label)

        # Command preview
        cmd_preview = self.tool.command
        if len(cmd_preview) > 70:
            cmd_preview = cmd_preview[:67] + "..."

        self.cmd_label = QLabel(f"💻 {cmd_preview}")
        self.cmd_label.setObjectName("commandPreview")
        layout.addWidget(self.cmd_label)

        # Tags und Kategorieinfo
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(6)

        # Tags (maximal 3 anzeigen)
        if hasattr(self.tool, 'tags') and self.tool.tags:
            tags_to_show = self.tool.tags[:3]
            for tag in tags_to_show:
                tag_label = QLabel(f"#{tag}")
                tag_label.setObjectName("toolTag")
                footer_layout.addWidget(tag_label)

            if len(self.tool.tags) > 3:
                more_label = QLabel(f"+{len(self.tool.tags) - 3}")
                more_label.setObjectName("moreTagsLabel")
                footer_layout.addWidget(more_label)

        footer_layout.addStretch()

        # Category indicator
        if hasattr(self.tool, 'category'):
            category_label = QLabel(f"📂 {self.tool.category}")
            category_label.setObjectName("categoryLabel")
            footer_layout.addWidget(category_label)

        layout.addLayout(footer_layout)
        self.setLayout(layout)

        # Styling
        self.apply_card_styling()

    def setup_animations(self):
        """Setup hover animations"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def apply_card_styling(self):
        """Apply modern card styling"""
        self.setStyleSheet("""
            QWidget#toolCard {
                background-color: white;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                margin: 4px;
            }

            QWidget#toolCard:hover {
                border-color: #4f46e5;
                background-color: #fafbff;
            }

            QLabel#toolTitle {
                font-size: 14px;
                font-weight: bold;
                color: #1f2937;
                margin: 0px;
            }

            QLabel#toolDescription {
                font-size: 12px;
                color: #6b7280;
                line-height: 1.4;
            }

            QLabel#commandPreview {
                font-size: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                color: #9ca3af;
                background-color: #f3f4f6;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid #e5e7eb;
            }

            QLabel#toolTag {
                background-color: #ddd6fe;
                color: #5b21b6;
                padding: 2px 6px;
                border-radius: 8px;
                font-size: 9px;
                font-weight: bold;
                border: 1px solid #c4b5fd;
            }

            QLabel#moreTagsLabel {
                font-size: 9px;
                color: #9ca3af;
                font-weight: bold;
            }

            QLabel#categoryLabel {
                font-size: 9px;
                color: #6b7280;
                font-weight: 600;
            }

            QCheckBox#toolCheckbox {
                spacing: 4px;
            }

            QCheckBox#toolCheckbox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
            }

            QCheckBox#toolCheckbox::indicator:hover {
                border-color: #4f46e5;
                background-color: #f0f9ff;
            }

            QCheckBox#toolCheckbox::indicator:checked {
                background-color: #4f46e5;
                border-color: #4f46e5;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }

            QPushButton#executeButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton#executeButton:hover {
                background-color: #059669;
            }

            QPushButton#executeButton:pressed {
                background-color: #047857;
            }
        """)

    def on_selection_changed(self, state):
        """Handle selection state change mit Animation"""
        self.is_selected = state == Qt.CheckState.Checked.value

        if self.is_selected:
            self.setStyleSheet(self.styleSheet() + """
                QWidget#toolCard {
                    border-color: #4f46e5 !important;
                    background-color: #eef2ff !important;
                    border-width: 3px !important;
                }
            """)
        else:
            self.apply_card_styling()

        self.selection_changed.emit(self.tool, self.is_selected)

    def set_selected(self, selected):
        """Programmatically set selection state"""
        self.checkbox.setChecked(selected)

    def enterEvent(self, event):
        """Mouse enter event"""
        self.is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Mouse leave event"""
        self.is_hovered = False
        super().leaveEvent(event)

class CategoryWidget(QWidget):
    """Moderne Category Widget mit erweiterte Smart Selection"""

    tool_selected = pyqtSignal(object)
    tools_selected = pyqtSignal(list)

    def __init__(self, category):
        super().__init__()
        self.category = category
        self.selected_tools = {}
        self.tool_cards = []
        self.view_mode = "grid"  # grid or list
        self.setup_ui()

    def setup_ui(self):
        """Setup category widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Header
        header = self.create_category_header()
        layout.addWidget(header)

        # Control panel
        controls = self.create_enhanced_control_panel()
        layout.addWidget(controls)

        # Tools area
        tools_area = self.create_tools_area()
        layout.addWidget(tools_area, 1)

        self.setLayout(layout)

    def create_category_header(self):
        """Create elegant category header"""
        header = QFrame()
        header.setObjectName("categoryHeader")
        header.setStyleSheet("""
            QFrame#categoryHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 16px;
                padding: 24px;
                margin: 0px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Title row
        title_layout = QHBoxLayout()

        # Category icon and name
        title_text = f"{self.category.icon}  {self.category.name}"
        title = QLabel(title_text)
        title.setObjectName("categoryTitle")
        title.setStyleSheet("""
            QLabel#categoryTitle {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        title_layout.addWidget(title)

        title_layout.addStretch()

        # Tools count badge
        count_badge = QLabel(f"{len(self.category.items)} tools")
        count_badge.setObjectName("countBadge")
        count_badge.setStyleSheet("""
            QLabel#countBadge {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 6px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
        """)
        title_layout.addWidget(count_badge)

        layout.addLayout(title_layout)

        # Description
        if self.category.description:
            desc = QLabel(self.category.description)
            desc.setObjectName("categoryDescription")
            desc.setStyleSheet("""
                QLabel#categoryDescription {
                    color: rgba(255, 255, 255, 0.9);
                    font-size: 14px;
                    background: transparent;
                    line-height: 1.4;
                }
            """)
            desc.setWordWrap(True)
            layout.addWidget(desc)

        header.setLayout(layout)
        return header

    def create_enhanced_control_panel(self):
        """Create enhanced control panel"""
        controls = QFrame()
        controls.setObjectName("controlPanel")
        controls.setStyleSheet("""
            QFrame#controlPanel {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 16px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Top row: Selection controls and view options
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Selection controls
        selection_group = self.create_selection_controls()
        top_row.addWidget(selection_group)

        top_row.addStretch()

        # View mode toggle
        view_toggle = self.create_view_toggle()
        top_row.addWidget(view_toggle)

        layout.addLayout(top_row)

        # Bottom row: Stats and execute button
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        # Selection stats
        self.stats_label = QLabel("0 tools selected")
        self.stats_label.setObjectName("selectionStats")
        self.stats_label.setStyleSheet("""
            QLabel#selectionStats {
                font-size: 14px;
                color: #6b7280;
                font-weight: 600;
                padding: 8px 0px;
            }
        """)
        bottom_row.addWidget(self.stats_label)

        bottom_row.addStretch()

        # Execute button
        self.execute_btn = QPushButton("🚀 Execute Selected Tools")
        self.execute_btn.setObjectName("executeSelectedButton")
        self.execute_btn.setEnabled(False)
        self.execute_btn.clicked.connect(self.execute_selected_tools)
        self.execute_btn.setStyleSheet("""
            QPushButton#executeSelectedButton {
                background-color: #4f46e5;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 200px;
            }

            QPushButton#executeSelectedButton:hover {
                background-color: #3730a3;
            }

            QPushButton#executeSelectedButton:disabled {
                background-color: #d1d5db;
                color: #9ca3af;
            }
        """)
        bottom_row.addWidget(self.execute_btn)

        layout.addLayout(bottom_row)
        controls.setLayout(layout)
        return controls

    def create_selection_controls(self):
        """Create selection control buttons mit erweiterte Smart Select"""
        group = QFrame()
        group.setObjectName("selectionGroup")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Select all button
        select_all_btn = QPushButton("✅ Select All")
        select_all_btn.setObjectName("selectionButton")
        select_all_btn.clicked.connect(self.select_all_tools)

        # Select none button
        select_none_btn = QPushButton("❌ Clear Selection")
        select_none_btn.setObjectName("selectionButton")
        select_none_btn.clicked.connect(self.select_no_tools)

        # Enhanced Smart selection button with dropdown menu
        self.smart_select_btn = QPushButton("🎯 Smart Select")
        self.smart_select_btn.setObjectName("selectionButton")
        self.smart_select_btn.setToolTip("Intelligent tool selection")

        # Create dropdown menu for Smart Select
        smart_menu = QMenu(self.smart_select_btn)
        smart_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                background-color: transparent;
                color: #374151;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QMenu::item:selected {
                background-color: #4f46e5;
                color: white;
            }
        """)

        # Add smart selection options
        smart_menu.addAction("🎯 Auto Smart Select", self.smart_select_auto)
        smart_menu.addAction("🔧 Essential Maintenance", self.smart_select_maintenance)
        smart_menu.addAction("🚀 Quick Setup", self.smart_select_quick_setup)
        smart_menu.addAction("🖥️ Hardware Specific", self.smart_select_hardware)
        smart_menu.addAction("💻 Development Tools", self.smart_select_development)
        smart_menu.addAction("📂 Category Recommended", self.smart_select_category)

        self.smart_select_btn.setMenu(smart_menu)

        # Default action (when button clicked directly)
        self.smart_select_btn.clicked.connect(self.smart_select_auto)

        # Apply button styling
        button_style = """
            QPushButton#selectionButton {
                background-color: #f3f4f6;
                color: #374151;
                border: 2px solid #d1d5db;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                min-width: 90px;
            }

            QPushButton#selectionButton:hover {
                background-color: #e5e7eb;
                border-color: #9ca3af;
            }

            QPushButton#selectionButton:pressed {
                background-color: #d1d5db;
            }

            QPushButton#selectionButton::menu-indicator {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 12px;
                height: 8px;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iIzM3NDE1MSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPHN2Zz4K);
            }
        """

        for btn in [select_all_btn, select_none_btn, self.smart_select_btn]:
            btn.setStyleSheet(button_style)
            layout.addWidget(btn)

        group.setLayout(layout)
        return group

    def create_view_toggle(self):
        """Create view mode toggle"""
        toggle_group = QFrame()
        toggle_group.setObjectName("viewToggle")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Grid view button
        self.grid_btn = QPushButton("⊞ Grid")
        self.grid_btn.setCheckable(True)
        self.grid_btn.setChecked(True)
        self.grid_btn.clicked.connect(lambda: self.set_view_mode("grid"))

        # List view button
        self.list_btn = QPushButton("☰ List")
        self.list_btn.setCheckable(True)
        self.list_btn.clicked.connect(lambda: self.set_view_mode("list"))

        # Button group for exclusive selection
        self.view_button_group = QButtonGroup()
        self.view_button_group.addButton(self.grid_btn)
        self.view_button_group.addButton(self.list_btn)

        # Styling
        toggle_style = """
            QPushButton {
                background-color: #f9fafb;
                color: #6b7280;
                border: 1px solid #d1d5db;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 600;
                min-width: 60px;
            }

            QPushButton:hover {
                background-color: #f3f4f6;
            }

            QPushButton:checked {
                background-color: #4f46e5;
                color: white;
                border-color: #4f46e5;
            }
        """

        self.grid_btn.setStyleSheet(toggle_style + "border-radius: 6px 0px 0px 6px;")
        self.list_btn.setStyleSheet(toggle_style + "border-radius: 0px 6px 6px 0px;")

        layout.addWidget(self.grid_btn)
        layout.addWidget(self.list_btn)

        toggle_group.setLayout(layout)
        return toggle_group

    def create_tools_area(self):
        """Create scrollable tools area"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("toolsScrollArea")
        scroll_area.setStyleSheet("""
            QScrollArea#toolsScrollArea {
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                background-color: #fafbfc;
            }

            QScrollArea#toolsScrollArea QScrollBar:vertical {
                background-color: #f3f4f6;
                width: 8px;
                border-radius: 4px;
                border: none;
            }

            QScrollArea#toolsScrollArea QScrollBar::handle:vertical {
                background-color: #d1d5db;
                border-radius: 4px;
                min-height: 20px;
            }

            QScrollArea#toolsScrollArea QScrollBar::handle:vertical:hover {
                background-color: #9ca3af;
            }
        """)

        # Tools container
        self.tools_container = QWidget()
        self.tools_container.setObjectName("toolsContainer")

        # Initial grid layout
        self.tools_layout = QGridLayout()
        self.tools_layout.setSpacing(12)
        self.tools_layout.setContentsMargins(16, 16, 16, 16)

        # Add tool cards
        self.populate_tools()

        self.tools_container.setLayout(self.tools_layout)
        scroll_area.setWidget(self.tools_container)

        return scroll_area

    def populate_tools(self):
        """Populate tools based on current view mode"""
        # Clear existing cards
        for card in self.tool_cards:
            card.setParent(None)
        self.tool_cards.clear()

        # Create new cards
        for i, tool in enumerate(self.category.items):
            tool_card = ToolCard(tool)
            tool_card.selection_changed.connect(self.on_tool_selection_changed)
            tool_card.tool_selected.connect(self.tool_selected.emit)

            self.tool_cards.append(tool_card)

            # Add to layout based on view mode
            if self.view_mode == "grid":
                row = i // 2  # 2 columns
                col = i % 2
                self.tools_layout.addWidget(tool_card, row, col)
            else:  # list mode
                self.tools_layout.addWidget(tool_card, i, 0, 1, 2)

        # Add stretch at the end
        if self.view_mode == "grid":
            self.tools_layout.setRowStretch(len(self.category.items) // 2 + 1, 1)
        else:
            self.tools_layout.setRowStretch(len(self.category.items), 1)

    def set_view_mode(self, mode):
        """Set view mode (grid or list)"""
        if self.view_mode == mode:
            return

        self.view_mode = mode

        # Update button states
        self.grid_btn.setChecked(mode == "grid")
        self.list_btn.setChecked(mode == "list")

        # Recreate layout
        self.populate_tools()

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
        total = len(self.category.items)

        # Update stats label
        if count == 0:
            self.stats_label.setText("No tools selected")
            self.stats_label.setStyleSheet(self.stats_label.styleSheet().replace("color: #4f46e5", "color: #6b7280"))
        elif count == total:
            self.stats_label.setText(f"All {total} tools selected")
            self.stats_label.setStyleSheet(self.stats_label.styleSheet().replace("color: #6b7280", "color: #10b981"))
        else:
            self.stats_label.setText(f"{count} of {total} tools selected")
            self.stats_label.setStyleSheet(self.stats_label.styleSheet().replace("color: #6b7280", "color: #4f46e5"))

        # Update execute button
        self.execute_btn.setEnabled(count > 0)
        if count > 0:
            if count == 1:
                self.execute_btn.setText("🚀 Execute 1 Tool")
            else:
                self.execute_btn.setText(f"🚀 Execute {count} Tools")
        else:
            self.execute_btn.setText("🚀 Execute Selected Tools")

    def select_all_tools(self):
        """Select all tools"""
        for card in self.tool_cards:
            card.set_selected(True)

    def select_no_tools(self):
        """Deselect all tools"""
        for card in self.tool_cards:
            card.set_selected(False)

    # ================== ERWEITERTE SMART SELECT FUNKTIONEN ==================

    def smart_select_auto(self):
        """Enhanced smart selection with multiple strategies"""
        # Clear current selection
        self.select_no_tools()

        # Define selection strategies with priority scores
        selection_strategies = {
            # High Priority (Essential maintenance)
            'essential_maintenance': {
                'keywords': ['system update', 'clean cache', 'remove orphan', 'mirrorlist'],
                'weight': 10,
                'description': 'Essential system maintenance'
            },

            # Medium Priority (Common tools)
            'common_tools': {
                'keywords': ['driver', 'flatpak setup', 'git', 'python'],
                'weight': 7,
                'description': 'Commonly needed tools'
            },

            # Hardware specific (detected automatically)
            'hardware_specific': {
                'keywords': self._detect_hardware_keywords(),
                'weight': 8,
                'description': 'Hardware-specific tools'
            },

            # Development tools (if dev environment detected)
            'development': {
                'keywords': ['docker', 'vscode', 'virtual machine'] if self._is_dev_environment() else [],
                'weight': 6,
                'description': 'Development environment'
            }
        }

        # Score each tool
        tool_scores = {}
        for card in self.tool_cards:
            tool = card.tool
            tool_text = f"{tool.name} {tool.description}".lower()
            score = 0
            matched_strategies = []

            for strategy_name, strategy in selection_strategies.items():
                for keyword in strategy['keywords']:
                    if keyword.lower() in tool_text:
                        score += strategy['weight']
                        matched_strategies.append(strategy_name)
                        break  # Only count once per strategy

            if score > 0:
                tool_scores[card] = {
                    'score': score,
                    'strategies': matched_strategies,
                    'tool': tool
                }

        # Sort by score and select top tools
        sorted_tools = sorted(tool_scores.items(), key=lambda x: x[1]['score'], reverse=True)

        selected_count = 0
        max_selections = 8  # Increased limit
        strategy_summary = {}

        for card, info in sorted_tools:
            if selected_count >= max_selections:
                break

            card.set_selected(True)
            selected_count += 1

            # Track which strategies were used
            for strategy in info['strategies']:
                strategy_summary[strategy] = strategy_summary.get(strategy, 0) + 1

        # Show detailed tooltip with selection rationale
        if selected_count > 0:
            tooltip_text = f"Auto Smart Selection: {selected_count} tools selected\n\n"
            tooltip_text += "Selection criteria:\n"

            for strategy, count in strategy_summary.items():
                description = selection_strategies[strategy]['description']
                tooltip_text += f"• {description}: {count} tools\n"

            self._show_selection_tooltip("Auto Smart Selection", tooltip_text.strip())

    def smart_select_maintenance(self):
        """Smart select for system maintenance"""
        maintenance_tools = [
            'System Update',
            'Clean Package Cache',
            'Remove Orphans',
            'Update Mirrorlist',
            'Clear System Logs'
        ]

        selected_count = self._select_tools_by_name(maintenance_tools)
        self._show_selection_tooltip("Maintenance Mode",
            f"Selected {selected_count} essential maintenance tools\n\n"
            "• System updates and cleanup\n"
            "• Package cache management\n"
            "• Mirror optimization")

    def smart_select_quick_setup(self):
        """Smart select for new system setup"""
        quick_setup_tools = [
            'System Update',
            'Setup Flatpak',
            'Install Yay',  # or Paru
            'UFW Firewall',
        ]

        # Add graphics driver based on detection
        quick_setup_tools.extend(self._get_graphics_recommendations())

        selected_count = self._select_tools_by_name(quick_setup_tools)
        self._show_selection_tooltip("Quick Setup",
            f"Selected {selected_count} tools for new system setup\n\n"
            "• System updates\n"
            "• Package managers\n"
            "• Security basics\n"
            "• Hardware drivers")

    def smart_select_hardware(self):
        """Smart select hardware-specific tools"""
        self.select_no_tools()

        hardware_keywords = self._detect_hardware_keywords()
        selected_count = 0

        for card in self.tool_cards:
            tool = card.tool
            tool_text = f"{tool.name} {tool.description}".lower()

            if any(keyword.lower() in tool_text for keyword in hardware_keywords):
                card.set_selected(True)
                selected_count += 1

        detected_hardware = ", ".join(hardware_keywords) if hardware_keywords else "Generic"
        self._show_selection_tooltip("Hardware Specific",
            f"Selected {selected_count} hardware-specific tools\n\n"
            f"Detected hardware: {detected_hardware}")

    def smart_select_development(self):
        """Smart select development tools"""
        dev_keywords = ['docker', 'vscode', 'visual studio', 'python', 'git', 'development', 'virtual machine']

        self.select_no_tools()
        selected_count = 0

        for card in self.tool_cards:
            tool = card.tool
            tool_text = f"{tool.name} {tool.description}".lower()

            if any(keyword in tool_text for keyword in dev_keywords):
                card.set_selected(True)
                selected_count += 1

        if selected_count == 0:
            # If no dev tools in current category, show message
            self._show_selection_tooltip("Development Tools",
                "No development tools found in this category.\n"
                "Try the 'Development Tools' category for programming tools.")
        else:
            self._show_selection_tooltip("Development Tools",
                f"Selected {selected_count} development tools\n\n"
                "• IDEs and editors\n"
                "• Programming languages\n"
                "• Development utilities")

    def smart_select_category(self):
        """Smart select based on current category"""
        category_strategies = {
            'system_maintenance': ['System Update', 'Clean Package Cache', 'Remove Orphans'],
            'graphics': self._get_graphics_recommendations(),
            'development': ['Visual Studio Code', 'Docker', 'Python Development'],
            'multimedia': ['VLC Media Player', 'GIMP'],
            'gaming': ['Steam', 'Wine'],
            'productivity': ['LibreOffice', 'Thunderbird'],
            'security': ['UFW Firewall'],
            'flatpak': ['Setup Flatpak'],
            'troubleshoot': self._get_troubleshoot_recommendations(),
        }

        current_category = self.category.id
        recommended_tools = category_strategies.get(current_category, [])

        if not recommended_tools:
            # Fallback to general smart select
            return self.smart_select_auto()

        # Select recommended tools for this category
        selected_count = self._select_tools_by_name(recommended_tools)

        self._show_selection_tooltip("Category Recommended",
            f"Selected {selected_count} recommended tools for {self.category.name}\n\n"
            f"Category-specific recommendations based on\n"
            f"common use cases and best practices.")

    # ================== HELPER FUNCTIONS ==================

    def _detect_hardware_keywords(self):
        """Detect hardware-specific keywords based on system"""
        hardware_keywords = []

        try:
            # Try to detect GPU
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
            output = result.stdout.lower()

            # Check for NVIDIA
            if 'nvidia' in output:
                hardware_keywords.extend(['nvidia', 'nvidia driver'])

            # Check for AMD
            if 'amd' in output or 'radeon' in output:
                hardware_keywords.extend(['amd', 'amd driver', 'mesa'])

            # Check for Intel graphics
            if 'intel' in output and 'graphics' in output:
                hardware_keywords.extend(['intel graphics', 'intel driver'])

        except Exception:
            # Fallback to common hardware
            hardware_keywords = ['nvidia', 'amd', 'intel graphics']

        return hardware_keywords

    def _is_dev_environment(self):
        """Check if this looks like a development environment"""
        dev_indicators = [
            # Check for common dev directories
            os.path.exists(os.path.expanduser('~/git')),
            os.path.exists(os.path.expanduser('~/Projects')),
            os.path.exists(os.path.expanduser('~/Code')),

            # Check for dev tools
            shutil.which('git') is not None,
            shutil.which('code') is not None,
            shutil.which('docker') is not None,

            # Check for Python virtual environments
            'VIRTUAL_ENV' in os.environ,
            os.path.exists(os.path.expanduser('~/.virtualenvs')),
        ]

        # If more than 2 indicators are true, consider it a dev environment
        return sum(dev_indicators) >= 2

    def _get_graphics_recommendations(self):
        """Get graphics driver recommendations based on hardware"""
        recommendations = []

        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
            output = result.stdout.lower()

            if 'nvidia' in output:
                recommendations.append('NVIDIA Open Drivers')  # Prefer open drivers
            elif 'amd' in output or 'radeon' in output:
                recommendations.append('AMD Drivers')
            elif 'intel' in output:
                recommendations.append('Intel Graphics')

        except:
            # If detection fails, suggest most common
            recommendations = ['NVIDIA Open Drivers', 'AMD Drivers']

        return recommendations

    def _get_troubleshoot_recommendations(self):
        """Get troubleshooting recommendations based on common issues"""
        # Could be enhanced to detect actual system issues
        common_issues = [
            'No Audio Devices',  # Very common on new installs
            'Bluetooth can\'t start',  # Common Bluetooth issues
            'Network-Manager'  # Network connectivity issues
        ]
        return common_issues

    def _select_tools_by_name(self, tool_names):
        """Helper to select tools by name"""
        self.select_no_tools()

        selected_count = 0
        for card in self.tool_cards:
            if card.tool.name in tool_names:
                card.set_selected(True)
                selected_count += 1

        return selected_count

    def _show_selection_tooltip(self, title, message):
        """Show informative tooltip about selection"""
        if hasattr(self, 'selected_tools') and len(self.selected_tools) > 0:
            QToolTip.showText(
                self.smart_select_btn.mapToGlobal(self.smart_select_btn.rect().center()),
                f"{title}\n\n{message}",
                self,
                self.smart_select_btn.rect(),
                5000  # Show for 5 seconds
            )

    # ================== ORIGINAL FUNCTIONS ==================

    def execute_selected_tools(self):
        """Execute selected tools with enhanced confirmation"""
        if not self.selected_tools:
            return

        selected_list = list(self.selected_tools.values())

        # Show detailed confirmation dialog
        dialog = ExecutionConfirmationDialog(selected_list, self)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            self.tools_selected.emit(selected_list)

    def get_selected_tools(self):
        """Get list of selected tools"""
        return list(self.selected_tools.values())

    def clear_selection(self):
        """Clear all selections"""
        self.select_no_tools()

class ExecutionConfirmationDialog(QMessageBox):
    """Enhanced execution confirmation dialog"""

    def __init__(self, tools_list, parent=None):
        super().__init__(parent)
        self.tools_list = tools_list
        self.setup_dialog()

    def setup_dialog(self):
        """Setup confirmation dialog"""
        self.setWindowTitle("Confirm Tool Execution")
        self.setIcon(QMessageBox.Icon.Question)

        count = len(self.tools_list)
        if count == 1:
            self.setText(f"Execute '{self.tools_list[0].name}'?")
        else:
            self.setText(f"Execute {count} selected tools?")

        # Build detailed information
        info_text = "The following tools will be executed:\n\n"

        for i, tool in enumerate(self.tools_list[:8], 1):
            info_text += f"{i}. {tool.name}\n"
            info_text += f"   └─ {tool.description}\n"

        if len(self.tools_list) > 8:
            info_text += f"\n... and {len(self.tools_list) - 8} more tools"

        info_text += f"\n\n⚠️ This will execute {count} system command(s)."
        info_text += "\nMake sure you understand what each tool does."

        self.setInformativeText(info_text)
        self.setDetailedText(self.build_commands_text())

        # Custom buttons
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        self.setDefaultButton(QMessageBox.StandardButton.No)

        # Style the dialog
        self.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #1f2937;
            }
            QMessageBox QPushButton {
                background-color: #4f46e5;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #3730a3;
            }
        """)

    def build_commands_text(self):
        """Build detailed commands text"""
        commands_text = "Commands that will be executed:\n\n"

        for i, tool in enumerate(self.tools_list, 1):
            commands_text += f"{i}. {tool.name}:\n"
            commands_text += f"   {tool.command}\n\n"

        return commands_text

# Export classes
__all__ = ['CategoryWidget', 'ToolCard', 'ExecutionConfirmationDialog']
