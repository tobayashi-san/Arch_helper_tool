"""
Command Executor - Korrigiert mit verbessertem sudo-Handling und Lock-Detection
Behebt Probleme mit Passwort-Eingabe und Pacman-Lock-Detection
"""

import subprocess
import threading
import queue
import time
import os
import signal
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

from PyQt6.QtWidgets import QInputDialog, QLineEdit

class CommandStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NEEDS_PASSWORD = "needs_password"
    LOCKED = "locked"

@dataclass
class CommandResult:
    """Result of command execution"""
    command: str
    status: CommandStatus
    return_code: int
    stdout: str
    stderr: str
    execution_time: float

class CommandExecutor(QObject):
    """Verbesserter Command Executor mit sudo-Handling und Lock-Detection"""

    # Qt Signals
    output_received = pyqtSignal(str, str)  # (output_type, text)
    command_started = pyqtSignal(str)  # command
    command_finished = pyqtSignal(object)  # CommandResult
    password_required = pyqtSignal()  # Passwort benötigt

    def __init__(self, output_callback: Optional[Callable] = None):
        super().__init__()
        self.output_callback = output_callback
        self.current_process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.should_cancel = False
        self.sudo_password = None
        self.password_attempts = 0
        self.max_password_attempts = 3

    def is_command_safe(self, command: str) -> bool:
        """Erweiterte Command Safety Check"""
        dangerous_patterns = [
            'rm -rf /', 'dd if=', 'mkfs.', 'fdisk', 'parted',
            ':(){ :|:& };:', 'chmod -R 777 /', 'format', 'erase'
        ]

        command_lower = command.lower()
        return not any(pattern in command_lower for pattern in dangerous_patterns)

    def check_pacman_lock(self) -> bool:
        """Prüfe ob Pacman gesperrt ist"""
        lock_file = "/var/lib/pacman/db.lck"
        return os.path.exists(lock_file)

    def remove_pacman_lock(self) -> bool:
        """Entferne Pacman Lock nach Bestätigung"""
        try:
            if self.check_pacman_lock():
                # Prüfe ob wirklich kein Pacman läuft
                result = subprocess.run(['pgrep', '-x', 'pacman'],
                                      capture_output=True, timeout=5)

                if result.returncode == 0:
                    # Pacman läuft tatsächlich
                    return False

                # Lock-Datei entfernen
                subprocess.run(['sudo', 'rm', '-f', '/var/lib/pacman/db.lck'],
                             check=True, timeout=10)
                return True
        except Exception as e:
            print(f"Fehler beim Entfernen des Pacman-Locks: {e}")
            return False

        return True

    def get_sudo_password(self) -> Optional[str]:
        """Hole sudo-Passwort vom Benutzer"""
        if self.sudo_password and self.password_attempts < self.max_password_attempts:
            return self.sudo_password

        # Passwort-Dialog anzeigen
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()

        if app:
            password, ok = QInputDialog.getText(
                None,
                "Sudo Password Required",
                "Please enter your sudo password:",
                echo=QLineEdit.EchoMode.Password
            )

            if ok and password:
                self.sudo_password = password
                self.password_attempts = 0
                return password

        return None

    def validate_sudo_password(self, password: str) -> bool:
        """Validiere sudo-Passwort"""
        try:
            # Teste Passwort mit einem harmlosen sudo-Befehl
            process = subprocess.Popen(
                ['sudo', '-S', 'true'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(input=password + '\n', timeout=5)

            if process.returncode == 0:
                return True
            else:
                self.password_attempts += 1
                return False

        except Exception:
            return False

    def prepare_command_with_sudo(self, command: str) -> tuple[list, str]:
        """Bereite Befehl mit sudo vor"""
        # Prüfe ob sudo benötigt wird
        needs_sudo = command.strip().startswith('sudo')

        if needs_sudo:
            # Entferne 'sudo' vom Anfang und bereite für stdin vor
            cmd_without_sudo = command.strip()[4:].strip()
            cmd_list = ['sudo', '-S'] + cmd_without_sudo.split()

            # Hole Passwort
            password = self.get_sudo_password()
            if not password:
                return None, "Password required but not provided"

            # Validiere Passwort
            if not self.validate_sudo_password(password):
                if self.password_attempts >= self.max_password_attempts:
                    self.sudo_password = None  # Reset cached password
                return None, "Invalid password"

            return cmd_list, password + '\n'
        else:
            return command.split(), None

    def execute_command(self, command: str, use_sudo: bool = True, timeout: int = 300) -> CommandResult:
        """Execute a system command safely mit verbessertem sudo-Handling"""
        start_time = time.time()

        # Basic safety check
        if not self.is_command_safe(command):
            return CommandResult(
                command=command,
                status=CommandStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr="Command blocked for safety reasons",
                execution_time=0
            )

        # Prüfe Pacman Lock bei Pacman-Befehlen
        if 'pacman' in command.lower():
            if self.check_pacman_lock():
                # Frage Benutzer ob Lock entfernt werden soll
                from PyQt6.QtWidgets import QApplication
                app = QApplication.instance()

                if app:
                    reply = QMessageBox.question(
                        None,
                        "Pacman Database Locked",
                        "The pacman database is locked. This usually means another package manager is running.\n\n"
                        "Do you want to remove the lock file? (Only do this if you're sure no other package manager is running)",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )

                    if reply == QMessageBox.StandardButton.Yes:
                        if not self.remove_pacman_lock():
                            return CommandResult(
                                command=command,
                                status=CommandStatus.LOCKED,
                                return_code=-1,
                                stdout="",
                                stderr="Could not remove pacman lock - another package manager may be running",
                                execution_time=time.time() - start_time
                            )
                    else:
                        return CommandResult(
                            command=command,
                            status=CommandStatus.LOCKED,
                            return_code=-1,
                            stdout="",
                            stderr="Command cancelled - pacman database is locked",
                            execution_time=time.time() - start_time
                        )

        # Prepare command
        cmd_result = self.prepare_command_with_sudo(command)
        if cmd_result[0] is None:
            return CommandResult(
                command=command,
                status=CommandStatus.NEEDS_PASSWORD,
                return_code=-1,
                stdout="",
                stderr=cmd_result[1],
                execution_time=time.time() - start_time
            )

        cmd_list, password_input = cmd_result

        # Emit started signal
        self.command_started.emit(command)

        try:
            self.is_running = True
            self.should_cancel = False

            # Start process
            self.current_process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid if os.name != 'nt' else None  # Für ordentliches Cleanup
            )

            # Send password if needed
            if password_input:
                try:
                    self.current_process.stdin.write(password_input)
                    self.current_process.stdin.flush()
                except Exception as e:
                    print(f"Error sending password: {e}")

            # Read output in real-time
            stdout_lines = []
            stderr_lines = []
            stdout_queue = queue.Queue()
            stderr_queue = queue.Queue()

            def read_stdout():
                try:
                    for line in iter(self.current_process.stdout.readline, ''):
                        if line:
                            stdout_queue.put(line.rstrip())
                        if self.should_cancel:
                            break
                except Exception as e:
                    stdout_queue.put(f"Error reading stdout: {e}")
                finally:
                    stdout_queue.put(None)

            def read_stderr():
                try:
                    for line in iter(self.current_process.stderr.readline, ''):
                        if line:
                            stderr_queue.put(line.rstrip())
                        if self.should_cancel:
                            break
                except Exception as e:
                    stderr_queue.put(f"Error reading stderr: {e}")
                finally:
                    stderr_queue.put(None)

            # Start reader threads
            stdout_thread = threading.Thread(target=read_stdout, daemon=True)
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stdout_thread.start()
            stderr_thread.start()

            # Monitor output
            stdout_finished = False
            stderr_finished = False

            while not (stdout_finished and stderr_finished):
                if self.should_cancel:
                    self.terminate_process()
                    break

                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    self.terminate_process()
                    return CommandResult(
                        command=command,
                        status=CommandStatus.FAILED,
                        return_code=-1,
                        stdout='\n'.join(stdout_lines),
                        stderr='\n'.join(stderr_lines) + '\nTimeout reached',
                        execution_time=time.time() - start_time
                    )

                # Read stdout
                try:
                    line = stdout_queue.get_nowait()
                    if line is None:
                        stdout_finished = True
                    else:
                        stdout_lines.append(line)
                        self.output_received.emit('stdout', line)
                        if self.output_callback:
                            self.output_callback('stdout', line)
                except queue.Empty:
                    pass

                # Read stderr
                try:
                    line = stderr_queue.get_nowait()
                    if line is None:
                        stderr_finished = True
                    else:
                        stderr_lines.append(line)
                        self.output_received.emit('stderr', line)
                        if self.output_callback:
                            self.output_callback('stderr', line)
                except queue.Empty:
                    pass

                time.sleep(0.01)

            # Wait for process to complete
            if self.current_process:
                return_code = self.current_process.wait()
            else:
                return_code = -1

            # Determine status
            if self.should_cancel:
                status = CommandStatus.CANCELLED
            elif return_code == 0:
                status = CommandStatus.SUCCESS
            else:
                status = CommandStatus.FAILED

            # Create result
            result = CommandResult(
                command=command,
                status=status,
                return_code=return_code,
                stdout='\n'.join(stdout_lines),
                stderr='\n'.join(stderr_lines),
                execution_time=time.time() - start_time
            )

            # Emit finished signal
            self.command_finished.emit(result)
            return result

        except Exception as e:
            error_result = CommandResult(
                command=command,
                status=CommandStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr=f"Execution error: {e}",
                execution_time=time.time() - start_time
            )
            self.command_finished.emit(error_result)
            return error_result

        finally:
            self.is_running = False
            self.current_process = None

    def terminate_process(self):
        """Proper process termination"""
        if self.current_process:
            try:
                if os.name != 'nt':
                    # Linux/Unix: Terminate process group
                    os.killpg(os.getpgid(self.current_process.pid), signal.SIGTERM)
                    time.sleep(1)
                    if self.current_process.poll() is None:
                        os.killpg(os.getpgid(self.current_process.pid), signal.SIGKILL)
                else:
                    # Windows
                    self.current_process.terminate()
                    time.sleep(1)
                    if self.current_process.poll() is None:
                        self.current_process.kill()
            except Exception as e:
                print(f"Error terminating process: {e}")

    def cancel_current_command(self):
        """Cancel the currently running command"""
        if self.is_running:
            self.should_cancel = True
            self.terminate_process()

    def check_sudo_available(self) -> bool:
        """Check if sudo is available"""
        try:
            result = subprocess.run(['which', 'sudo'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def reset_sudo_cache(self):
        """Reset cached sudo password"""
        self.sudo_password = None
        self.password_attempts = 0

    def preauth_sudo(self) -> bool:
        """Pre-authenticate sudo to avoid password prompts during execution"""
        try:
            password = self.get_sudo_password()
            if not password:
                return False

            # Extend sudo timeout
            process = subprocess.Popen(
                ['sudo', '-S', '-v'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate(input=password + '\n', timeout=10)

            if process.returncode == 0:
                print("✅ Sudo pre-authentication successful")
                return True
            else:
                print(f"❌ Sudo pre-authentication failed: {stderr}")
                return False

        except Exception as e:
            print(f"❌ Sudo pre-authentication error: {e}")
            return False

class InteractiveCommandExecutor(CommandExecutor):
    """Erweiterte Version mit interaktiver Eingabe"""

    user_input_required = pyqtSignal(str)  # Prompt text

    def __init__(self, output_callback: Optional[Callable] = None):
        super().__init__(output_callback)
        self.pending_input = queue.Queue()

    def send_user_input(self, input_text: str):
        """Send user input to running process"""
        if self.current_process and self.is_running:
            try:
                self.current_process.stdin.write(input_text + '\n')
                self.current_process.stdin.flush()
            except Exception as e:
                print(f"Error sending user input: {e}")

    def detect_input_prompt(self, line: str) -> bool:
        """Detect if line is asking for user input"""
        prompts = [
            'password:', '[y/n]', '[Y/n]', 'continue?',
            'proceed?', 'confirm', 'enter', 'input'
        ]

        line_lower = line.lower()
        return any(prompt in line_lower for prompt in prompts)

class CommandQueue:
    """Queue für die Ausführung mehrerer Commands"""

    def __init__(self, executor: CommandExecutor):
        self.executor = executor
        self.queue = []
        self.is_running = False
        self.current_index = 0

    def add_command(self, command: str, description: str = ""):
        """Add command to queue"""
        self.queue.append({
            'command': command,
            'description': description,
            'status': 'pending',
            'result': None
        })

    def execute_queue(self):
        """Execute all commands in queue"""
        if self.is_running:
            return False

        self.is_running = True
        self.current_index = 0

        for i, cmd_info in enumerate(self.queue):
            if not self.is_running:  # Queue was cancelled
                break

            self.current_index = i
            cmd_info['status'] = 'running'

            result = self.executor.execute_command(cmd_info['command'])
            cmd_info['result'] = result

            if result.status == CommandStatus.SUCCESS:
                cmd_info['status'] = 'completed'
            else:
                cmd_info['status'] = 'failed'
                # Optionally stop queue on failure
                break

        self.is_running = False
        return True

    def cancel_queue(self):
        """Cancel queue execution"""
        self.is_running = False
        self.executor.cancel_current_command()

    def get_progress(self) -> tuple[int, int]:
        """Get current progress (completed, total)"""
        completed = sum(1 for cmd in self.queue if cmd['status'] in ['completed', 'failed'])
        return completed, len(self.queue)

# Export classes
__all__ = [
    'CommandExecutor', 'CommandResult', 'CommandStatus',
    'InteractiveCommandExecutor', 'CommandQueue'
]
