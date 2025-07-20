"""
Command Executor - Simplified
Safely executes system commands with sudo and real-time output
"""

import subprocess
import threading
import queue
import time
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal

class CommandStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

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
    """Simple command executor with Qt signals"""

    # Qt Signals
    output_received = pyqtSignal(str, str)  # (output_type, text)
    command_started = pyqtSignal(str)  # command
    command_finished = pyqtSignal(object)  # CommandResult

    def __init__(self, output_callback: Optional[Callable] = None):
        super().__init__()
        self.output_callback = output_callback
        self.current_process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.should_cancel = False

    def is_command_safe(self, command: str) -> bool:
        """Basic command safety check"""
        dangerous_patterns = [
            'rm -rf /', 'dd if=', 'mkfs.', 'fdisk', 'parted',
            ':(){ :|:& };:', 'chmod -R 777 /'
        ]

        command_lower = command.lower()
        return not any(pattern in command_lower for pattern in dangerous_patterns)

    def execute_command(self, command: str, use_sudo: bool = True, timeout: int = 300) -> CommandResult:
        """Execute a system command safely"""
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

        # Prepare command
        if use_sudo and not command.strip().startswith('sudo'):
            cmd_list = ['sudo'] + command.split()
        else:
            cmd_list = command.split()

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
                bufsize=1
            )

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
                except:
                    pass
                finally:
                    stdout_queue.put(None)

            def read_stderr():
                try:
                    for line in iter(self.current_process.stderr.readline, ''):
                        if line:
                            stderr_queue.put(line.rstrip())
                except:
                    pass
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
                    self.current_process.terminate()
                    break

                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    self.current_process.terminate()
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

    def cancel_current_command(self):
        """Cancel the currently running command"""
        if self.is_running and self.current_process:
            self.should_cancel = True
            try:
                self.current_process.terminate()
                time.sleep(1)
                if self.current_process.poll() is None:
                    self.current_process.kill()
            except:
                pass

    def check_sudo_available(self) -> bool:
        """Check if sudo is available"""
        try:
            result = subprocess.run(['which', 'sudo'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
