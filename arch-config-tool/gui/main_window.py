"""
Main application window
"""
import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QScrollArea, QLineEdit, QMessageBox,
    QTextEdit, QSplitter, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QFrame, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSignal as Signal
from PyQt6.QtGui import QFont, QPixmap, QPalette, QColor

from gui.widgets.category_widget import CategoryWidget
from gui.widgets.status_widget import StatusWidget
from gui.widgets.command_output_widget import CommandOutputWidget

class CommandExecutionThread(QThread):
    """Background thread for command execution"""

    progress_updated = Signal(int, str)  # progress, status
    command_finished = Signal(object)   # result
    output_received = Signal(str, str)   # type, text

    def __init__(self, tools_list, command_executor):
        super().__init__()
        self.tools_list = tools_list
        self.command_executor = command_executor
        self.results = []

    def run(self):
        """Execute tools in background"""
        total = len(self.tools_list)

        for i, tool in enumerate(self.tools_list):
            progress = int((i / total) * 100)
            self.progress_updated.emit(progress, f"Executing: {tool.name}")


            try:
                result = self.command_executor.execute_command(tool.command)
                self.results.append({
                    'tool': tool,
                    'result': result,
                    'success': result.status.value == "success"
                })

                # Emit output
                if result.stdout:
                    self.output_received.emit('stdout', result.stdout)
                if result.stderr:
                    self.output_received.emit('stderr', result.stderr)

            except Exception as e:
                self.results.append({
                    'tool': tool,
                    'result': None,
                    'success': False,
                    'error': str(e)
                })

        self.progress_updated.emit(100, "Completed")
        self.command_finished.emit(self.results)

class MainWindow(QMainWindow):
    """Überarbeitetes Hauptfenster mit einheitlichem Design"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔧 Arch Linux Configuration Tool v2.0")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        # State management
        self.command_history = []
        self.current_category = None
        self.execution_thread = None

        # Backend components
        self.init_backend()

        # Setup UI
        self.setup_ui()
        self.apply_theme()
        self.setup_status_bar()

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

            # Connect command executor signals
            self.command_executor.output_received.connect(self.on_command_output)

        except ImportError as e:
            self.show_error(f"Backend components failed to load: {e}")

        self.categories = {}

    def setup_ui(self):
        """Setup main user interface with improved layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel (sidebar + status)
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # Right panel (content + output)
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions (25% sidebar, 75% content)
        main_splitter.setSizes([350, 1050])
        main_splitter.setChildrenCollapsible(False)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_splitter)
        central_widget.setLayout(layout)

    def create_left_panel(self):
        """Create left sidebar panel"""
        panel = QFrame()
        panel.setObjectName("sidebar")
        panel.setMaximumWidth(400)
        panel.setMinimumWidth(300)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Header
        header = self.create_sidebar_header()
        layout.addWidget(header)

        # Search
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search tools and categories...")
        self.search_box.setObjectName("searchBox")
        self.search_box.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_box)

        # Categories list
        categories_label = QLabel("📂 Categories")
        categories_label.setObjectName("sectionTitle")
        layout.addWidget(categories_label)

        self.categories_list = QListWidget()
        self.categories_list.setObjectName("categoriesList")
        self.categories_list.itemClicked.connect(self.on_category_selected)
        layout.addWidget(self.categories_list)

        # Action buttons
        buttons_layout = self.create_action_buttons()
        layout.addLayout(buttons_layout)

        # Status widget (fallback if not available)
        if StatusWidget:
            self.status_widget = StatusWidget()
            layout.addWidget(self.status_widget)
        else:
            # Simple fallback status
            status_label = QLabel("Status: Ready")
            layout.addWidget(status_label)

        panel.setLayout(layout)
        return panel

    def create_sidebar_header(self):
        """Create elegant sidebar header"""
        header = QFrame()
        header.setObjectName("sidebarHeader")

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # App title
        title = QLabel("Arch Config Tool")
        title.setObjectName("appTitle")
        layout.addWidget(title)

        # Version info
        version = QLabel("v2.0 • System Configuration")
        version.setObjectName("appSubtitle")
        layout.addWidget(version)

        header.setLayout(layout)
        return header

    def create_action_buttons(self):
        """Create action buttons layout"""
        layout = QVBoxLayout()
        layout.setSpacing(8)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Configuration")
        refresh_btn.setObjectName("primaryButton")
        refresh_btn.clicked.connect(self.refresh_configuration)
        layout.addWidget(refresh_btn)

        # Dependency check button
        deps_btn = QPushButton("🔍 Check Dependencies")
        deps_btn.setObjectName("secondaryButton")
        deps_btn.clicked.connect(self.run_dependency_check)
        layout.addWidget(deps_btn)

        return layout

    def create_right_panel(self):
        """Create right content panel with vertical splitter"""
        # Vertical splitter for content and output
        right_splitter = QSplitter(Qt.Orientation.Vertical)

        # Top: Main content with tabs
        content_area = self.create_content_area()
        right_splitter.addWidget(content_area)

        # Bottom: Command output (initially hidden) - with fallback
        if CommandOutputWidget:
            self.output_widget = CommandOutputWidget()
        else:
            # Simple fallback output widget
            self.output_widget = QTextEdit()
            self.output_widget.setReadOnly(True)
            self.output_widget.setFont(QFont("Consolas", 10))

        self.output_widget.setMaximumHeight(250)
        self.output_widget.hide()
        right_splitter.addWidget(self.output_widget)

        # Set proportions (80% content, 20% output when visible)
        right_splitter.setSizes([650, 150])

        return right_splitter

    def create_content_area(self):
        """Create main content area with tabs"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("mainTabs")

        # Tools tab
        self.tools_tab = self.create_tools_tab()
        self.tab_widget.addTab(self.tools_tab, "🛠️ Tools")

        # History tab
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📋 History")

        return self.tab_widget

    def create_tools_tab(self):
        """Create tools tab with welcome screen"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("toolsScrollArea")

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(20)

        self.content_widget.setLayout(self.content_layout)
        scroll_area.setWidget(self.content_widget)

        return scroll_area


    def create_history_tab(self):
        """Create command history tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()

        header_label = QLabel("📋 Command History")
        header_label.setObjectName("tabTitle")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # Clear button
        clear_btn = QPushButton("🗑️ Clear History")
        clear_btn.setObjectName("dangerButton")
        clear_btn.clicked.connect(self.clear_history)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setObjectName("historyTable")
        self.setup_history_table()
        layout.addWidget(self.history_table)

        widget.setLayout(layout)
        return widget

    def setup_history_table(self):
        """Setup history table with proper styling"""
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Time", "Tool", "Category", "Status", "Exit Code", "Duration"
        ])

        # Configure columns
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        # Styling
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)



    def setup_status_bar(self):
        """Setup enhanced status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Connection status
        self.connection_label = QLabel("●")
        self.connection_label.setToolTip("Configuration loaded")
        self.status_bar.addPermanentWidget(self.connection_label)

    def apply_theme(self):
        """Apply unified theme from external stylesheet"""
        try:
            # Pfad der aktuellen Python-Datei (main_window.py)
            base_dir = os.path.dirname(os.path.abspath(__file__))

            # Relativer Pfad zur styles.css
            css_path = os.path.join(base_dir, "styles", "styles.css")

            with open(css_path, "r") as f:
                self.setStyleSheet(f.read())

        except Exception as e:
            print(f"Failed to load stylesheet: {e}")

    def load_configuration(self):
        """Load configuration and update UI"""
        self.update_status("Loading configuration...", show_progress=True)

        try:
            self.categories = self.config_manager.get_config()
            self.populate_categories()

            # Update status
            total_tools = sum(len(cat.items) for cat in self.categories.values())
            self.update_status(f"Loaded {len(self.categories)} categories with {total_tools} tools")
            self.connection_label.setToolTip("Configuration loaded successfully")

        except Exception as e:
            self.show_error(f"Failed to load configuration: {e}")
            self.update_status("Configuration load failed")
            self.connection_label.setToolTip("Configuration load failed")

    def populate_categories(self):
        """Populate categories list with improved styling"""
        self.categories_list.clear()

        for category in self.config_manager.get_categories():
            item = QListWidgetItem()
            item.setText(f"{category.icon}  {category.name}")
            item.setData(Qt.ItemDataRole.UserRole, category.id)
            item.setToolTip(f"{category.description}\n{len(category.items)} tools available")
            self.categories_list.addItem(item)

        # Auto-select first category
        if self.categories_list.count() > 0:
            self.categories_list.setCurrentRow(0)
            self.on_category_selected(self.categories_list.item(0))

    def on_category_selected(self, item):
        """Handle category selection with improved UX"""
        category_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_category = category_id

        if category_id in self.categories:
            category = self.categories[category_id]
            self.show_category_tools(category)
            self.update_status(f"Viewing {category.name} - {len(category.items)} tools")

    def show_category_tools(self, category):
        """Display category tools with enhanced UI"""
        # Switch to tools tab
        self.tab_widget.setCurrentIndex(0)

        # Clear current content
        self.clear_content_layout()

        # Create category widget
        category_widget = CategoryWidget(category)
        category_widget.tool_selected.connect(self.execute_single_tool)
        category_widget.tools_selected.connect(self.execute_multiple_tools)

        self.content_layout.addWidget(category_widget)

    def clear_content_layout(self):
        """Safely clear content layout"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def execute_single_tool(self, tool):
        """Execute single tool with confirmation"""
        if not self.confirm_execution([tool]):
            return

        self.show_output_widget()
        self.output_widget.clear()

        # Execute in background
        self.execution_thread = CommandExecutionThread([tool], self.command_executor)
        self.execution_thread.progress_updated.connect(self.update_execution_progress)
        self.execution_thread.command_finished.connect(self.on_execution_finished)
        self.execution_thread.output_received.connect(self.on_command_output)
        self.execution_thread.start()

    def execute_multiple_tools(self, tools_list):
        """Execute multiple tools with enhanced progress tracking"""
        if not tools_list or not self.confirm_execution(tools_list):
            return

        self.show_output_widget()
        self.output_widget.clear()

        # Execute in background
        self.execution_thread = CommandExecutionThread(tools_list, self.command_executor)
        self.execution_thread.progress_updated.connect(self.update_execution_progress)
        self.execution_thread.command_finished.connect(self.on_execution_finished)
        self.execution_thread.output_received.connect(self.on_command_output)
        self.execution_thread.start()

    def confirm_execution(self, tools_list):
        """Show execution confirmation dialog"""
        if len(tools_list) == 1:
            title = "Execute Tool"
            text = f"Execute '{tools_list[0].name}'?"
            info = f"Command: {tools_list[0].command}"
        else:
            title = "Execute Multiple Tools"
            text = f"Execute {len(tools_list)} selected tools?"
            tools_text = "\n".join([f"• {tool.name}" for tool in tools_list[:5]])
            if len(tools_list) > 5:
                tools_text += f"\n... and {len(tools_list) - 5} more tools"
            info = f"Tools to execute:\n\n{tools_text}"

        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(text)
        msg.setInformativeText(info)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)

        return msg.exec() == QMessageBox.StandardButton.Yes

    def update_execution_progress(self, progress, status):
        """Update execution progress"""
        self.progress_bar.setValue(progress)
        self.progress_bar.show()
        self.update_status(status)

    def on_execution_finished(self, results):
        """Handle execution completion"""
        self.progress_bar.hide()

        # Process results
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)

        # Add to history
        for result_data in results:
            self.add_to_history(result_data)

        # Update UI
        self.update_history_table()


        # Show completion message
        if success_count == total_count:
            self.update_status(f"✅ All {total_count} tools executed successfully")
            if total_count > 1:
                self.show_success(f"Batch execution completed!\n\n✅ {success_count}/{total_count} tools executed successfully")
        else:
            failed_count = total_count - success_count
            self.update_status(f"⚠️ Completed with {failed_count} failures")
            self.show_warning(f"Batch execution completed with errors!\n\n✅ Successful: {success_count}\n❌ Failed: {failed_count}\n📊 Total: {total_count}")

    def show_output_widget(self):
        """Show command output widget"""
        self.output_widget.show()

    def add_to_history(self, result_data):
        """Add execution result to history"""
        from datetime import datetime

        tool = result_data['tool']
        result = result_data.get('result')
        success = result_data['success']

        history_entry = {
            'time': datetime.now().strftime("%H:%M:%S"),
            'tool': tool.name,
            'category': getattr(tool, 'category', 'Unknown'),
            'status': 'success' if success else 'failed',
            'return_code': result.return_code if result else -1,
            'duration': f"{result.execution_time:.1f}s" if result else "0.0s",
            'command': tool.command
        }

        self.command_history.append(history_entry)

    def update_history_table(self):
        """Update history table with improved styling"""
        self.history_table.setRowCount(len(self.command_history))

        for row, entry in enumerate(reversed(self.command_history)):  # Latest first
            # Time
            self.history_table.setItem(row, 0, QTableWidgetItem(entry['time']))

            # Tool name
            self.history_table.setItem(row, 1, QTableWidgetItem(entry['tool']))

            # Category
            self.history_table.setItem(row, 2, QTableWidgetItem(entry['category']))

            # Status with styling
            status_item = QTableWidgetItem(entry['status'].title())
            if entry['status'] == 'success':
                status_item.setForeground(QColor("#10b981"))
            else:
                status_item.setForeground(QColor("#ef4444"))
            self.history_table.setItem(row, 3, status_item)

            # Exit code
            self.history_table.setItem(row, 4, QTableWidgetItem(str(entry['return_code'])))

            # Duration
            self.history_table.setItem(row, 5, QTableWidgetItem(entry['duration']))

    def on_search_changed(self, text):
        """Enhanced search functionality"""
        if not text.strip():
            self.populate_categories()
            return

        # Switch to tools tab and show search results
        self.tab_widget.setCurrentIndex(0)
        self.clear_content_layout()

        # Search header
        search_header = self.create_search_header(text)
        self.content_layout.addWidget(search_header)

        # Search through all tools
        results = self.config_manager.search_tools(text)

        if results:
            # Group results by category
            from collections import defaultdict
            grouped_results = defaultdict(list)

            for tool in results:
                category_name = "Unknown"
                for cat in self.categories.values():
                    if any(t.name == tool.name for t in cat.items):
                        category_name = cat.name
                        break
                grouped_results[category_name].append(tool)

            # Display grouped results
            for category_name, tools in grouped_results.items():
                category_header = QLabel(f"📂 {category_name} ({len(tools)} results)")
                self.content_layout.addWidget(category_header)

                for tool in tools[:5]:  # Limit results per category
                    tool_widget = self.create_search_result_widget(tool)
                    self.content_layout.addWidget(tool_widget)

        else:
            # No results message
            no_results = self.create_no_results_widget(text)
            self.content_layout.addWidget(no_results)

        self.content_layout.addStretch()
        self.update_status(f"Search: '{text}' - {len(results)} results found")

    def create_search_header(self, query):
        """Create search results header"""
        header = QFrame()
        header.setObjectName("searchHeader")

        layout = QVBoxLayout()

        title = QLabel(f"🔍 Search Results for '{query}'")
        layout.addWidget(title)

        subtitle = QLabel("Tools matching your search criteria")
        layout.addWidget(subtitle)

        header.setLayout(layout)
        return header

    def create_search_result_widget(self, tool):
        """Create search result item"""
        widget = QFrame()
        widget.setObjectName("searchResult")

        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Tool info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        name_label = QLabel(tool.name)
        info_layout.addWidget(name_label)

        desc_label = QLabel(tool.description)
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)

        layout.addLayout(info_layout, 1)

        # Execute button
        exec_btn = QPushButton("Execute")
        exec_btn.setObjectName("successButton")
        exec_btn.setFixedSize(80, 32)
        exec_btn.clicked.connect(lambda: self.execute_single_tool(tool))
        layout.addWidget(exec_btn)

        widget.setLayout(layout)
        return widget

    def create_no_results_widget(self, query):
        """Create no results widget"""
        widget = QFrame()
        widget.setObjectName("noResults")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("No tools found")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel(f"No tools match '{query}'. Try a different search term.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        widget.setLayout(layout)
        return widget

    def refresh_configuration(self):
        """Refresh configuration with better UX"""
        self.update_status("Refreshing configuration...", show_progress=True)
        self.connection_label.setToolTip("Refreshing configuration...")

        try:
            self.categories = self.config_manager.get_config(force_update=True)
            self.populate_categories()


            total_tools = sum(len(cat.items) for cat in self.categories.values())
            self.update_status(f"Configuration refreshed - {len(self.categories)} categories, {total_tools} tools")
            self.connection_label.setToolTip("Configuration refreshed successfully")

            self.show_success("Configuration refreshed successfully!")

        except Exception as e:
            self.show_error(f"Failed to refresh configuration: {e}")
            self.update_status("Configuration refresh failed")
            self.connection_label.setToolTip("Configuration refresh failed")

    def run_dependency_check(self):
        """Run dependency check with improved feedback"""
        self.update_status("Running dependency check...", show_progress=True)

        try:
            success = self.dependency_checker.run_startup_check()

            if success:
                self.show_success("✅ All dependencies are satisfied!\n\nYour system is ready to use the Arch Config Tool.")
                self.update_status("Dependency check passed")
            else:
                self.show_warning("⚠️ Some dependencies are missing.\n\nSome features may not work properly. Please install the missing dependencies.")
                self.update_status("Dependency check failed")

        except Exception as e:
            self.show_error(f"Dependency check failed: {e}")
            self.update_status("Dependency check error")

    def clear_history(self):
        """Clear command history with confirmation"""
        if not self.command_history:
            self.show_info("No history to clear.")
            return

        reply = QMessageBox.question(
            self,
            "Clear History",
            f"Are you sure you want to clear all {len(self.command_history)} history entries?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.command_history.clear()
            self.update_history_table()

            self.update_status("Command history cleared")
            self.show_success("Command history cleared successfully!")

    def on_command_output(self, output_type, text):
        """Handle command output"""
        if hasattr(self, 'output_widget') and self.output_widget.isVisible():
            self.output_widget.append_output(output_type, text)

    def update_status(self, message, show_progress=False):
        """Update status bar message"""
        self.status_label.setText(message)

        if show_progress:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.progress_bar.show()
        else:
            self.progress_bar.hide()

    def show_success(self, message):
        """Show success message"""
        QMessageBox.information(self, "Success", message)

    def show_warning(self, message):
        """Show warning message"""
        QMessageBox.warning(self, "Warning", message)

    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message):
        """Show info message"""
        QMessageBox.information(self, "Information", message)

    def closeEvent(self, event):
        """Handle application close"""
        # Stop any running execution thread
        if self.execution_thread and self.execution_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Exit Application",
                "A command is currently running. Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

            # Terminate execution thread
            self.execution_thread.terminate()
            self.execution_thread.wait(3000)  # Wait up to 3 seconds

        event.accept()
