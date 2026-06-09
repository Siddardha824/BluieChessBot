from PySide6.QtCore import QObject, QProcess, Signal
from ..services.engine_connector import EngineConnector
from ..services.uci_parser import UCIParser, PacketType
from ..models.engine_info import EngineInfo
from ..models.analysis_state import AnalysisState
from gui.utils import get_logger


logger = get_logger(__name__)


class EngineSession(QObject):

    engine_ready = Signal()
    engine_stopped = Signal(int, QProcess.ExitStatus)
    engine_error = Signal(str)
    best_move_updated = Signal(str)

    def __init__(
        self,
        parent=None
    ):
        super().__init__(parent)

        self._connector = EngineConnector(self)
        self._engine_info = EngineInfo(self)
        self._analysis_state = AnalysisState(self)

        self._connector.stdout_received.connect(
            self._on_stdout
        )

        self._connector.process_finished.connect(
            self._on_process_finished
        )

        self._connector.process_error.connect(
            self._on_process_error
        )
        logger.debug("Engine session initialized")

    @property
    def engine_info(self) -> EngineInfo:
        return self._engine_info
    
    @property
    def analysis_state(self) -> AnalysisState:
        return self._analysis_state

    def start(self, engine_path: str):

        if self._connector.start(engine_path):

            self.engine_info.path = engine_path
            self.engine_info.connection_status = "Connecting"

            self.send("uci")
            logger.info("Engine session started: %s", engine_path)
        else:
            logger.warning("Engine session failed to start: %s", engine_path)

    def stop(self):

        logger.info("Stopping engine session")
        self._connector.stop()

    def send(self, command: str):

        self._connector.send(command)

    def is_ready(self):

        logger.debug("Checking engine readiness")
        self.send("isready")

    def set_position_startpos(self):

        logger.debug("Setting engine position to startpos")
        self.send("position startpos")

    def set_position_fen(self, fen: str):

        logger.debug("Setting engine position FEN: %s", fen)
        self.send(f"position fen {fen}")

    def go_depth(self, depth: int):

        logger.info("Starting engine search to depth %s", depth)
        self.send(f"go depth {depth}")

    def stop_search(self):

        logger.info("Stopping engine search")
        self.send("stop")

    def _on_stdout(self, line: str):

        packet = UCIParser.parse_line(line, self._analysis_state)

        if packet is None:
            return

        packet_type = packet["type"]

        if packet_type == PacketType.UCIOK:
            self.engine_info.connection_status = "Connected"
            logger.info("Engine UCI handshake complete")

        elif packet_type == PacketType.READYOK:
            logger.info("Engine ready")
            self.engine_ready.emit()

        elif packet_type == PacketType.ID:
            if "name" in packet:
                self.engine_info.name = packet["name"]
                logger.info("Engine name: %s", packet["name"])

            if "author" in packet:
                self.engine_info.author = packet["author"]
                logger.info("Engine author: %s", packet["author"])

        elif packet_type == PacketType.INFO:
            self._analysis_state.updated.emit()

        elif packet_type == PacketType.BESTMOVE:
            self._analysis_state.best_move = (
                packet["best_move"]
            )
            logger.info("Best move received: %s", packet["best_move"])
            self.best_move_updated.emit(
                packet["best_move"]
            )


    def _on_process_finished(
        self,
        exit_code,
        exit_status
    ):
        self.engine_info.connection_status = "Disconnected"

        logger.info("Engine session stopped: code=%s status=%s", exit_code, exit_status)
        self.engine_stopped.emit(exit_code, exit_status)
    
    def _on_process_error(
        self,
        message: str
    ):
        self.engine_info.connection_status = "Error"

        logger.error("Engine session error: %s", message)
        self.engine_error.emit(message)
