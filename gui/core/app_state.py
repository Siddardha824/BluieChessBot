# gui/core/app_state.py

from PySide6.QtCore import QObject, Signal

class AppStateSignals(QObject):
    """Signals for global application state changes."""
    page_changed = Signal(str)            # Emitted when active tab shifts, passes new tab name
    theme_changed = Signal(str)           # Emitted when theme selection changes, passes new theme name
    engine_config_changed = Signal(dict)  # Emitted when setting overrides occur

class AppState:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppState, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.signals = AppStateSignals()
        
        # Core state variables
        self._active_page = "DASHBOARD"
        self._active_theme = "BLUIE_QUANTUM"
        self._engine_options = {
            "Hash": 64,
            "Threads": 1,
            "Overhead": 10
        }
        self._initialized = True

    @property
    def active_page(self) -> str:
        return self._active_page

    @active_page.setter
    def active_page(self, page_name: str) -> None:
        if self._active_page != page_name:
            self._active_page = page_name
            self.signals.page_changed.emit(page_name)

    @property
    def active_theme(self) -> str:
        return self._active_theme

    @active_theme.setter
    def active_theme(self, theme_name: str) -> None:
        if self._active_theme != theme_name:
            self._active_theme = theme_name
            self.signals.theme_changed.emit(theme_name)

    @property
    def engine_options(self) -> dict:
        return self._engine_options

    def update_engine_options(self, options: dict) -> None:
        self._engine_options.update(options)
        self.signals.engine_config_changed.emit(self._engine_options)

# Shared global state instance
app_state = AppState()
