from PySide6.QtCore import QObject

from ..sessions.engine_session import EngineSession
from gui.utils import get_logger


logger = get_logger(__name__)

class EngineManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.sessions: dict[str, EngineSession] = {}
        logger.info("Engine manager initialized")

    def create_session(self, session_id: str) -> EngineSession | None:
        if session_id in self.sessions:
            logger.warning("Engine session already exists: %s", session_id)
            return None
        session = EngineSession(self)
        self.sessions[session_id] = session
        logger.info("Engine session created: %s", session_id)
        return session
    
    def get_session(self, session_id: str) -> EngineSession | None:
        return self.sessions.get(session_id)
    
    def has_session(self, session_id: str) -> bool:
        return session_id in self.sessions
    
    def start_session(self, session_id: str, engine_path: str):
        session = self.sessions.get(session_id)
        if session:
            logger.info("Starting engine session '%s': %s", session_id, engine_path)
            session.start(engine_path)
        else:
            logger.warning("Cannot start missing engine session: %s", session_id)
    
    def remove_session(self, session_id: str):
        session = self.sessions.pop(session_id, None)
        if session:
            logger.info("Removing engine session: %s", session_id)
            session.stop()
        else:
            logger.warning("Cannot remove missing engine session: %s", session_id)

    def shutdown(self):
        logger.info("Shutting down %d engine session(s)", len(self.sessions))
        for session in self.sessions.values():
            session.stop()

        self.sessions.clear()
