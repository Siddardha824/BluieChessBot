from PySide6.QtCore import QObject, QProcess, Signal

from ..models.engine_status import EngineStatus
from ..services.engine_connector import EngineConnector
from ..services.uci_parser import UCIParser, PacketType

from gui.utils import get_logger

logger = get_logger(__name__)

class EngineService(QObject):
    """
    Internal service that handles the execution, process lifecycle, 
    and UCI parsing for a single engine subprocess.
    """
    engine_ready = Signal()
    engine_stopped = Signal(int, QProcess.ExitStatus)
    engine_error = Signal(str)
    best_move_updated = Signal(str)

    def __init__(self, engine_status: EngineStatus, parent):
        super().__init__(parent)
        self.status = engine_status
        self._connector = EngineConnector(self)

        self._connector.stdout_received.connect(self._on_stdout)
        self._connector.process_finished.connect(self._on_process_finished)
        self._connector.process_error.connect(self._on_process_error)
        self._connector.process.stateChanged.connect(self._on_process_state_changed)
        
        logger.debug("Engine service initialized")

    def _on_process_state_changed(self, state: QProcess.ProcessState):
        if state == QProcess.ProcessState.NotRunning:
            self.status.info.connection_status = "NotRunning"
        elif state == QProcess.ProcessState.Starting:
            self.status.info.connection_status = "Starting"
        elif state == QProcess.ProcessState.Running:
            self.status.info.connection_status = "Running"
        self.status.info.notify_updated()

    def start(self, fallback_path: str = "") -> bool:
        if fallback_path and not self.status.settings.engine_path:
            self.status.settings.engine_path = fallback_path

        target_path = self.status.settings.engine_path

        if self._connector.start(target_path):
            self.status.info.search_status = "Connecting"
            self.status.info.notify_updated()
            self.send("uci")
            logger.info("Engine service process started using path: %s", target_path)
            return True
        else:
            logger.warning("Engine service failed to start process at: %s", target_path)
            return False

    def stop(self):
        logger.info("Stopping engine service process")
        self._connector.stop()

    def send(self, command: str):
        self._connector.send(command)

    def update_settings(self, **kwargs):
        """
        Dynamically updates the engine settings model from provided keyword arguments.
        """
        for key, value in kwargs.items():
            if hasattr(self.status.settings, key):
                setattr(self.status.settings, key, value)
                logger.debug("Updated setting '%s' to %s", key, value)
            else:
                logger.warning("Attempted to update unknown engine setting: %s", key)

    def is_running(self) -> bool:
        return self._connector.process.state() == QProcess.ProcessState.Running

    def is_ready(self):
        self.send("isready")

    def set_position_startpos(self):
        self.send("position startpos")

    def set_position_fen(self, fen: str):
        self.send(f"position fen {fen}")

    def set_options(self):
        threads = self.status.settings.threads
        hash_size = self.status.settings.hash_size
        self.send(f"setoption name Threads value {threads}")
        self.send(f"setoption name Hash value {hash_size}")

    def go(self):
        """
        Reads the constraint mode from settings and executes the corresponding search.
        """
        mode = self.status.settings.constraint_mode.lower()
        
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
        self.status.info.search_status = "Searching"
        self.status.info.notify_updated()
        self.send(f"go depth {depth}")

    def go_infinite(self):
        self.status.info.search_status = "Searching"
        self.status.info.notify_updated()
        self.send("go infinite")

    def go_time(self, ms: int):
        self.status.info.search_status = "Searching"
        self.status.info.notify_updated()
        self.send(f"go movetime {ms}")

    def go_nodes(self, nodes: int):
        self.status.info.search_status = "Searching"
        self.status.info.notify_updated()
        self.send(f"go nodes {nodes}")

    def stop_search(self):
        self.status.info.search_status = "Idle"
        self.status.info.notify_updated()
        self.send("stop")

    def _on_stdout(self, line: str):
        packet = UCIParser.parse_line(line, self.status.analysis)
        if packet is None:
            return
            
        packet_type = packet["type"]
        if packet_type == PacketType.UCIOK:
            self.status.info.search_status = "Idle"
            self.status.info.notify_updated()
            logger.info("Engine UCI handshake complete")
            
        elif packet_type == PacketType.READYOK:
            logger.info("Engine ready for commands")
            self.engine_ready.emit()
            
        elif packet_type == PacketType.ID:
            if "name" in packet:
                self.status.info.name = packet["name"]
            if "author" in packet:
                self.status.info.author = packet["author"]
            self.status.info.notify_updated()
            
        elif packet_type == PacketType.INFO:
            self.status.analysis.notify_updated()
            
        elif packet_type == PacketType.BESTMOVE:
            self.status.analysis.best_move = packet["best_move"]
            self.status.info.search_status = "Idle"
            self.status.analysis.notify_updated()
            self.status.info.notify_updated()
            self.best_move_updated.emit(packet["best_move"])

    def _on_process_finished(self, exit_code, exit_status):
        logger.info("Engine process finished: code=%s status=%s", exit_code, exit_status)
        self.status.info.search_status = "Offline"
        self.status.info.notify_updated()
        self.engine_stopped.emit(exit_code, exit_status)

    def _on_process_error(self, message: str):
        logger.error("Engine process error encountered: %s", message)
        self.status.info.connection_status = "Error"
        self.status.info.search_status = "Offline"
        self.status.info.notify_updated()
        self.engine_error.emit(message)