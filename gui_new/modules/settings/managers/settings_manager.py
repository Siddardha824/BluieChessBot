from PySide6.QtCore import QObject
from ..services.preferences_service import PreferencesService

class SettingsManager(QObject):
    _instance = None

    @classmethod
    def get_instance(cls) -> 'SettingsManager':
        if cls._instance is None:
            cls._instance = SettingsManager()
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)


