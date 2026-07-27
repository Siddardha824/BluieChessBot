"""Manage the lifecycle and communication of a single UCI-compatible chess engine.

This module provides the EngineService class, which manages subprocess execution,
UCI protocol communication, status tracking, search control, and configuration
settings for the engine.
"""

from PySide6.QtCore import QObject, QProcess, Signal

from ..models.engine_status import EngineStatus
from ..services.engine_connector import EngineConnector
from ..services.uci_parser import UCIParser, PacketType

from gui.utils import get_logger

logger = get_logger(__name__)


class EngineService(QObject):
    """Manage a single UCI chess engine subprocess.

    This service handles all aspects of engine lifecycle including process creation,
    UCI protocol communication, and status updates. It acts as a bridge between the
    GUI and the chess engine, translating high-level requests into UCI commands
    and parsing engine output into structured analysis data.

    Signals:
        engine_ready: Emitted when the engine confirms readiness (READYOK).
        engine_stopped: Emitted when the engine process terminates (exit_code, exit_status).
        engine_error: Emitted on engine process error (error_message).
        best_move_updated: Emitted when the engine finds the best move (best_move_string).
    """

    engine_ready = Signal()
    engine_stopped = Signal(int, QProcess.ExitStatus)
    engine_error = Signal(str)
    best_move_updated = Signal(str)

    def __init__(self, engine_status: EngineStatus, parent):
        """Initialize the engine service.

        Args:
            engine_status: EngineStatus model containing settings and state.
            parent: Qt parent object for memory management.
        """
        super().__init__(parent)
        self.status = engine_status
        self._connector = EngineConnector(self)

        # Connect engine connector signals to internal handlers
        self._connector.stdout_received.connect(self._on_stdout)
        self._connector.process_finished.connect(self._on_process_finished)
        self._connector.process_error.connect(self._on_process_error)
        self._connector.process.stateChanged.connect(self._on_process_state_changed)

        logger.debug("Engine service initialized")

    def _on_process_state_changed(self, state: QProcess.ProcessState):
        """Handle process state changes from the engine connector.

        Update the engine connection status in the model whenever the process
        transitions between NotRunning, Starting, and Running states.

        Args:
            state: Current QProcess.ProcessState.
        """
        if state == QProcess.ProcessState.NotRunning:
            self.status.info.connection_status = "NotRunning"
        elif state == QProcess.ProcessState.Starting:
            self.status.info.connection_status = "Starting"
        elif state == QProcess.ProcessState.Running:
            self.status.info.connection_status = "Running"
        self.status.info.notify_updated()

    def start(self, fallback_path: str = "") -> bool:
        """Start the engine process and initiate UCI handshake.

        If no engine path is configured, use the provided fallback path.
        After successfully starting the process, send the UCI initialization command.

        Args:
            fallback_path: Optional path to use if engine_path is not configured.

        Returns:
            True if the process started successfully, False otherwise.
        """
        # Use fallback path if configured path is not set
        if fallback_path and not self.status.settings.engine_path:
            self.status.settings.engine_path = fallback_path

        target_path = self.status.settings.engine_path

        if self._connector.start(target_path):
            # Mark as connecting and initiate UCI protocol
            self.status.info.search_status = "Connecting"
            self.status.info.notify_updated()
            self.send("uci")
            logger.info("Engine service process started using path: %s", target_path)
            return True
        else:
            logger.warning("Engine service failed to start process at: %s", target_path)
            return False

    def stop(self):
        """Stop the engine process gracefully."""
        logger.info("Stopping engine service process")
        self._connector.stop()

    def send(self, command: str):
        """Send a UCI command to the engine.

        If a setoption command is sent, change connection status to SyncingSettings
        and automatically send an 'isready' command to synchronize with the engine.

        Args:
            command: UCI command string to send.
        """
        self._connector.send(command)
        if command.startswith("setoption"):
            self.status.info.connection_status = "SyncingSettings"
            self.status.info.notify_updated()
            self._connector.send("isready")


    def update_settings(self, **kwargs):
        """Dynamically update engine settings from keyword arguments.

        Validate that each setting exists on the settings model before updating.
        If hash_size or threads are updated, synchronizes them with the active engine process.
        Emits a change notification on the settings model if any configurations were changed.

        Args:
            **kwargs: Setting name-value pairs (e.g., threads=4, hash_size=256).
        """
        updated = False
        threads_changed = False
        hash_changed = False

        for key, value in kwargs.items():
            if hasattr(self.status.settings, key):
                old_val = getattr(self.status.settings, key)
                if old_val != value:
                    setattr(self.status.settings, key, value)
                    logger.debug("Updated setting '%s' to %s", key, value)
                    updated = True
                    if key == "threads":
                        threads_changed = True
                    elif key == "hash_size":
                        hash_changed = True
            else:
                logger.warning("Attempted to update unknown engine setting: %s", key)

        if updated:
            self.status.settings.notify_updated()
            # If the engine is running, synchronize the modified threads/hash options
            if self.is_running():
                if threads_changed:
                    self.set_options("threads")
                if hash_changed:
                    self.set_options("hash_size")

    def is_running(self) -> bool:
        """Check if the engine process is currently running.

        Returns:
            True if the process is in the Running state, False otherwise.
        """
        return self._connector.process.state() == QProcess.ProcessState.Running

    def is_ready(self):
        """Send an 'isready' probe to verify engine responsiveness."""
        self.send("isready")

    def set_position_startpos(self):
        """Set the board position to the standard starting position."""
        self.send("position startpos")

    def set_position_fen(self, fen: str):
        """Set the board position from a FEN string.

        Args:
            fen: FEN string representing the board position.
        """
        self.send(f"position fen {fen}")

    def set_options(self, option_name: str | None = None):
        """Configure engine options (threads and/or hash table size).

        If option_name is specified, configure only that option by reading its value from the
        settings model and sending the corresponding setoption command. Otherwise, configure
        all options.

        Args:
            option_name: Optional name of the setting to configure ("threads" or "hash_size").
        """
        if option_name is None:
            threads = self.status.settings.threads
            hash_size = self.status.settings.hash_size
            self.send(f"setoption name Threads value {threads}")
            self.send(f"setoption name Hash value {hash_size}")
        elif option_name == "threads":
            threads = self.status.settings.threads
            self.send(f"setoption name Threads value {threads}")
        elif option_name == "hash_size":
            hash_size = self.status.settings.hash_size
            self.send(f"setoption name Hash value {hash_size}")
        else:
            logger.warning("Attempted to set unknown engine option: %s", option_name)


    def go(self):
        """Execute a search using the constraint mode configured in settings.

        Dispatch to the appropriate search method (go_depth, go_time, go_nodes, or go_infinite)
        based on the constraint_mode setting.
        """
        mode = self.status.settings.constraint_mode.lower()

        # Dispatch to appropriate search method based on constraint mode
        if mode == "depth":
            self.go_depth(self.status.settings.max_depth)
        elif mode == "time":
            self.go_time(self.status.settings.max_time_ms)
        elif mode == "nodes":
            self.go_nodes(self.status.settings.max_nodes)
        elif mode == "infinite":
            self.go_infinite()
        else:
            logger.warning("Unrecognized constraint mode in settings: %s", mode)

    def go_depth(self, depth: int):
        """Start a search limited to a specific depth.

        Args:
            depth: Maximum search depth in plies.
        """
        self.status.info.search_status = "Searching"
        self.status.info.notify_updated()
        self.send(f"go depth {depth}")

    def go_infinite(self):
        """Start an infinite search (continues until stopped)."""
        self.status.info.search_status = "Searching"
        self.status.info.notify_updated()
        self.send("go infinite")

    def go_time(self, ms: int):
        """Start a search limited to a specific time amount.

        Args:
            ms: Maximum search time in milliseconds.
        """
        self.status.info.search_status = "Searching"
        self.status.info.notify_updated()
        self.send(f"go movetime {ms}")

    def go_nodes(self, nodes: int):
        """Start a search limited to a specific number of nodes.

        Args:
            nodes: Maximum number of nodes to evaluate.
        """
        self.status.info.search_status = "Searching"
        self.status.info.notify_updated()
        self.send(f"go nodes {nodes}")

    def stop_search(self):
        """Stop the current search and mark the engine as idle."""
        self.status.info.search_status = "Idle"
        self.status.info.notify_updated()
        self.send("stop")

    def _on_stdout(self, line: str):
        """Handle incoming stdout from the engine process.

        Parse UCI protocol output and dispatch to appropriate handlers based on
        packet type (UCIOK, READYOK, ID, INFO, BESTMOVE).

        Args:
            line: Single line of engine stdout output.
        """
        # Parse UCI protocol line into structured packet
        packet = UCIParser.parse_line(line, self.status.analysis)
        if packet is None:
            return

        packet_type = packet["type"]

        # Handle UCI initialization complete
        if packet_type == PacketType.UCIOK:
            self.status.info.search_status = "Idle"
            self.status.info.notify_updated()
            logger.info("Engine UCI handshake complete")

        # Handle engine ready acknowledgment
        elif packet_type == PacketType.READYOK:
            logger.info("Engine ready for commands")
            if self.status.info.connection_status == "SyncingSettings":
                self.status.info.connection_status = "Running"
                self.status.info.notify_updated()
                logger.info("Engine settings successfully synchronized and applied")
            self.engine_ready.emit()

        # Handle engine identification
        elif packet_type == PacketType.ID:
            if "name" in packet:
                self.status.info.name = packet["name"]
            if "author" in packet:
                self.status.info.author = packet["author"]
            self.status.info.notify_updated()

        # Handle analysis update (depth, score, PV, etc.)
        elif packet_type == PacketType.INFO:
            self.status.analysis.notify_updated()

        # Handle best move discovery
        elif packet_type == PacketType.BESTMOVE:
            self.status.analysis.best_move = packet["best_move"]
            self.status.info.search_status = "Idle"
            self.status.analysis.notify_updated()
            self.status.info.notify_updated()
            self.best_move_updated.emit(packet["best_move"])

    def _on_process_finished(self, exit_code, exit_status):
        """Handle engine process termination.

        Args:
            exit_code: Process exit code (0 = normal, non-zero = error).
            exit_status: QProcess.ExitStatus indicating normal vs. crash termination.
        """
        logger.info("Engine process finished: code=%s status=%s", exit_code, exit_status)
        self.status.info.search_status = "Offline"
        self.status.info.notify_updated()
        self.engine_stopped.emit(exit_code, exit_status)

    def _on_process_error(self, message: str):
        """Handle engine process errors.

        Args:
            message: Error message from QProcess.
        """
        logger.error("Engine process error encountered: %s", message)
        self.status.info.connection_status = "Error"
        self.status.info.search_status = "Offline"
        self.status.info.notify_updated()
        self.engine_error.emit(message)