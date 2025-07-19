"""
Dependency Checker
Verifies that required package managers are installed
"""

import subprocess
import shutil
import os
from typing import Dict, List, Tuple
from PyQt6.QtWidgets import QMessageBox, QWidget

class DependencyChecker:
    def __init__(self, parent_widget: QWidget = None):
        self.parent_widget = parent_widget
        self.required_tools = {
            'pacman': {
                'path': '/usr/bin/pacman',
                'description': 'Arch Linux Package Manager',
                'install_cmd': None  # pacman sollte immer da sein
            },
            'sudo': {
                'path': '/usr/bin/sudo',
                'description': 'Superuser privileges',
                'install_cmd': 'pacman -S --noconfirm sudo'
            }
        }

        self.optional_tools = {
            'flatpak': {
                'path': '/usr/bin/flatpak',
                'description': 'Universal Package Manager',
                'install_cmd': 'pacman -S --noconfirm flatpak'
            },
            'aur_helper': {
                'path': None,  # Wird dynamisch gesetzt
                'description': 'AUR Helper (yay oder paru)',
                'install_cmd': None  # AUR Helper müssen manuell installiert werden
            },
            'reflector': {
                'path': '/usr/bin/reflector',
                'description': 'Mirror ranking tool',
                'install_cmd': 'pacman -S --noconfirm reflector'
            }
        }

    def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH or at specific location"""
        # Erst in PATH suchen
        if shutil.which(command):
            return True

        # Dann spezifische Pfade prüfen
        tool_info = self.required_tools.get(command) or self.optional_tools.get(command)
        if tool_info and os.path.exists(tool_info['path']):
            return True

        return False

    def check_dependencies(self) -> Tuple[Dict[str, bool], Dict[str, bool]]:
        """Check if required and optional dependencies are available"""
        print("🔍 Überprüfe Abhängigkeiten...")

        required_status = {}
        optional_status = {}

        # Required Tools prüfen
        for tool, info in self.required_tools.items():
            exists = self.check_command_exists(tool)
            required_status[tool] = exists
            status = "✅" if exists else "❌"
            print(f"  {status} {tool}: {info['description']}")

        # Optional Tools prüfen (außer aur_helper)
        for tool, info in self.optional_tools.items():
            if tool == 'aur_helper':
                # Spezielle Behandlung für AUR Helper
                aur_helper = self.get_available_aur_helper()
                exists = aur_helper is not None
                optional_status[tool] = exists
                status = "✅" if exists else "⚠️ "
                helper_name = f" ({aur_helper})" if aur_helper else ""
                print(f"  {status} {tool}: {info['description']}{helper_name}")
            else:
                exists = self.check_command_exists(tool)
                optional_status[tool] = exists
                status = "✅" if exists else "⚠️ "
                print(f"  {status} {tool}: {info['description']}")

        return required_status, optional_status

    def get_missing_required(self, required_status: Dict[str, bool]) -> List[str]:
        """Get list of missing required dependencies"""
        return [tool for tool, exists in required_status.items() if not exists]

    def get_missing_optional(self, optional_status: Dict[str, bool]) -> List[str]:
        """Get list of missing optional dependencies"""
        return [tool for tool, exists in optional_status.items() if not exists]

    def install_missing_dependencies(self, missing: List[str]) -> bool:
        """Attempt to install missing dependencies"""
        if not missing:
            return True

        print(f"\n📦 Versuche fehlende Dependencies zu installieren: {', '.join(missing)}")

        installable = []
        manual_install = []

        # Sortiere nach installierbaren und manuellen
        for tool in missing:
            tool_info = self.required_tools.get(tool) or self.optional_tools.get(tool)
            if tool_info and tool_info['install_cmd']:
                installable.append((tool, tool_info['install_cmd']))
            else:
                manual_install.append(tool)

        # Installiere automatisch installierbare Tools
        success = True
        for tool, install_cmd in installable:
            try:
                print(f"  📥 Installiere {tool}...")
                result = subprocess.run(
                    install_cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 Minuten Timeout
                )

                if result.returncode == 0:
                    print(f"  ✅ {tool} erfolgreich installiert")
                else:
                    print(f"  ❌ Fehler beim Installieren von {tool}: {result.stderr}")
                    success = False

            except subprocess.TimeoutExpired:
                print(f"  ⏰ Timeout beim Installieren von {tool}")
                success = False
            except Exception as e:
                print(f"  ❌ Unexpected error installing {tool}: {e}")
                success = False

        # Zeige manuelle Installationsanweisungen
        if manual_install:
            self.show_manual_install_instructions(manual_install)

        return success and len(manual_install) == 0

    def show_manual_install_instructions(self, tools: List[str]):
        """Show manual installation instructions for tools that can't be auto-installed"""
        instructions = []

        for tool in tools:
            if tool == 'aur_helper':
                instructions.append(
                    "AUR Helper (yay ODER paru):\n\n"
                    "Option 1 - YAY installieren:\n"
                    "git clone https://aur.archlinux.org/yay.git\n"
                    "cd yay && makepkg -si\n\n"
                    "Option 2 - PARU installieren:\n"
                    "git clone https://aur.archlinux.org/paru.git\n"
                    "cd paru && makepkg -si\n\n"
                    "Hinweis: Nur einer der beiden AUR Helper ist erforderlich!"
                )
            elif tool == 'pacman':
                instructions.append(
                    "PACMAN fehlt - Das sollte auf Arch Linux nie passieren!\n"
                    "Vermutlich ist dies keine Arch-basierte Distribution."
                )

        if instructions and self.parent_widget:
            msg = QMessageBox(self.parent_widget)
            msg.setWindowTitle("Manuelle Installation erforderlich")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Einige Tools müssen manuell installiert werden:")
            msg.setDetailedText("\n\n".join(instructions))
            msg.exec()
        else:
            print("\n📋 Manuelle Installation erforderlich:")
            for instruction in instructions:
                print(f"\n{instruction}")

    def get_available_aur_helper(self) -> str:
        """Return the first available AUR helper"""
        for helper in ['yay', 'paru']:
            if self.check_command_exists(helper):
                return helper
        return None

    def check_arch_linux(self) -> bool:
        """Check if running on Arch Linux or Arch-based distribution"""
        try:
            # Check /etc/os-release
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    content = f.read().lower()
                    if any(distro in content for distro in ['arch', 'manjaro', 'endeavouros', 'artix']):
                        return True

            # Check if pacman exists (strong indicator)
            return self.check_command_exists('pacman')

        except Exception:
            return False

    def run_startup_check(self) -> bool:
        """Run complete startup dependency check with user interaction"""
        print("🚀 Starte Dependency Check...")

        # Prüfe ob Arch Linux
        if not self.check_arch_linux():
            if self.parent_widget:
                msg = QMessageBox(self.parent_widget)
                msg.setWindowTitle("Warnung")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Dieses Tool ist für Arch Linux entwickelt.\nIhre Distribution wurde nicht erkannt.")
                msg.setInformativeText("Möchten Sie trotzdem fortfahren?")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if msg.exec() != QMessageBox.StandardButton.Yes:
                    return False
            else:
                print("⚠️  Warnung: Keine Arch-basierte Distribution erkannt!")

        # Dependency Check
        required_status, optional_status = self.check_dependencies()
        missing_required = self.get_missing_required(required_status)
        missing_optional = self.get_missing_optional(optional_status)

        # Kritische Dependencies fehlen
        if missing_required:
            print(f"\n❌ Kritische Dependencies fehlen: {', '.join(missing_required)}")

            if self.parent_widget:
                msg = QMessageBox(self.parent_widget)
                msg.setWindowTitle("Fehlende Dependencies")
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Kritische Dependencies fehlen!")
                msg.setInformativeText(f"Fehlend: {', '.join(missing_required)}\n\nSollen diese installiert werden?")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                if msg.exec() == QMessageBox.StandardButton.Yes:
                    success = self.install_missing_dependencies(missing_required)
                    if not success:
                        return False
                else:
                    return False
            else:
                install = input(f"Fehlende Dependencies installieren? ({', '.join(missing_required)}) [y/N]: ")
                if install.lower() in ['y', 'yes', 'ja']:
                    success = self.install_missing_dependencies(missing_required)
                    if not success:
                        return False
                else:
                    return False

        # Optional Dependencies
        if missing_optional:
            print(f"\n⚠️  Optionale Dependencies fehlen: {', '.join(missing_optional)}")

            if self.parent_widget:
                msg = QMessageBox(self.parent_widget)
                msg.setWindowTitle("Optionale Dependencies")
                msg.setIcon(QMessageBox.Icon.Question)
                msg.setText("Optionale Dependencies fehlen.")
                msg.setInformativeText(f"Fehlend: {', '.join(missing_optional)}\n\nSollen diese installiert werden?")
                msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                if msg.exec() == QMessageBox.StandardButton.Yes:
                    self.install_missing_dependencies(missing_optional)
            else:
                install = input(f"Optionale Dependencies installieren? ({', '.join(missing_optional)}) [y/N]: ")
                if install.lower() in ['y', 'yes', 'ja']:
                    self.install_missing_dependencies(missing_optional)

        print("✅ Dependency Check abgeschlossen!")
        return True


# Test function
if __name__ == "__main__":
    checker = DependencyChecker()
    success = checker.run_startup_check()
    print(f"\nDependency Check {'erfolgreich' if success else 'fehlgeschlagen'}!")

    # Show available AUR helper
    aur_helper = checker.get_available_aur_helper()
    if aur_helper:
        print(f"Verfügbarer AUR Helper: {aur_helper}")
    else:
        print("Kein AUR Helper verfügbar")
