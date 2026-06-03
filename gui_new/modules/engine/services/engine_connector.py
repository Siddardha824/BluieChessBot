import os
from typing import Optional
from PySide6.QtCore import QObject, QProcess, Slot, Signal

class EngineConnector(QObject):
    """
    Manages the lifecycle of the C++ Chess Engine process asynchronously using PySide6's QProcess.
    """

    stdout_received = Signal(str)
    stderr_received = Signal(str)

    process_finished = Signal(int, QProcess.ExitStatus)
    process_error = Signal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self.process = QProcess(self)
        
        # Configure process stream channels and environment
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        
        # Wire QProcess internal signals
        self.process.readyReadStandardOutput.connect(self._handle_ready_read_stdout)
        self.process.readyReadStandardError.connect(self._handle_ready_read_stderr)
        self.process.errorOccurred.connect(self._handle_process_error)
        self.process.finished.connect(self._handle_process_finished)

    def start(self, executable_path: str) -> bool:
        """
        Launches the Chess Engine subprocess.
        """
        if self.process.state() != QProcess.ProcessState.NotRunning:
            # logger.warning("Attempted to start engine, but a process is already running.")
            return False

        if not os.path.exists(executable_path):
            # logger.error(f"Engine executable not found at: {executable_path}")
            return False
        
        # logger.info(f"Starting engine subprocess: {executable_path}")
        
        # Run subprocess
        self.process.start(executable_path)
        
        return True
    
    def stop(self) -> None:
        """
        Safely halts search threads and terminates the subprocess.
        """
        if self.process.state() == QProcess.ProcessState.Running:
            self.send("quit")
            # Wait briefly for process to exit cleanly
            if not self.process.waitForFinished(1000):
                # logger.warning("Engine did not exit cleanly within 1s. Terminating forcefully...")
                self.process.terminate()

    def send(self, command : str):
        """
        Writes a standard command line to the engine cin stdin stream.
        """
        if self.process.state() != QProcess.ProcessState.Running:
            # logger.warning(f"Failed to send command '{command}': engine is not running.")
            return
        
        # Write to stream
        command_bytes = f"{command.strip()}\n".encode("utf-8")
        self.process.write(command_bytes)

    @Slot()
    def _handle_ready_read_stdout(self) -> None:
        """
        Read stdout line-by-line and emit raw text.
        """

        while self.process.canReadLine():

            raw_line = self._decode_qbytearray(
                self.process.readLine()
            ).strip()

            if raw_line:
                self.stdout_received.emit(raw_line)


    @Slot()
    def _handle_ready_read_stderr(self) -> None:
        """
        Read stderr output and emit it.
        """

        stderr_text = self._decode_qbytearray(
            self.process.readAllStandardError()
        ).strip()

        if stderr_text:
            self.stderr_received.emit(stderr_text)

    @Slot(QProcess.ProcessError)
    def _handle_process_error(
        self,
        error: QProcess.ProcessError
    ) -> None:
        """
        Handle QProcess failures.
        """

        error_messages = {
            QProcess.ProcessError.FailedToStart:
                "Failed to start process",

            QProcess.ProcessError.Crashed:
                "Process crashed",

            QProcess.ProcessError.Timedout:
                "Process timed out",

            QProcess.ProcessError.WriteError:
                "Write error",

            QProcess.ProcessError.ReadError:
                "Read error",

            QProcess.ProcessError.UnknownError:
                "Unknown process error"
        }

        message = error_messages.get(
            error,
            f"Process error: {error}"
        )

        self.process_error.emit(message)

    @Slot(int, QProcess.ExitStatus)
    def _handle_process_finished(
        self,
        exit_code: int,
        exit_status: QProcess.ExitStatus
    ) -> None:
        """
        Handle process termination.
        """

        self.process_finished.emit(exit_code, exit_status)

    @staticmethod
    def _decode_qbytearray(data) -> str:
        return bytes(data.data()).decode(
            "utf-8",
            errors="ignore"
        )