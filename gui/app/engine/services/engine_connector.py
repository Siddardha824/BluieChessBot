import os
from typing import Optional
from PySide6.QtCore import QObject, QProcess, Slot, Signal
from gui.utils import get_logger

logger = get_logger(__name__)

class EngineConnector(QObject):
    """
    Manages the lifecycle of the C++ Chess Engine process asynchronously using PySide6's QProcess.
    Optimized for low-latency I/O and UI responsiveness.
    """
    stdout_received = Signal(str)
    stderr_received = Signal(str)
    process_finished = Signal(int, QProcess.ExitStatus)
    process_error = Signal(str)

    # Reusing dictionary prevents memory reallocation on every error occurrence
    _ERROR_MESSAGES = {
        QProcess.ProcessError.FailedToStart: "Failed to start process",
        QProcess.ProcessError.Crashed: "Process crashed",
        QProcess.ProcessError.Timedout: "Process timed out",
        QProcess.ProcessError.WriteError: "Write error",
        QProcess.ProcessError.ReadError: "Read error",
        QProcess.ProcessError.UnknownError: "Unknown process error"
    }

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.process = QProcess(self)
        
        # Configure process stream channels
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        
        # Wire QProcess internal signals
        self.process.readyReadStandardOutput.connect(self._handle_ready_read_stdout)
        self.process.readyReadStandardError.connect(self._handle_ready_read_stderr)
        self.process.errorOccurred.connect(self._handle_process_error)
        self.process.finished.connect(self._handle_process_finished)
        
        logger.debug("Engine connector initialized")

    def start(self, executable_path: str) -> bool:
        """
        Launches the Chess Engine subprocess.
        """
        if self.process.state() != QProcess.ProcessState.NotRunning:
            logger.warning("Attempted to start engine while process is already running")
            # Wait briefly to see if it's currently starting up
            if self.process.waitForStarted(250):
                return True

        if not os.path.exists(executable_path):
            logger.error("Engine executable not found: %s", executable_path)
            return False
            
        logger.info("Starting engine subprocess: %s", executable_path)
        
        self.process.start(executable_path)
        
        # Reduced blocking timeout to 250ms to prevent GUI thread freezing.
        # Standard local binaries start almost instantaneously.
        if not self.process.waitForStarted(250):
            logger.error("Engine subprocess failed to start within 250ms")
            return False
            
        return True

    def stop(self) -> None:
        """
        Safely halts search threads and terminates the subprocess.
        """
        if self.process.state() == QProcess.ProcessState.Running:
            logger.info("Stopping engine subprocess")
            self.send("quit")
            
            # Reduced blocking wait to 300ms. 
            # If the engine hangs, we want to free the UI thread quickly.
            if not self.process.waitForFinished(300):
                logger.warning("Engine did not exit gracefully within 300ms; terminating")
                self.process.terminate()
        else:
            logger.debug("Stop requested while engine subprocess is not running")

    def send(self, command: str):
        """
        Writes a standard command line to the engine cin stdin stream.
        """
        if self.process.state() != QProcess.ProcessState.Running:
            logger.warning("Failed to send command; engine is not running: %s", command)
            return
            
        logger.debug("Sent engine command: %s", command)
        
        # Avoid string interpolation (f-strings) overhead for high-frequency writes
        self.process.write((command + "\n").encode("utf-8"))

    @Slot()
    def _handle_ready_read_stdout(self) -> None:
        """
        Read stdout line-by-line and emit raw text. 
        Highly optimized hot-path for processing thousands of lines per second.
        """
        while self.process.canReadLine():
            raw_line = bytes(self.process.readLine().data()).decode("utf-8", errors="ignore").strip()
            if raw_line:
                self.stdout_received.emit(raw_line)

    @Slot()
    def _handle_ready_read_stderr(self) -> None:
        """
        Read stderr output and emit it.
        """
        stderr_text = bytes(self.process.readAllStandardError().data()).decode("utf-8", errors="ignore").strip()
        if stderr_text:
            logger.warning("Engine stderr: %s", stderr_text)
            self.stderr_received.emit(stderr_text)

    @Slot(QProcess.ProcessError)
    def _handle_process_error(self, error: QProcess.ProcessError) -> None:
        """
        Handle QProcess failures using the class-level map.
        """
        message = self._ERROR_MESSAGES.get(error, f"Process error: {error}")
        logger.error("Engine process error: %s", message)
        self.process_error.emit(message)

    @Slot(int, QProcess.ExitStatus)
    def _handle_process_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        """
        Handle process termination.
        """
        logger.info("Engine process finished with exit code %s and status %s", exit_code, exit_status)
        self.process_finished.emit(exit_code, exit_status)