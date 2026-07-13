import dataclasses
from PySide6.QtWidgets import QApplication
from gui.app.shared import (
    SPACE_DOWN_ARROW_ICON,
    SPACE_SPIN_DOWN_ARROW_ICON,
    SPACE_SPIN_UP_ARROW_ICON,
    STYLESHEET
)

from .constants import PRESET_THEMES
from ..models.theme_state import ThemeState
from gui.utils import get_logger

logger = get_logger(__name__)

class ThemeService:
    def __init__(self, app: QApplication):
        self._app = app
        self._qss = STYLESHEET

    def load_presets(self) -> dict[str, ThemeState]:
        return PRESET_THEMES

    def apply_stylesheet(self, theme: ThemeState):

        try:
            with open(self._qss, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
        except Exception:
            logger.exception("Failed to load stylesheet.qss")
            return False

        theme_dic = dataclasses.asdict(theme)

        for key, value in theme_dic.items():
            if value is not None:
                placeholder = f"{{{{ {key} }}}}"
                stylesheet.replace(placeholder, str(value))

        stylesheet.replace("__SPACE_DOWN_ARROW_ICON__", SPACE_DOWN_ARROW_ICON.as_posix())
        stylesheet.replace("__SPACE_SPIN_UP_ARROW_ICON__", SPACE_SPIN_UP_ARROW_ICON.as_posix())
        stylesheet.replace("__SPACE_SPIN_DOWN_ARROW_ICON__", SPACE_SPIN_DOWN_ARROW_ICON.as_posix())

        self._app.setStyleSheet(stylesheet)
        logger.info("Theme set to %s", theme.name)

        return True

        