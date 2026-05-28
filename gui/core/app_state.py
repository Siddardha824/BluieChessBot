# gui/core/app_state.py

import json
from pathlib import Path
from PySide6.QtCore import QObject, Signal
from gui.core import config

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
        
        # Default state variables
        self._active_page = "DASHBOARD"
        self._active_theme = "BLUIE_QUANTUM"
        self._engine_options = {
            "Hash": 64,
            "Threads": 1,
            "Overhead": 10
        }
        self._stats = {
            "total_moves": 0,
            "avg_nps": 0.0,
            "wins": 0,
            "losses": 0,
            "draws": 0
        }
        self._ui_preferences = {
            "show_coordinates": True,
            "sounds_enabled": True
        }
        
        # Load profile dynamically
        self.load_preferences()
        self._initialized = True

    def load_preferences(self) -> None:
        """Loads all persistent parameters from preferences.json, creating it if missing."""
        try:
            pref_path = config.PREFERENCES_PATH
            if pref_path.exists():
                with open(pref_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._active_theme = data.get("active_theme", self._active_theme)
                    self._engine_options = data.get("engine_options", self._engine_options)
                    self._stats = data.get("stats", self._stats)
                    self._ui_preferences = data.get("ui_preferences", self._ui_preferences)
            else:
                self.save_preferences()
        except Exception:
            # Fall back silently to default parameters if read fails
            pass

    def save_preferences(self) -> None:
        """Serializes current states and profiles to preferences.json."""
        try:
            data = {
                "active_theme": self._active_theme,
                "engine_options": self._engine_options,
                "stats": self._stats,
                "ui_preferences": self._ui_preferences
            }
            pref_path = config.PREFERENCES_PATH
            with open(pref_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

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
            self.save_preferences()
            self.signals.theme_changed.emit(theme_name)

    @property
    def engine_options(self) -> dict:
        return self._engine_options

    def update_engine_options(self, options: dict) -> None:
        self._engine_options.update(options)
        self.save_preferences()
        self.signals.engine_config_changed.emit(self._engine_options)

    @property
    def stats(self) -> dict:
        return self._stats

    def update_stats(self, new_stats: dict) -> None:
        self._stats.update(new_stats)
        self.save_preferences()

    @property
    def ui_preferences(self) -> dict:
        return self._ui_preferences

    def update_ui_preferences(self, new_prefs: dict) -> None:
        self._ui_preferences.update(new_prefs)
        self.save_preferences()

# Shared global state instance
app_state = AppState()
