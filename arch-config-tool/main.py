#!/usr/bin/env python3
"""
Arch Linux Configuration Tool - Main Entry Point
With startup dependency check
"""

import sys
import os

def run_dependency_check():
    """Run dependency check at startup"""
    try:
        from core.dependency_check import DependencyChecker

        print("🔍 Running dependency check...")
        checker = DependencyChecker()
        success = checker.run_startup_check()

        if not success:
            print("❌ Dependency check failed. Some features may not work properly.")
            return False
        else:
            print("✅ All dependencies satisfied!")
            return True

    except Exception as e:
        print(f"⚠️ Dependency check error: {e}")
        return True  # Continue anyway

def main():
    """Main application entry point"""
    print("🚀 Starting Arch Config Tool...")

    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        sys.exit(1)

    try:
        # Import Qt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        print("✅ PyQt6 imported successfully")

        # Import main window
        from gui.main_window import MainWindow
        print("✅ Main window imported successfully")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install dependencies: pip install PyQt6 requests PyYAML")
        sys.exit(1)

    # Run dependency check before starting GUI
    dependency_success = run_dependency_check()

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Arch Config Tool")
    app.setApplicationVersion("2.0")

    # Apply styling
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
            font-family: system-ui, -apple-system, sans-serif;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton[class="success"] {
            background-color: #4CAF50;
        }
        QPushButton[class="success"]:hover {
            background-color: #45a049;
        }
        QPushButton[class="warning"] {
            background-color: #FF9800;
        }
        QPushButton[class="warning"]:hover {
            background-color: #F57C00;
        }
        QPushButton[class="secondary"] {
            background-color: transparent;
            color: #2196F3;
            border: 2px solid #2196F3;
        }
        QPushButton[class="secondary"]:hover {
            background-color: #2196F3;
            color: white;
        }
        QListWidget {
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
            padding: 5px;
        }
        QListWidget::item {
            padding: 10px;
            border-radius: 4px;
            margin: 2px 0px;
        }
        QListWidget::item:hover {
            background-color: #e3f2fd;
        }
        QListWidget::item:selected {
            background-color: #2196F3;
            color: white;
        }
        QLineEdit {
            padding: 8px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 12px;
        }
        QLineEdit:focus {
            border-color: #2196F3;
        }
        QCheckBox {
            color: #212121;
            background-color: transparent;
            spacing: 6px;
        }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border: 2px solid #BDBDBD;
            border-radius: 4px;
            background-color: white;
        }
        QCheckBox::indicator:hover {
            border-color: #2196F3;
            background-color: #f0f8ff;
        }
        QCheckBox::indicator:checked {
            background-color: #2196F3;
            border-color: #2196F3;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
        }
        QWidget[class="tool-card"] {
            background-color: white;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin: 5px;
            padding: 10px;
            color: #212121;
        }
        QWidget[class="tool-card"]:hover {
            border-color: #2196F3;
            background-color: #f8fcff;
        }
        QWidget[class="tool-card-selected"] {
            border-color: #2196F3;
            background-color: #e3f2fd;
            border-width: 3px;
        }
        QLabel {
            color: #212121;
            background-color: transparent;
        }
        QLabel[class="tool-description"] {
            color: #666666;
            background-color: transparent;
        }
        QLabel[class="command-display"] {
            color: #888888;
            background-color: #f5f5f5;
            padding: 4px;
            border-radius: 3px;
        }
    """)

    try:
        # Create and show main window
        window = MainWindow()

        # Pass dependency check result to window
        window.dependency_check_passed = dependency_success

        window.show()
        print("✅ Main window created successfully")

        # Center window
        screen = app.primaryScreen().geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        window.move(x, y)

        print("✅ Arch Config Tool started successfully!")

        # Run application
        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Failed to start: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
