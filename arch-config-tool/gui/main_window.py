"""
Main application window - Mit Multi-Selection Checkboxen
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QScrollArea, QLineEdit, QMessageBox,
    QTextEdit, QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Import the advanced CategoryWidget with checkboxes
from gui.widgets.category_widget import CategoryWidget

class MainWindow(QMainWindow):
    """Main application window - mit Multi-Selection"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔧 Arch Linux Configuration Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Command history for tabs
        self.command_history = []

        # Backend components
        self.init_backend()

        # Setup UI
        self.setup_ui()
        self.setup_menu()

        # Load configuration
        self.load_configuration()

    def init_backend(self):
        """Initialize backend components"""
        try:
            from core.config_manager import ConfigManager
            from core.command_executor import CommandExecutor
            from core.dependency_check import DependencyChecker

            self.config_manager = ConfigManager()
            self.command_executor = CommandExecutor()
            self.dependency_checker = DependencyChecker(self)

        except ImportError as e:
            print(f"Backend import failed: {e}")
            self.show_error("Failed to load backend components")

        self.categories = {}
        self.current_category = None

    def setup_ui(self):
        """Setup main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with splitter
        layout = QHBoxLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left sidebar
        sidebar = self.create_sidebar()
        splitter.addWidget(sidebar)

        # Right content area with tabs
        content = self.create_tabbed_content_area()
        splitter.addWidget(content)

        # Set splitter proportions
        splitter.setSizes([300, 900])

        layout.addWidget(splitter)
        central_widget.setLayout(layout)

    def create_sidebar(self):
        """Create left sidebar with categories"""
        sidebar = QWidget()
        sidebar.setMaximumWidth(350)
        sidebar.setProperty("class", "sidebar")

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("📂 Categories")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setProperty("class", "sidebar-title")
        layout.addWidget(title)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search tools...")
        self.search_box.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_box)

        # Categories list
        self.categories_list = QListWidget()
        self.categories_list.itemClicked.connect(self.on_category_selected)
        layout.addWidget(self.categories_list)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Config")
        refresh_btn.clicked.connect(self.refresh_configuration)
        layout.addWidget(refresh_btn)

        sidebar.setLayout(layout)
        return sidebar

    def create_tabbed_content_area(self):
        """Create main content area with tabs"""
        # Tab widget
        self.tab_widget = QTabWidget()

        # Tools tab (main content)
        self.tools_tab = self.create_tools_tab()
        self.tab_widget.addTab(self.tools_tab, "🛠️ Tools")

        # History tab
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📋 Verlauf")

        # Statistics tab
        self.stats_tab = self.create_stats_tab()
        self.tab_widget.addTab(self.stats_tab, "📊 Statistiken")

        return self.tab_widget

    def create_tools_tab(self):
        """Create the main tools tab"""
        content = QScrollArea()
        content.setWidgetResizable(True)
        content.setProperty("class", "content-area")

        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(20, 20, 20, 20)

        # Welcome message
        welcome = QLabel("👋 Welcome to Arch Config Tool")
        welcome.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome.setProperty("class", "welcome-title")
        self.content_layout.addWidget(welcome)

        info = QLabel("Select a category from the sidebar to view available tools.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setProperty("class", "welcome-subtitle")
        self.content_layout.addWidget(info)

        # Multi-Selection Info
        multi_info = QLabel("✅ Use checkboxes to select multiple tools and execute them together!")
        multi_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        multi_info.setStyleSheet("color: #2196F3; font-weight: bold; margin: 10px;")
        self.content_layout.addWidget(multi_info)

        self.content_layout.addStretch()
        self.content_widget.setLayout(self.content_layout)
        content.setWidget(self.content_widget)

        return content

    def create_history_tab(self):
        """Create command history tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("📋 Command History")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Time", "Tool", "Status", "Exit Code", "Duration"
        ])

        # Make table look nice
        header_view = self.history_table.horizontalHeader()
        header_view.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.history_table)

        # Clear history button
        clear_btn = QPushButton("🗑️ Clear History")
        clear_btn.setProperty("class", "warning")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)

        widget.setLayout(layout)
        return widget

    def create_stats_tab(self):
        """Create statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("📊 Statistics")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header)

        # Stats content
        self.stats_content = QLabel()
        self.stats_content.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stats_content.setWordWrap(True)
        layout.addWidget(self.stats_content)

        # Refresh stats button
        refresh_stats_btn = QPushButton("🔄 Refresh Statistics")
        refresh_stats_btn.clicked.connect(self.update_stats)
        layout.addWidget(refresh_stats_btn)

        layout.addStretch()

        # Load initial stats
        self.update_stats()

        widget.setLayout(layout)
        return widget

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Refresh Configuration", self.refresh_configuration)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction("Dependency Check", self.run_dependency_check)
        tools_menu.addAction("Clear History", self.clear_history)

        # Help menu
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About", self.show_about)

    def load_configuration(self):
        """Load configuration from ConfigManager"""
        self.statusBar().showMessage("Loading configuration...")

        try:
            self.categories = self.config_manager.get_config()
            self.populate_categories()
            self.statusBar().showMessage(f"✅ Loaded {len(self.categories)} categories")
            self.update_stats()  # Update stats when config loads

        except Exception as e:
            self.show_error(f"Failed to load configuration: {e}")
            self.statusBar().showMessage("❌ Configuration load failed")

    def populate_categories(self):
        """Populate categories list"""
        self.categories_list.clear()

        for category in self.config_manager.get_categories():
            item = QListWidgetItem()
            item.setText(f"{category.icon} {category.name} ({len(category.items)})")
            item.setData(Qt.ItemDataRole.UserRole, category.id)
            self.categories_list.addItem(item)

        # Select first category
        if self.categories_list.count() > 0:
            self.categories_list.setCurrentRow(0)
            self.on_category_selected(self.categories_list.item(0))

    def on_category_selected(self, item):
        """Handle category selection"""
        category_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_category = category_id

        if category_id in self.categories:
            self.show_category_tools(self.categories[category_id])

    def show_category_tools(self, category):
        """Display tools for selected category - with advanced multi-selection widget"""
        # Switch to tools tab
        self.tab_widget.setCurrentIndex(0)

        # Clear current content
        self.clear_content_layout()

        # Create advanced category widget with checkboxes and multi-selection
        category_widget = CategoryWidget(category)

        # Connect signals
        category_widget.tool_selected.connect(self.on_tool_selected)
        category_widget.tools_selected.connect(self.on_tools_selected)  # Multi-selection

        self.content_layout.addWidget(category_widget)

        self.statusBar().showMessage(f"📂 {category.name} - {len(category.items)} tools | ✅ Multi-selection enabled")

    def clear_content_layout(self):
        """Clear content layout safely"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def on_tool_selected(self, tool):
        """Handle single tool execution"""
        reply = QMessageBox.question(
            self,
            "Execute Tool",
            f"Execute '{tool.name}'?\n\nCommand: {tool.command}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.execute_tool(tool)

    def on_tools_selected(self, tools_list):
        """Handle multiple tools execution (MULTI-SELECTION)"""
        if not tools_list:
            return

        # Show detailed confirmation for batch execution
        msg = QMessageBox(self)
        msg.setWindowTitle("🚀 Batch Execute Tools")
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(f"Execute {len(tools_list)} selected tools?")

        # Build tool list for confirmation
        tools_text = "\n".join([f"• {tool.name}" for tool in tools_list[:8]])
        if len(tools_list) > 8:
            tools_text += f"\n... and {len(tools_list) - 8} more tools"

        msg.setInformativeText(f"The following tools will be executed in sequence:\n\n{tools_text}")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)

        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.execute_multiple_tools(tools_list)

    def execute_tool(self, tool):
        """Execute single tool"""
        from datetime import datetime

        try:
            start_time = datetime.now()
            self.statusBar().showMessage(f"🔄 Executing: {tool.name}...")

            result = self.command_executor.execute_command(tool.command)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Add to history
            history_entry = {
                'time': start_time.strftime("%H:%M:%S"),
                'tool': tool.name,
                'status': result.status.value,
                'return_code': result.return_code,
                'duration': f"{duration:.1f}s"
            }
            self.command_history.append(history_entry)
            self.update_history_table()
            self.update_stats()

            if result.status.value == "success":
                self.statusBar().showMessage(f"✅ {tool.name} completed successfully!")
                QMessageBox.information(self, "Success", f"'{tool.name}' executed successfully!")
            else:
                self.statusBar().showMessage(f"❌ {tool.name} failed!")
                QMessageBox.warning(self, "Failed", f"'{tool.name}' failed:\n{result.stderr}")

        except Exception as e:
            self.show_error(f"Execution failed: {e}")

    def execute_multiple_tools(self, tools_list):
        """Execute multiple tools in sequence"""
        from datetime import datetime

        success_count = 0
        failed_count = 0

        # Progress tracking
        total_tools = len(tools_list)

        for i, tool in enumerate(tools_list, 1):
            try:
                self.statusBar().showMessage(f"🔄 Executing {i}/{total_tools}: {tool.name}...")

                start_time = datetime.now()
                result = self.command_executor.execute_command(tool.command)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()

                # Add to history
                history_entry = {
                    'time': start_time.strftime("%H:%M:%S"),
                    'tool': tool.name,
                    'status': result.status.value,
                    'return_code': result.return_code,
                    'duration': f"{duration:.1f}s"
                }
                self.command_history.append(history_entry)

                if result.status.value == "success":
                    success_count += 1
                    print(f"✅ {tool.name} - Success")
                else:
                    failed_count += 1
                    print(f"❌ {tool.name} - Failed: {result.stderr}")

            except Exception as e:
                failed_count += 1
                print(f"❌ {tool.name} - Error: {e}")

                # Add failed entry to history
                history_entry = {
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'tool': tool.name,
                    'status': 'failed',
                    'return_code': -1,
                    'duration': '0.0s'
                }
                self.command_history.append(history_entry)

        # Update UI
        self.update_history_table()
        self.update_stats()

        # Show final result
        if failed_count == 0:
            self.statusBar().showMessage(f"✅ All {total_tools} tools executed successfully!")
            QMessageBox.information(
                self,
                "🎉 Batch Execution Complete",
                f"✅ All {total_tools} tools executed successfully!"
            )
        else:
            self.statusBar().showMessage(f"⚠️ Batch complete: {success_count} success, {failed_count} failed")
            QMessageBox.warning(
                self,
                "⚠️ Batch Execution Complete",
                f"Batch execution finished:\n\n"
                f"✅ Successful: {success_count}\n"
                f"❌ Failed: {failed_count}\n"
                f"📊 Total: {total_tools}\n\n"
                f"Check the History tab for details."
            )

    def update_history_table(self):
        """Update the command history table"""
        self.history_table.setRowCount(len(self.command_history))

        for row, entry in enumerate(reversed(self.command_history)):  # Latest first
            self.history_table.setItem(row, 0, QTableWidgetItem(entry['time']))
            self.history_table.setItem(row, 1, QTableWidgetItem(entry['tool']))

            # Status with color
            status_item = QTableWidgetItem(entry['status'])
            if entry['status'] == 'success':
                status_item.setStyleSheet("color: #4CAF50; font-weight: bold;")
            elif entry['status'] == 'failed':
                status_item.setStyleSheet("color: #F44336; font-weight: bold;")
            self.history_table.setItem(row, 2, status_item)

            self.history_table.setItem(row, 3, QTableWidgetItem(str(entry['return_code'])))
            self.history_table.setItem(row, 4, QTableWidgetItem(entry['duration']))

    def update_stats(self):
        """Update statistics display"""
        total_categories = len(self.categories)
        total_tools = sum(len(cat.items) for cat in self.categories.values())
        total_commands = len(self.command_history)

        if total_commands > 0:
            successful = sum(1 for cmd in self.command_history if cmd['status'] == 'success')
            failed = sum(1 for cmd in self.command_history if cmd['status'] == 'failed')
            success_rate = (successful / total_commands) * 100
        else:
            successful = failed = success_rate = 0

        stats_html = f"""
        <h3>📊 System Overview</h3>
        <p><strong>Categories loaded:</strong> {total_categories}</p>
        <p><strong>Tools available:</strong> {total_tools}</p>
        <br>
        <h3>📋 Command Statistics</h3>
        <p><strong>Total executed:</strong> {total_commands}</p>
        <p><strong>Successful:</strong> <span style='color: #4CAF50;'>{successful}</span></p>
        <p><strong>Failed:</strong> <span style='color: #F44336;'>{failed}</span></p>
        <p><strong>Success rate:</strong> {success_rate:.1f}%</p>
        <br>
        <h3>🚀 Multi-Selection Features</h3>
        <p>✅ <strong>Checkboxes:</strong> Select multiple tools</p>
        <p>🎯 <strong>Select All/None:</strong> Quick selection</p>
        <p>⚡ <strong>Batch Execution:</strong> Run tools in sequence</p>
        """

        if total_commands == 0:
            stats_html += "<br><p><em>Execute some tools to see detailed statistics!</em></p>"

        self.stats_content.setText(stats_html)

    def clear_history(self):
        """Clear command history"""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all command history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.command_history.clear()
            self.update_history_table()
            self.update_stats()
            self.statusBar().showMessage("🗑️ History cleared")

    def on_search_changed(self, text):
        """Handle search functionality"""
        if not text.strip():
            self.populate_categories()
            return

        # Switch to tools tab for search results
        self.tab_widget.setCurrentIndex(0)
        self.clear_content_layout()

        search_label = QLabel(f"🔍 Search results for: '{text}'")
        search_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        search_label.setProperty("class", "search-title")
        self.content_layout.addWidget(search_label)

        # Search through all tools
        results = self.config_manager.search_tools(text)

        if results:
            for tool in results[:10]:  # Limit to 10 results
                tool_widget = self.create_simple_tool_widget(tool)
                self.content_layout.addWidget(tool_widget)
        else:
            no_results = QLabel("No tools found.")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results.setProperty("class", "no-results")
            self.content_layout.addWidget(no_results)

        self.content_layout.addStretch()

    def create_simple_tool_widget(self, tool):
        """Create simple search result widget"""
        widget = QWidget()
        widget.setProperty("class", "search-result")

        layout = QHBoxLayout()

        # Tool info
        info_layout = QVBoxLayout()

        name = QLabel(tool.name)
        name.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(name)

        desc = QLabel(tool.description)
        desc.setProperty("class", "tool-description")
        info_layout.addWidget(desc)

        layout.addLayout(info_layout, 1)

        # Execute button
        exec_btn = QPushButton("Execute")
        exec_btn.setProperty("class", "success")
        exec_btn.clicked.connect(lambda: self.on_tool_selected(tool))
        layout.addWidget(exec_btn)

        widget.setLayout(layout)
        return widget

    def refresh_configuration(self):
        """Refresh configuration from GitHub"""
        self.statusBar().showMessage("🔄 Refreshing configuration...")

        try:
            self.categories = self.config_manager.get_config(force_update=True)
            self.populate_categories()
            self.update_stats()
            self.statusBar().showMessage("✅ Configuration refreshed")
            QMessageBox.information(self, "Success", "Configuration refreshed successfully!")

        except Exception as e:
            self.show_error(f"Refresh failed: {e}")

    def run_dependency_check(self):
        """Run dependency check"""
        try:
            success = self.dependency_checker.run_startup_check()
            if success:
                QMessageBox.information(self, "Dependency Check", "✅ All dependencies are satisfied!")
            else:
                QMessageBox.warning(self, "Dependency Check", "⚠️ Some dependencies are missing.")
        except Exception as e:
            self.show_error(f"Dependency check failed: {e}")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Arch Config Tool",
            "🔧 Arch Linux Configuration Tool v2.0\n\n"
            "A modern GUI tool for system configuration\n"
            "and maintenance of Arch-based distributions.\n\n"
            "Features:\n"
            "✅ Multi-Selection with Checkboxes\n"
            "🚀 Batch Tool Execution\n"
            "📋 Command History\n"
            "📊 Statistics & Analytics"
        )

    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
        print(f"❌ Error: {message}")

    def closeEvent(self, event):
        """Handle application close"""
        event.accept()
