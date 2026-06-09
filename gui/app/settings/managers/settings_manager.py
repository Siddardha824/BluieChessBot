from PySide6.QtCore import QObject
from ..services.preferences_service import PreferencesService
from gui.utils import get_logger


logger = get_logger(__name__)

class SettingsManager(QObject):
    _instance = None

    @classmethod
    def get_instance(cls) -> 'SettingsManager':
        if cls._instance is None:
            logger.info("Creating settings manager singleton")
            cls._instance = SettingsManager()
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Settings manager initialized")


