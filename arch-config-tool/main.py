#!/usr/bin/env python3
"""
Arch Linux Configuration Tool - Main Entry Point
Qt6 Compatible Version
"""

import sys
import os

def main():
    """Main application entry point"""
    print("🚀 Starte Arch Config Tool...")

    try:
        print("📦 Importiere PyQt6...")
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont
        print("✅ PyQt6 erfolgreich importiert")

        print("📦 Importiere GUI Module...")
        from gui.main_window import MainWindow, apply_modern_theme_to_app
        print("✅ GUI Module erfolgreich importiert")

    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("💡 Stelle sicher, dass PyQt6 installiert ist: pip install PyQt6")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        sys.exit(1)

    # Qt6 Application erstellen (High-DPI ist standardmäßig aktiviert)
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Arch Linux Configuration Tool")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Arch Config Tools")

    print("🎨 Wende modernes Theme an...")
    # Apply modern theme
    apply_modern_theme_to_app(app)

    print("🏗️ Erstelle Hauptfenster...")
    # Create and show main window
    try:
        window = MainWindow()
        window.show()

        # Center window on screen
        screen = app.primaryScreen().geometry()
        window_rect = window.geometry()
        x = (screen.width() - window_rect.width()) // 2
        y = (screen.height() - window_rect.height()) // 2
        window.move(x, y)

        print("✅ Arch Config Tool erfolgreich gestartet!")
        print("🖱️ Fenster ist bereit für Interaktion")

        # Run application
        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Fehler beim Starten des Hauptfensters: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
