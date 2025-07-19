#!/usr/bin/env python3
"""
Arch Linux Configuration Tool
Main Entry Point mit Debug
"""

import sys
import os

def main():
    """Hauptfunktion mit Debug-Output"""
    print("🚀 Starte Arch Config Tool...")

    try:
        print("📦 Importiere PyQt6...")
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 erfolgreich importiert")

        print("📦 Importiere GUI Module...")
        from gui.main_window import MainWindow
        print("✅ MainWindow erfolgreich importiert")

        print("🖥️  Erstelle QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("Arch Config Tool")
        app.setApplicationVersion("1.0.0")
        print("✅ QApplication erstellt")

        print("🏠 Erstelle MainWindow...")
        window = MainWindow()
        print("✅ MainWindow erstellt")

        print("👁️  Zeige Fenster...")
        window.show()
        print("✅ Fenster angezeigt")

        print("🔄 Starte Event Loop...")
        sys.exit(app.exec())

    except ImportError as e:
        print(f"❌ Import Fehler: {e}")
        print("💡 Mögliche Lösungen:")
        print("   - pip install PyQt6")
        print("   - pip install PyYAML")
        print("   - Überprüfe Python-Pfad")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
