"""
Main application window
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QListWidget, QListWidgetItem, QTableWidget,
    QLineEdit, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Import theme and styles
from .styles.modern_theme import ModernTheme

class MainWindow(QMainWindow):
    """Moderne Hauptfenster-Klasse mit einheitlichem Design"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔧 Arch Linux Configuration Tool")
        self.setGeometry(100, 100, 1400, 900)

        # Set styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {ModernTheme.BACKGROUND};
                font-family: {ModernTheme.FONT_FAMILY};
            }}
        """)

        # Initialize components
        self.init_components()
        self.setup_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.load_configuration()

    def init_components(self):
        """Initialize backend components and UI state"""
        # Backend components
        try:
            from core.config_manager import ConfigManager
            from core.command_executor import CommandExecutor
            self.config_manager = ConfigManager()
            self.command_executor = CommandExecutor()
        except ImportError as e:
            print(f"Warning: Backend import failed: {e}")
            # Create mock manager for testing
            self.config_manager = MockConfigManager()
            self.command_executor = None

        # UI state
        self.categories = {}
        self.current_category = None
        self.command_history = []

    def setup_ui(self):
        """Initialize modern user interface"""
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {ModernTheme.BACKGROUND};")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Sidebar und Content
        sidebar = self.create_sidebar()
        content = self.create_content_area()

        if sidebar:
            main_layout.addWidget(sidebar, 1)
        if content:
            main_layout.addWidget(content, 3)

        central_widget.setLayout(main_layout)

    def create_sidebar(self):
        """Create sidebar"""
        sidebar_card = QWidget()
        sidebar_card.setFixedWidth(320)
        sidebar_card.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        title = QLabel("🗂️ Kategorien")
        title.setFont(QFont(ModernTheme.FONT_FAMILY, 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        subtitle = QLabel("Wählen Sie eine Kategorie aus")
        subtitle.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        subtitle.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        layout.addWidget(subtitle)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Suche nach Tools...")
        self.search_box.textChanged.connect(self.on_search_changed)
        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                font-family: {ModernTheme.FONT_FAMILY};
                font-size: {ModernTheme.FONT_SIZE_MD};
                padding: {ModernTheme.SPACING_SM} {ModernTheme.SPACING_MD};
                border: 2px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_SMALL};
                background-color: {ModernTheme.SURFACE};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {ModernTheme.PRIMARY};
            }}
        """)
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
        refresh_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {ModernTheme.PRIMARY};
                border: 2px solid {ModernTheme.PRIMARY};
                padding: {ModernTheme.SPACING_SM} {ModernTheme.SPACING_MD};
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {ModernTheme.PRIMARY};
                color: white;
            }}
        """)
        layout.addWidget(refresh_button)

        sidebar_card.setLayout(layout)
        return sidebar_card

    def create_content_area(self):
        """Create content area"""
        content_card = QWidget()
        content_card.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                margin-top: 5px;
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {ModernTheme.TEXT_SECONDARY};
                padding: {ModernTheme.SPACING_SM} {ModernTheme.SPACING_LG};
                margin-right: 2px;
                border-radius: {ModernTheme.RADIUS_SMALL};
                font-family: {ModernTheme.FONT_FAMILY};
                font-size: {ModernTheme.FONT_SIZE_MD};
                font-weight: 600;
            }}
            QTabBar::tab:hover {{
                background-color: {ModernTheme.BORDER};
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QTabBar::tab:selected {{
                background-color: transparent;
                color: {ModernTheme.PRIMARY};
            }}
        """)

        # Tools tab
        self.tools_tab = QScrollArea()
        self.tools_tab.setWidgetResizable(True)
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
        self.tools_layout.setSpacing(24)
        self.tools_content.setLayout(self.tools_layout)
        self.tools_tab.setWidget(self.tools_content)
        self.tab_widget.addTab(self.tools_tab, "🛠️ Tools")

        # Add placeholder tabs
        history_tab = QWidget()
        history_tab.setStyleSheet(f"background-color: {ModernTheme.BACKGROUND};")
        history_layout = QVBoxLayout()
        history_label = QLabel("📋 Verlauf wird implementiert...")
        history_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        history_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; font-size: 16px;")
        history_layout.addWidget(history_label)
        history_tab.setLayout(history_layout)
        self.tab_widget.addTab(history_tab, "📋 Verlauf")

        stats_tab = QWidget()
        stats_tab.setStyleSheet(f"background-color: {ModernTheme.BACKGROUND};")
        stats_layout = QVBoxLayout()

        self.stats_content = QLabel("📊 Statistiken werden geladen...")
        self.stats_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stats_content.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; font-size: 16px;")
        stats_layout.addWidget(self.stats_content)
        stats_tab.setLayout(stats_layout)
        self.tab_widget.addTab(stats_tab, "📊 Statistiken")

        layout.addWidget(self.tab_widget)
        content_card.setLayout(layout)
        return content_card

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

    def run_dependency_check(self):
        """Run dependency check dialog"""
        try:
            # For now, just show a simple dialog
            QMessageBox.information(self, "Dependency Check", "🔍 Dependency Check wird implementiert...")
        except Exception as e:
            print(f"Dependency check error: {e}")

    def load_configuration(self):
        """Load configuration from ConfigManager"""
        print("Loading configuration...")
        self.statusBar().showMessage("⏳ Lade Konfiguration...")

        try:
            self.categories = self.config_manager.get_config()
            print(f"Loaded {len(self.categories)} categories")
            self.populate_categories()
            self.statusBar().showMessage(f"✅ Konfiguration geladen: {len(self.categories)} Kategorien")
        except Exception as e:
            print(f"Error loading configuration: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Konfiguration:\n{e}")
            self.statusBar().showMessage("❌ Fehler beim Laden der Konfiguration")

    def populate_categories(self):
        """Populate the categories list with modern styling"""
        print("Populating categories...")
        self.categories_list.clear()

        for category in self.config_manager.get_categories():
            print(f"Adding category: {category.name} with {len(category.items)} items")
            item = QListWidgetItem()
            item.setText(f"{category.icon} {category.name}")
            item.setData(Qt.ItemDataRole.UserRole, category.id)
            item.setToolTip(f"{category.description}\n\n📊 {len(category.items)} Tools verfügbar")
            self.categories_list.addItem(item)

        # Select first category by default
        if self.categories_list.count() > 0:
            print("Selecting first category")
            self.categories_list.setCurrentRow(0)
            self.on_category_selected(self.categories_list.item(0))

    def on_category_selected(self, item):
        """Handle category selection"""
        category_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_category = category_id
        print(f"Category selected: {category_id}")

        if category_id in self.categories:
            category = self.categories[category_id]
            print(f"Showing category with {len(category.items)} items")
            self.show_category_tools(category)
            self.statusBar().showMessage(f"📂 Kategorie: {category.name}")

    def show_category_tools(self, category):
        """Show tools for selected category"""
        print(f"Showing tools for category: {category.name}")

        # Clear current content safely
        self.clear_tools_layout()

        # For now, show a simple placeholder
        try:
            # Try to import and use CategoryWidget
            from .widgets.category_widget import CategoryWidget
            category_widget = CategoryWidget(category)
            category_widget.tool_selected.connect(self.on_tool_selected)
            self.tools_layout.addWidget(category_widget)
            print("CategoryWidget successfully added")
        except ImportError as e:
            print(f"CategoryWidget import failed: {e}")
            # Fallback: simple placeholder with tool list
            self.create_simple_category_display(category)
        except Exception as e:
            print(f"Error creating CategoryWidget: {e}")
            # Fallback: simple placeholder
            self.create_simple_category_display(category)

        self.tools_layout.addStretch()
        print("Category widget added to layout")

    def clear_tools_layout(self):
        """Safely clear the tools layout"""
        print(f"Clearing tools layout with {self.tools_layout.count()} items...")

        # Collect all items first
        items_to_remove = []
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item is not None:
                items_to_remove.append(item)

        # Remove items safely
        for item in items_to_remove:
            self.tools_layout.removeItem(item)

            if item.widget() is not None:
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
                print(f"  ✓ Widget removed")
            elif item.layout() is not None:
                # Handle nested layouts
                layout = item.layout()
                self.clear_layout_recursive(layout)
                print(f"  ✓ Layout removed")
            else:
                print(f"  ✓ Empty item removed")

        print(f"Layout cleared. Items remaining: {self.tools_layout.count()}")

    def clear_layout_recursive(self, layout):
        """Recursively clear a layout"""
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            if item.widget() is not None:
                item.widget().setParent(None)
                item.widget().deleteLater()
            elif item.layout() is not None:
                self.clear_layout_recursive(item.layout())

    def create_simple_category_display(self, category):
        """Create a simple category display as fallback"""
        print(f"Creating simple display for {category.name}")

        # Main container
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: {ModernTheme.RADIUS_MEDIUM};
                padding: {ModernTheme.SPACING_LG};
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(16)

        # Header
        header = QLabel(f"{category.icon} {category.name}")
        header.setFont(QFont(ModernTheme.FONT_FAMILY, 20, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(header)

        # Description
        if category.description:
            desc = QLabel(category.description)
            desc.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
            desc.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
            desc.setWordWrap(True)
            layout.addWidget(desc)

        # Tools count
        tools_count = QLabel(f"📦 {len(category.items)} Tools verfügbar")
        tools_count.setFont(QFont(ModernTheme.FONT_FAMILY, 14, QFont.Weight.Bold))
        tools_count.setStyleSheet(f"color: {ModernTheme.PRIMARY}; background: transparent;")
        layout.addWidget(tools_count)

        # Tool list
        tools_widget = QWidget()
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(8)

        for i, tool in enumerate(category.items[:5]):  # Show max 5 tools
            tool_item = QWidget()
            tool_item.setStyleSheet(f"""
                QWidget {{
                    background-color: {ModernTheme.SURFACE_DARK};
                    border: 1px solid {ModernTheme.BORDER};
                    border-radius: {ModernTheme.RADIUS_SMALL};
                    padding: {ModernTheme.SPACING_SM};
                    margin: 2px 0px;
                }}
            """)

            tool_layout = QHBoxLayout()
            tool_layout.setContentsMargins(8, 4, 8, 4)

            # Tool name
            tool_name = QLabel(f"{i+1}. {tool.name}")
            tool_name.setFont(QFont(ModernTheme.FONT_FAMILY, 11, QFont.Weight.Bold))
            tool_name.setStyleSheet(f"color: {ModernTheme.TEXT_PRIMARY}; background: transparent;")
            tool_layout.addWidget(tool_name)

            tool_layout.addStretch()

            # Simple button
            btn = QPushButton("Info")
            btn.setFixedSize(50, 24)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ModernTheme.PRIMARY};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {ModernTheme.PRIMARY_DARK};
                }}
            """)
            btn.clicked.connect(lambda checked, t=tool: self.show_tool_info(t))
            tool_layout.addWidget(btn)

            tool_item.setLayout(tool_layout)
            tools_layout.addWidget(tool_item)

        if len(category.items) > 5:
            more_label = QLabel(f"... und {len(category.items) - 5} weitere Tools")
            more_label.setStyleSheet(f"color: {ModernTheme.TEXT_DISABLED}; font-style: italic; background: transparent;")
            tools_layout.addWidget(more_label)

        tools_widget.setLayout(tools_layout)
        layout.addWidget(tools_widget)

        # Note about CategoryWidget
        note = QLabel("💡 CategoryWidget wird geladen...")
        note.setStyleSheet(f"color: {ModernTheme.TEXT_DISABLED}; font-style: italic; background: transparent;")
        layout.addWidget(note)

        container.setLayout(layout)
        self.tools_layout.addWidget(container)

    def show_tool_info(self, tool):
        """Show tool information dialog"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Tool Information")
        msg_box.setText(f"🔧 {tool.name}")
        msg_box.setInformativeText(
            f"📝 <b>Beschreibung:</b><br>{tool.description}<br><br>"
            f"💻 <b>Befehl:</b><br><code>{tool.command}</code>"
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def on_search_changed(self, text: str):
        """Handle search input"""
        print(f"Search changed: '{text}'")

        if not text.strip():
            # Reset to show categories
            try:
                self.populate_categories()
            except Exception as e:
                print(f"Error populating categories: {e}")
            return

        # Clear current content safely
        self.clear_tools_layout()

        # Show "search not implemented" message
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

        title_label = QLabel("🔍 Suche wird implementiert...")
        title_label.setFont(QFont(ModernTheme.FONT_FAMILY, 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: {ModernTheme.TEXT_SECONDARY}; background: transparent;")
        no_results_layout.addWidget(title_label)

        desc_label = QLabel(f"Die Suchfunktion für '{text}' wird noch implementiert.")
        desc_label.setFont(QFont(ModernTheme.FONT_FAMILY, 12))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet(f"color: {ModernTheme.TEXT_DISABLED}; background: transparent;")
        desc_label.setWordWrap(True)
        no_results_layout.addWidget(desc_label)

        no_results_card.setLayout(no_results_layout)
        self.tools_layout.addWidget(no_results_card)
        self.tools_layout.addStretch()

    def on_tool_selected(self, item):
        """Handle tool selection and execution"""
        print(f"Tool selected: {item.name}")

        # Modern confirmation dialog
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Befehl ausführen")
        msg_box.setText("🚀 Tool ausführen")
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

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            print(f"User confirmed execution of: {item.command}")
            QMessageBox.information(self, "Ausführung", f"Tool '{item.name}' würde jetzt ausgeführt werden:\n{item.command}")

    def refresh_configuration(self):
        """Refresh configuration"""
        print("Refreshing configuration...")
        self.statusBar().showMessage("🔄 Aktualisiere Konfiguration...")

        try:
            self.categories = self.config_manager.get_config(force_update=True)
            self.populate_categories()
            self.statusBar().showMessage("✅ Konfiguration aktualisiert")

            QMessageBox.information(self, "Erfolg", "✅ Konfiguration erfolgreich aktualisiert!")
        except Exception as e:
            print(f"Error refreshing configuration: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Aktualisieren:\n{e}")
            self.statusBar().showMessage("❌ Fehler beim Aktualisieren")

    def clear_history(self):
        """Clear command history"""
        print("Clearing history...")
        self.command_history.clear()
        if hasattr(self, 'history_table'):
            self.history_table.setRowCount(0)
        self.statusBar().showMessage("🗑️ Verlauf gelöscht")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "Über Arch Config Tool",
                         "🔧 Arch Linux Configuration Tool\n\n"
                         "Version 2.0\n\n"
                         "Ein modernes GUI-Tool für die Systemkonfiguration\n"
                         "und -wartung von Arch-basierten Linux-Distributionen.")

    def add_command_to_history(self, command_data):
        """Add a command to the history"""
        self.command_history.append(command_data)
        # Keep only last 100 commands
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
        print(f"Command added to history: {command_data.get('command', 'Unknown')}")

    def update_stats(self):
        """Update statistics display"""
        print("Updating stats...")
        # Simple stats for now
        if hasattr(self, 'stats_content'):
            total_tools = sum(len(cat.items) for cat in self.categories.values())
            stats_html = f"""
            <h2>📊 Statistiken</h2>
            <p><strong>Kategorien geladen:</strong> {len(self.categories)}</p>
            <p><strong>Tools verfügbar:</strong> {total_tools}</p>
            <p><strong>Befehle ausgeführt:</strong> {len(self.command_history)}</p>
            """
            self.stats_content.setText(stats_html)

    def closeEvent(self, event):
        """Handle application close event"""
        print("Application closing...")
        event.accept()


# Mock ConfigManager for testing when backend is not available
class MockConfigManager:
    """Mock config manager for testing"""

    def get_config(self, force_update=False):
        """Return mock configuration"""
        from core.config_manager import ConfigCategory, ConfigItem

        categories = {
            "graphics": ConfigCategory(
                id="graphics",
                name="Graphics Drivers",
                description="Graphics drivers and related tools",
                icon="🎮",
                items=[
                    ConfigItem("AMD Drivers", "AMD graphics drivers", "sudo pacman -S mesa", tags=["amd", "drivers"]),
                    ConfigItem("NVIDIA Drivers", "NVIDIA graphics drivers", "sudo pacman -S nvidia", tags=["nvidia", "drivers"]),
                ]
            ),
            "system": ConfigCategory(
                id="system",
                name="System Tools",
                description="Essential system tools",
                icon="🔧",
                items=[
                    ConfigItem("System Update", "Update the system", "sudo pacman -Syu", tags=["update"]),
                ]
            )
        }
        return categories

    def get_categories(self):
        """Return list of categories"""
        return list(self.get_config().values())


# Export for main.py
__all__ = ['MainWindow']


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
    """)
