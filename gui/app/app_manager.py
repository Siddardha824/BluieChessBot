from pathlib import Path
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .engine import EngineSession

from PySide6.QtCore import QObject

from .board import BoardManager
from .theme import ThemeManager
from .settings import SettingsManager
from .game import GameManager
from .engine import EngineManager
from .shared import ROOT_DIR
from gui.utils import get_logger


logger = get_logger(__name__)


class AppManager(QObject):
    """
    Root application object.

    Owns and wires together all major subsystems.
    """

    MAIN_SESSION_ID = "main"

    def __init__(self, app,parent=None):
        super().__init__(parent)

        logger.info("Initializing app manager")

        self._board = BoardManager(self)

        self._engine = EngineManager(self)
        self._main_session: EngineSession | None = None

        self._settings = SettingsManager.get_instance()

        self._theme_manager = ThemeManager(app)

        self._game = GameManager(self)

        self._connect_modules()
        logger.info("App manager initialized")

    @property
    def board(self) -> BoardManager:
        return self._board

    @property
    def engine(self) -> EngineManager:
        return self._engine

    @property
    def game(self) -> GameManager:
        return self._game

    @property
    def settings(self) -> SettingsManager:
        return self._settings

    @property
    def theme(self) -> ThemeManager:
        return self._theme_manager

    @property
    def main_session(self) -> "EngineSession":
        return self._ensure_main_session()

    def startup(
        self,
        engine_path: str | Path | None = None,
        start_engine: bool = True
    ):
        """
        Initialize application state.
        """

        logger.info("Starting application services")
        session = self._ensure_main_session()

        self.board.new_game()

        if start_engine:
            resolved_engine_path = self._resolve_engine_path(engine_path)

            if resolved_engine_path is not None:
                logger.info("Starting main engine session: %s", resolved_engine_path)
                session.start(str(resolved_engine_path))
                session.set_position_fen(self.board.getSession.fen)
            else:
                logger.warning("Engine executable could not be resolved")

    def set_theme(self) -> None:
        self._theme_manager.apply_theme("space")

    def shutdown(self):
        """
        Graceful application shutdown.
        """

        logger.info("Shutting down application services")
        self.engine.shutdown()
        self._main_session = None

    def start_engine(
        self,
        engine_path: str | Path | None = None,
        session_id: str = MAIN_SESSION_ID
    ) -> bool:
        """
        Start the specified engine session if an executable can be resolved.
        """

        resolved_engine_path = self._resolve_engine_path(engine_path)

        if resolved_engine_path is None:
            logger.warning("Unable to start engine; executable could not be resolved")
            return False

        logger.info("Starting engine session '%s': %s", session_id, resolved_engine_path)
        
        session = self.engine.get_session(session_id)
        if session is None:
            session = self.engine.create_session(session_id)

        if session is None:
            logger.error("Failed to create engine session: %s", session_id)
            return False

        session.start(str(resolved_engine_path))
        session.set_position_fen(self.board.getSession.fen)

        return True

    def stop_engine(self, session_id: str = MAIN_SESSION_ID):
        """
        Stop the specified engine session without tearing down all modules.
        """

        session = self.engine.get_session(session_id)

        if session is not None:
            logger.info("Stopping engine session: %s", session_id)
            session.stop()

    def _connect_modules(self):

        self._ensure_main_session()

        self.board.position_changed.connect(self._sync_engine_position)
        logger.debug("Connected board position updates to engine session")

    def _ensure_main_session(self) -> "EngineSession":

        if self._main_session is not None:
            return self._main_session

        session = self.engine.get_session(self.MAIN_SESSION_ID)

        if session is None:
            logger.debug("Creating main engine session")
            session = self.engine.create_session(self.MAIN_SESSION_ID)

        if session is None:
            raise RuntimeError("Unable to create main engine session")

        self._main_session = session
        return session

    def _sync_engine_position(self, fen: str):
        for session in list(self.engine.sessions.values()):
            if session.is_running():
                session.set_position_fen(fen)

    @staticmethod
    def _resolve_engine_path(
        engine_path: str | Path | None = None
    ) -> Path | None:
        import sys
        if engine_path is not None:
            path = Path(engine_path)
            if path.exists():
                return path
        else:
            suffix = ".exe" if sys.platform == "win32" else ""
            # Try project root
            path = ROOT_DIR.parent / "build" / f"BluieChessBot{suffix}"
            if path.exists():
                return path
            
            # Try app root
            path = ROOT_DIR / "build" / f"BluieChessBot{suffix}"
            if path.exists():
                return path
            
            # Fallback to check alternate suffix in project root
            alt_suffix = "" if sys.platform == "win32" else ".exe"
            alt_path = ROOT_DIR.parent / "build" / f"BluieChessBot{alt_suffix}"
            if alt_path.exists():
                return alt_path

            # Fallback to check alternate suffix in app root
            alt_path = ROOT_DIR / "build" / f"BluieChessBot{alt_suffix}"
            if alt_path.exists():
                return alt_path

        logger.debug("Engine path does not exist")
        return None
