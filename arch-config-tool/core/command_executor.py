"""
Command Executor
Safely executes system commands with sudo and real-time output
"""

import subprocess
import threading
import queue
import signal
import os
import time
from typing import Optional, Callable, Tuple, Dict
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QThread

class CommandStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

@dataclass
class CommandResult:
    """Result of command execution"""
    command: str
    status: CommandStatus
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    start_time: float
    end_time: float

class CommandExecutor(QObject):
    """Thread-safe command executor with Qt signals"""

    # Qt Signals für GUI Integration
    output_received = pyqtSignal(str, str)  # (output_type, text)
    command_started = pyqtSignal(str)  # command
    command_finished = pyqtSignal(object)  # CommandResult
    progress_updated = pyqtSignal(str)  # status_message

    def __init__(self, output_callback: Optional[Callable] = None):
        super().__init__()
        self.output_callback = output_callback
        self.current_process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.should_cancel = False

        # Command history
        self.command_history: list[CommandResult] = []
        self.max_history = 100

        # Security settings
        self.allowed_commands = {
            'pacman', 'sudo', 'flatpak', 'yay', 'paru',
            'reflector', 'systemctl', 'mkdir', 'cp', 'mv', 'rm',
            'echo', 'cat', 'ls', 'whoami', 'which', 'test', 'true', 'false'
        }
        self.dangerous_patterns = [
            'rm -rf /', 'dd if=', ':(){ :|:& };:', 'chmod -R 777 /',
            'mkfs.', 'fdisk', 'parted'
        ]

    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate command for security"""
        command = command.strip()

        # Check for empty command
        if not command:
            return False, "Leerer Befehl"

        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern in command.lower():
                return False, f"Gefährlicher Befehl erkannt: {pattern}"

        # Extract base command (first word, ignore sudo)
        parts = command.split()
        base_cmd = parts[0]
        if base_cmd == 'sudo' and len(parts) > 1:
            base_cmd = parts[1]

        # Remove path from command (e.g., /usr/bin/echo -> echo)
        base_cmd = os.path.basename(base_cmd)

        # Check if command is allowed
        if base_cmd not in self.allowed_commands:
            return False, f"Befehl nicht erlaubt: {base_cmd}"

        return True, "OK"

    def check_sudo_available(self) -> bool:
        """Check if sudo is available and configured"""
        try:
            # First check if sudo command exists
            result = subprocess.run(
                ['which', 'sudo'],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                return False

            # Then check if we can use sudo (try non-interactive first)
            result = subprocess.run(
                ['sudo', '-n', 'true'],
                capture_output=True,
                timeout=5
            )

            # If non-interactive works, great!
            if result.returncode == 0:
                return True

            # If not, sudo is available but needs password
            # We'll handle password prompts in the GUI
            return True

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_sudo_command(self, command: str) -> list[str]:
        """Convert command string to sudo command list"""
        # If command already starts with sudo, use as-is
        if command.strip().startswith('sudo'):
            return command.split()

        # Add sudo prefix
        return ['sudo'] + command.split()

    def execute_command(
        self,
        command: str,
        use_sudo: bool = True,
        timeout: int = 300,
        working_dir: str = None
    ) -> CommandResult:
        """Execute a system command safely"""

        start_time = time.time()

        # Validate command
        is_valid, validation_msg = self.validate_command(command)
        if not is_valid:
            return CommandResult(
                command=command,
                status=CommandStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr=f"Sicherheitsvalidierung fehlgeschlagen: {validation_msg}",
                execution_time=0,
                start_time=start_time,
                end_time=time.time()
            )

        # Prepare command
        if use_sudo:
            cmd_list = self.get_sudo_command(command)
        else:
            cmd_list = command.split()

        # Emit started signal
        self.command_started.emit(command)
        self.progress_updated.emit(f"Starte Befehl: {command}")

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
                universal_newlines=True,
                cwd=working_dir,
                env=os.environ.copy()
            )

            # Read output in real-time
            stdout_lines = []
            stderr_lines = []

            # Create threads for reading stdout and stderr
            stdout_queue = queue.Queue()
            stderr_queue = queue.Queue()

            def read_stdout():
                try:
                    for line in iter(self.current_process.stdout.readline, ''):
                        if line:
                            stdout_queue.put(('stdout', line.rstrip()))
                except Exception:
                    pass
                finally:
                    stdout_queue.put(('stdout', None))

            def read_stderr():
                try:
                    for line in iter(self.current_process.stderr.readline, ''):
                        if line:
                            stderr_queue.put(('stderr', line.rstrip()))
                except Exception:
                    pass
                finally:
                    stderr_queue.put(('stderr', None))

            stdout_thread = threading.Thread(target=read_stdout, daemon=True)
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)

            stdout_thread.start()
            stderr_thread.start()

            # Monitor output and process
            stdout_finished = False
            stderr_finished = False

            while not (stdout_finished and stderr_finished):
                if self.should_cancel:
                    self.current_process.terminate()
                    time.sleep(1)
                    if self.current_process.poll() is None:
                        self.current_process.kill()
                    break

                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    self.current_process.terminate()
                    time.sleep(1)
                    if self.current_process.poll() is None:
                        self.current_process.kill()

                    return CommandResult(
                        command=command,
                        status=CommandStatus.TIMEOUT,
                        return_code=-1,
                        stdout='\n'.join(stdout_lines),
                        stderr='\n'.join(stderr_lines) + '\nTimeout erreicht',
                        execution_time=time.time() - start_time,
                        start_time=start_time,
                        end_time=time.time()
                    )

                # Read stdout
                try:
                    output_type, line = stdout_queue.get_nowait()
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
                    output_type, line = stderr_queue.get_nowait()
                    if line is None:
                        stderr_finished = True
                    else:
                        stderr_lines.append(line)
                        self.output_received.emit('stderr', line)
                        if self.output_callback:
                            self.output_callback('stderr', line)
                except queue.Empty:
                    pass

                time.sleep(0.01)  # Small delay to prevent busy waiting

            # Wait for process to complete
            return_code = self.current_process.wait()

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
                execution_time=time.time() - start_time,
                start_time=start_time,
                end_time=time.time()
            )

            # Add to history
            self.add_to_history(result)

            # Emit finished signal
            self.command_finished.emit(result)
            self.progress_updated.emit(f"Befehl beendet: {status.value}")

            return result

        except FileNotFoundError as e:
            error_result = CommandResult(
                command=command,
                status=CommandStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr=f"Befehl nicht gefunden: {e}",
                execution_time=time.time() - start_time,
                start_time=start_time,
                end_time=time.time()
            )
            self.command_finished.emit(error_result)
            return error_result

        except Exception as e:
            error_result = CommandResult(
                command=command,
                status=CommandStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr=f"Unerwarteter Fehler: {e}",
                execution_time=time.time() - start_time,
                start_time=start_time,
                end_time=time.time()
            )
            self.command_finished.emit(error_result)
            return error_result

        finally:
            self.is_running = False
            self.current_process = None

    def cancel_current_command(self):
        """Cancel the currently running command"""
        if self.is_running and self.current_process:
            self.should_cancel = True
            self.progress_updated.emit("Breche Befehl ab...")

    def add_to_history(self, result: CommandResult):
        """Add command result to history"""
        self.command_history.append(result)

        # Limit history size
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]

    def get_history(self) -> list[CommandResult]:
        """Get command execution history"""
        return self.command_history.copy()

    def clear_history(self):
        """Clear command execution history"""
        self.command_history.clear()

    def get_stats(self) -> Dict:
        """Get execution statistics"""
        if not self.command_history:
            return {}

        total_commands = len(self.command_history)
        successful = sum(1 for r in self.command_history if r.status == CommandStatus.SUCCESS)
        failed = sum(1 for r in self.command_history if r.status == CommandStatus.FAILED)
        cancelled = sum(1 for r in self.command_history if r.status == CommandStatus.CANCELLED)

        avg_execution_time = sum(r.execution_time for r in self.command_history) / total_commands

        return {
            'total_commands': total_commands,
            'successful': successful,
            'failed': failed,
            'cancelled': cancelled,
            'success_rate': (successful / total_commands) * 100,
            'average_execution_time': avg_execution_time
        }


class CommandExecutorThread(QThread):
    """Qt Thread wrapper for CommandExecutor"""

    def __init__(self, executor: CommandExecutor, command: str, use_sudo: bool = True):
        super().__init__()
        self.executor = executor
        self.command = command
        self.use_sudo = use_sudo
        self.result: Optional[CommandResult] = None

    def run(self):
        """Execute command in thread"""
        self.result = self.executor.execute_command(self.command, self.use_sudo)


# Test functions
def test_command_executor():
    """Test the CommandExecutor"""
    print("🧪 Teste CommandExecutor...")

    def output_callback(output_type: str, line: str):
        print(f"[{output_type.upper()}] {line}")

    executor = CommandExecutor(output_callback=output_callback)

    # Test 1: Simple command
    print("\n1. Teste einfachen Befehl...")
    result = executor.execute_command("echo 'Hello World'", use_sudo=False)
    print(f"Status: {result.status.value}")
    print(f"Return Code: {result.return_code}")
    print(f"Output: {result.stdout}")

    # Test 2: Command validation
    print("\n2. Teste Befehlsvalidierung...")
    dangerous_cmd = "rm -rf /"
    is_valid, msg = executor.validate_command(dangerous_cmd)
    print(f"Gefährlicher Befehl '{dangerous_cmd}': {'Erlaubt' if is_valid else 'Blockiert'} - {msg}")

    # Test 3: Sudo availability
    print("\n3. Teste sudo-Verfügbarkeit...")
    sudo_available = executor.check_sudo_available()
    print(f"Sudo verfügbar: {'Ja' if sudo_available else 'Nein'}")

    # Test 4: Command with sudo (if available)
    if sudo_available:
        print("\n4. Teste sudo-Befehl...")
        result = executor.execute_command("whoami", use_sudo=True)
        print(f"Status: {result.status.value}")
        print(f"Output: {result.stdout}")

    # Test 5: Statistics
    print("\n5. Statistiken:")
    stats = executor.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")

    # Test 6: History
    print(f"\n6. Historie ({len(executor.get_history())} Befehle):")
    for i, cmd_result in enumerate(executor.get_history()[-3:], 1):  # Last 3
        print(f"   {i}. {cmd_result.command} -> {cmd_result.status.value}")

if __name__ == "__main__":
    # Test without Qt (for standalone testing)
    test_command_executor()
