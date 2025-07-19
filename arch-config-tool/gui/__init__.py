"""
GUI module for Arch Linux Configuration Tool
"""

from .main_window import MainWindow
from .styles.modern_theme import ModernTheme, apply_modern_theme_to_app
from .widgets.category_widget import CategoryWidget
from .widgets.modern_dialogs import DependencyCheckDialog, PasswordDialog, CommandExecutionDialog
from .workers.command_worker import CommandWorker

__all__ = [
    'MainWindow',
    'ModernTheme',
    'apply_modern_theme_to_app',
    'CategoryWidget',
    'DependencyCheckDialog',
    'PasswordDialog',
    'CommandExecutionDialog',
    'CommandWorker'
]
