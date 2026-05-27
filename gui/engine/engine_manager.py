# gui/engine/engine_manager.py

import os
from typing import List, Optional
from PySide6.QtCore import QObject, QProcess, Signal, Slot
from gui.engine.uci_parser import UCIParser
from gui.models.analysis_state import AnalysisState
from gui.utils.logger import get_logger


def _decode_qbytearray(data_input) -> str:
    """
    Safely converts a PySide6 QByteArray or Python bytes object to a standard string.
    Satisfies both runtime environments and Pylance static type checkers.
    """
    if hasattr(data_input, "data"):
        try:
            return bytes(data_input.data()).decode("utf-8", errors="ignore")
        except Exception:
            pass
    elif isinstance(data_input, bytes):
        return data_input.decode("utf-8", errors="ignore")
    
    return str(data_input)

logger = get_logger(__name__)

class EngineManager(QObject):
    """
    Manages the lifecycle of the C++ Chess Engine process asynchronously
    using PySide6's QProcess. Standardizes communication via standard streams
    and relays events to the GUI via thread-safe signals.
    """
    # Signals
    uciok_received = Signal()
    readyok_received = Signal()
    info_received = Signal(object)          # Emits AnalysisState
    bestmove_received = Signal(str)         # Emits bestmove coordinate string
    uci_io_logged = Signal(str, str)        # Emits (raw_text, direction "IN" or "OUT")
    status_changed = Signal(str)           # Emits engine status description
    engine_error = Signal(str)             # Emits process error descriptions

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.process = QProcess(self)
        
        # Track engine state
        self.is_white_turn = True
        self.engine_status = "Disconnected"
        self.engine_path = ""
        
        # Configure process stream channels and environment
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)
        
        # Wire QProcess internal signals
        self.process.readyReadStandardOutput.connect(self._handle_ready_read_stdout)
        self.process.readyReadStandardError.connect(self._handle_ready_read_stderr)
        self.process.errorOccurred.connect(self._handle_process_error)
        self.process.finished.connect(self._handle_process_finished)

    def start_engine(self, executable_path: str) -> bool:
        """
        Launches the Chess Engine subprocess.
        """
        if self.process.state() != QProcess.ProcessState.NotRunning:
            logger.warning("Attempted to start engine, but a process is already running.")
            return False

        if not os.path.exists(executable_path):
            err_msg = f"Engine executable not found at: {executable_path}"
            logger.error(err_msg)
            self.engine_error.emit(err_msg)
            return False

        self.engine_path = executable_path
        self._update_status("Starting")
        logger.info(f"Starting engine subprocess: {executable_path}")
        
        # Run subprocess
        self.process.start(executable_path)
        
        # Immediate handshake request
        self.send_command("uci")
        return True

    def send_command(self, cmd: str) -> None:
        """
        Writes a standard command line to the engine cin stdin stream.
        """
        if self.process.state() != QProcess.ProcessState.Running:
            logger.warning(f"Failed to send command '{cmd}': engine is not running.")
            return

        cmd_stripped = cmd.strip()
        logger.debug(f"Sending command to engine: {cmd_stripped}")
        
        # Emit command log as OUT direction
        self.uci_io_logged.emit(cmd_stripped, "OUT")
        
        # Write to stream
        self.process.write(f"{cmd_stripped}\n".encode("utf-8"))

    def send_position(self, fen: str, moves: Optional[List[str]] = None) -> None:
        """
        Sends current position FEN and moves history to the engine.
        Updates self.is_white_turn from FEN to normalize score calculations.
        """
        try:
            # Parse whose turn it is from FEN string (second token)
            parts = fen.strip().split()
            if len(parts) > 1:
                self.is_white_turn = (parts[1] == 'w')
        except Exception as e:
            logger.error(f"Error parsing turn from FEN '{fen}': {e}")
            self.is_white_turn = True

        cmd = f"position fen {fen}"
        if moves:
            cmd += " moves " + " ".join(moves)
            
        self.send_command(cmd)

    def start_search(self, depth: Optional[int] = None, movetime: Optional[int] = None, infinite: bool = False) -> None:
        """
        Instructs engine to start calculating using "go".
        """
        self._update_status("Searching")
        cmd = "go"
        if infinite:
            cmd += " infinite"
        else:
            if depth is not None:
                cmd += f" depth {depth}"
            if movetime is not None:
                cmd += f" movetime {movetime}"
                
        self.send_command(cmd)

    def stop_search(self) -> None:
        """
        Aborts active search operations instantly.
        """
        if self.engine_status == "Searching":
            self.send_command("stop")
            self._update_status("Ready")

    def quit_engine(self) -> None:
        """
        Safely halts search threads and terminates the subprocess.
        """
        if self.process.state() == QProcess.ProcessState.Running:
            self.send_command("quit")
            # Wait briefly for process to exit cleanly
            if not self.process.waitForFinished(1000):
                logger.warning("Engine did not exit cleanly within 1s. Terminating forcefully...")
                self.process.terminate()
                
        self._update_status("Disconnected")

    def _update_status(self, new_status: str) -> None:
        if self.engine_status != new_status:
            self.engine_status = new_status
            self.status_changed.emit(new_status)
            logger.debug(f"Engine status changed: {new_status}")

    @Slot()
    def _handle_ready_read_stdout(self) -> None:
        """
        Triggered when standard output data is piped back from the engine.
        Reads lines and routes them to the UCI parser.
        """
        while self.process.canReadLine():
            line_bytes = self.process.readLine()
            raw_line = _decode_qbytearray(line_bytes).strip()
            
            if not raw_line:
                continue
                
            # Log as IN stream
            self.uci_io_logged.emit(raw_line, "IN")
            
            # Parse line using static UCIParser
            try:
                parsed = UCIParser.parse_line(raw_line, is_white_turn=self.is_white_turn)
                if not parsed:
                    continue
                    
                ptype = parsed["type"]
                if ptype == "uciok":
                    self._update_status("Ready")
                    self.uciok_received.emit()
                    
                elif ptype == "readyok":
                    self._update_status("Ready")
                    self.readyok_received.emit()
                    
                elif ptype == "bestmove":
                    self._update_status("Ready")
                    self.bestmove_received.emit(parsed["best_move"])
                    
                elif ptype == "info":
                    self.info_received.emit(parsed["state"])
                    
            except Exception as e:
                logger.error(f"Error parsing engine stdout line '{raw_line}': {e}", exc_info=True)

    @Slot()
    def _handle_ready_read_stderr(self) -> None:
        """
        Pipes error stream logs to output error handlers.
        """
        err_bytes = self.process.readAllStandardError()
        err_str = _decode_qbytearray(err_bytes).strip()
        if err_str:
            logger.error(f"Engine STDERR: {err_str}")
            self.engine_error.emit(f"STDERR: {err_str}")

    @Slot(QProcess.ProcessError)
    def _handle_process_error(self, error: QProcess.ProcessError) -> None:
        """
        Pipes subprocess execution failures.
        """
        err_map = {
            QProcess.ProcessError.FailedToStart: "The process failed to start. Verify path or permissions.",
            QProcess.ProcessError.Crashed: "The engine process crashed unexpectedly.",
            QProcess.ProcessError.Timedout: "Subprocess timeout occurred.",
            QProcess.ProcessError.WriteError: "Failed to write data to engine standard input.",
            QProcess.ProcessError.ReadError: "Failed to read data from engine standard output.",
            QProcess.ProcessError.UnknownError: "An unknown process error occurred."
        }
        err_desc = err_map.get(error, f"Process error: {error}")
        logger.error(f"Engine subprocess error: {err_desc}")
        self.engine_error.emit(err_desc)
        self._update_status("Disconnected")

    @Slot(int, QProcess.ExitStatus)
    def _handle_process_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        """
        Triggered when engine process terminates.
        """
        logger.info(f"Engine process finished. Code: {exit_code}, Status: {exit_status}")
        self._update_status("Disconnected")
