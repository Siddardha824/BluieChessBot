from PySide6.QtCore import QObject

from ..sessions.engine_session import EngineSession

class EngineManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.sessions: dict[str, EngineSession] = {}

    def create_session(self, session_id: str) -> EngineSession | None:
        if session_id in self.sessions:
            return None
        session = EngineSession(self)
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> EngineSession | None:
        return self.sessions.get(session_id)
    
    def has_session(self, session_id: str) -> bool:
        return session_id in self.sessions
    
    def start_session(self, session_id: str, engine_path: str):
        session = self.sessions.get(session_id)
        if session:
            session.start(engine_path)
    
    def remove_session(self, session_id: str):
        session = self.sessions.pop(session_id, None)
        if session:
            session.stop()

    def shutdown(self):
        for session in self.sessions.values():
            session.stop()

        self.sessions.clear()
