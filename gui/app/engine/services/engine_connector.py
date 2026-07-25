"""Manage the lifecycle and I/O of a UCI chess engine subprocess using QProcess.

This module provides the EngineConnector class for managing subprocess execution,
asynchronous I/O streams, standard error logging, and graceful process termination.

Optimizations:
- Separate stdout/stderr channels to avoid mixing output streams.
- Line-by-line reading for efficient UCI protocol parsing.
- Reusable error message dictionary to prevent repeated allocations.
- Short timeouts to maintain UI responsiveness during process operations.
"""

import os
from PySide6.QtCore import QObject, QProcess, Slot, Signal
from gui.utils import get_logger

logger = get_logger(__name__)


class EngineConnector(QObject):
    """Manage the lifecycle and I/O of a UCI chess engine subprocess.

    This class wraps Qt's QProcess to provide:
    - Asynchronous engine process management.
    - Non-blocking stdout/stderr reading.
    - Graceful shutdown with timeout handling.
    - Standardized error reporting.

    All I/O operations are designed to be non-blocking to maintain UI thread responsiveness.
    Process state is monitored continuously and communicated via Qt signals.

    Signals:
        stdout_received: Emitted on each complete line from engine stdout.
        stderr_received: Emitted when engine outputs to stderr.
        process_finished: Emitted when process terminates (exit_code, exit_status).
        process_error: Emitted on process errors (error_message).
    """

    # Qt Signals for process events
    stdout_received = Signal(str)      # Single line from engine output
    stderr_received = Signal(str)      # Engine error/diagnostic output
    process_finished = Signal(int, QProcess.ExitStatus)  # Process termination
    process_error = Signal(str)        # Process error event

    # Class-level error message mapping (constant across all instances)
    # Benefits: Single allocation, cache-friendly, no runtime dict building
    _ERROR_MESSAGES = {
        QProcess.ProcessError.FailedToStart: "Failed to start process",
        QProcess.ProcessError.Crashed: "Process crashed",
        QProcess.ProcessError.Timedout: "Process timed out",
        QProcess.ProcessError.WriteError: "Write error",
        QProcess.ProcessError.ReadError: "Read error",
        QProcess.ProcessError.UnknownError: "Unknown process error"
    }

    def __init__(self, parent):
        """Initialize the engine connector.

        Set up the QProcess instance with separate stdout/stderr channels and
        connect internal signals for asynchronous I/O handling.

        Args:
            parent: Qt parent object for memory management.
        """
        super().__init__(parent)
        self.process = QProcess(self)

        # Separate stdout/stderr to prevent mixing and allow independent handling
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)

        # Connect QProcess signals to internal slot handlers
        self.process.readyReadStandardOutput.connect(self._handle_ready_read_stdout)
        self.process.readyReadStandardError.connect(self._handle_ready_read_stderr)
        self.process.errorOccurred.connect(self._handle_process_error)
        self.process.finished.connect(self._handle_process_finished)

        logger.debug("Engine connector initialized")

    def start(self, executable_path: str) -> bool:
        """Launch the UCI chess engine subprocess.

        Validate that the executable path exists, start the process, and wait briefly
        for initialization. If the process is already running, return success.

        Args:
            executable_path: Path to the chess engine executable.

        Returns:
            True if the process started successfully or was already running, False otherwise.
        """
        # Handle case where process is already running
        if self.process.state() != QProcess.ProcessState.NotRunning:
            logger.warning("Attempted to start engine while process is already running")
            # Brief check to confirm it's actually running
            if self.process.waitForStarted(250):
                return True

        # Validate executable exists before attempting to start
        if not os.path.exists(executable_path):
            logger.error("Engine executable not found: %s", executable_path)
            return False

        logger.info("Starting engine subprocess: %s", executable_path)

        # Start the process
        self.process.start(executable_path)

        # Wait for process startup with short timeout (250ms)
        # Purpose: Fail fast if process fails to start while keeping UI responsive
        # Standard local binaries start in < 50ms typically
        if not self.process.waitForStarted(250):
            logger.error("Engine subprocess failed to start within 250ms")
            return False

        return True

    def stop(self) -> None:
        """Gracefully stop the engine subprocess.

        Send the UCI 'quit' command to allow the engine to clean up resources.
        If the engine does not exit within the timeout, forcefully terminate the process.

        Blocking timeout is kept short (300ms) to maintain UI responsiveness.
        """
        if self.process.state() == QProcess.ProcessState.Running:
            logger.info("Stopping engine subprocess")
            # Send graceful shutdown command
            self.send("quit")

            # Wait for graceful termination with short timeout (300ms)
            # Purpose: Prevent UI thread blocking if engine is unresponsive
            # Most engines exit cleanly within 50ms
            if not self.process.waitForFinished(300):
                logger.warning("Engine did not exit gracefully within 300ms; force terminating")
                self.process.terminate()
        else:
            logger.debug("Stop requested while engine subprocess is not running")

    def send(self, command: str):
        """Send a UCI command to the engine stdin.

        Encode the command as UTF-8, append a newline, and write to the process stdin.
        Take no action if the process is not running.

        Args:
            command: UCI command string (e.g., "go depth 20", "position startpos").
        """
        # Validate process is running before attempting write
        if self.process.state() != QProcess.ProcessState.Running:
            logger.warning("Failed to send command; engine is not running: %s", command)
            return

        logger.debug("Sent engine command: %s", command)

        # Encode command and send with newline terminator
        # Note: Concatenation is faster than f-string for this high-frequency operation
        self.process.write((command + "\n").encode("utf-8"))

    @Slot()
    def _handle_ready_read_stdout(self) -> None:
        """Handle incoming stdout from the engine process.

        Read available lines and emit each as a signal. This is a hot-path that
        can be called hundreds of times per second during active analysis.
        Lines are decoded UTF-8 with error tolerance and whitespace stripped.

        Empty lines are silently discarded to reduce signal overhead.
        """
        # Drain all available lines from the buffer
        while self.process.canReadLine():
            # Read line as bytes, decode to string, and strip whitespace
            raw_line = bytes(self.process.readLine().data()).decode("utf-8", errors="ignore").strip()
            # Only emit non-empty lines
            if raw_line:
                self.stdout_received.emit(raw_line)

    @Slot()
    def _handle_ready_read_stderr(self) -> None:
        """Handle stderr output from the engine process.

        Read all available stderr data, log it as a warning, and emit it as a signal.
        Engine diagnostic and error messages are typically sent here.

        Empty stderr is silently ignored to reduce signal overhead.
        """
        # Read all available stderr data at once
        stderr_text = bytes(self.process.readAllStandardError().data()).decode("utf-8", errors="ignore").strip()
        if stderr_text:
            logger.warning("Engine stderr: %s", stderr_text)
            self.stderr_received.emit(stderr_text)

    @Slot(QProcess.ProcessError)
    def _handle_process_error(self, error: QProcess.ProcessError) -> None:
        """Handle process errors from the engine subprocess.

        Map QProcess error codes to human-readable messages using the class-level
        error dictionary and emit the process_error signal.

        Args:
            error: QProcess.ProcessError code indicating the type of error.
        """
        # Look up error message or use default if not found
        message = self._ERROR_MESSAGES.get(error, f"Process error: {error}")
        logger.error("Engine process error: %s", message)
        self.process_error.emit(message)

    @Slot(int, QProcess.ExitStatus)
    def _handle_process_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        """Handle engine process termination.

        Log the process exit information and emit the process_finished signal
        to notify listeners of the process state change.

        Args:
            exit_code: Process exit code (0 = normal, non-zero = error).
            exit_status: QProcess.ExitStatus (NormalExit or CrashExit).
        """
        logger.info("Engine process finished with exit code %s and status %s", exit_code, exit_status)
        self.process_finished.emit(exit_code, exit_status)