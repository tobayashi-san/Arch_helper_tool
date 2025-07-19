"""
Command execution worker thread
"""

from PyQt6.QtCore import QThread, pyqtSignal

class CommandWorker(QThread):
    """Worker thread für Befehlsausführung"""

    output_ready = pyqtSignal(str, str)  # output_type, text
    finished = pyqtSignal(int, str, str)  # return_code, stdout, stderr

    def __init__(self, command, sudo_password=None):
        super().__init__()
        self.command = command
        self.sudo_password = sudo_password
        self.should_stop = False

    def run(self):
        """Execute command in worker thread"""
        # ... komplette run Methode hier

    def stop(self):
        """Stop the worker thread"""
        self.should_stop = True
