from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from ..constants import THEMES
from gui.app.shared import (
    SPACE_DOWN_ARROW_ICON,
    SPACE_SPIN_DOWN_ARROW_ICON,
    SPACE_SPIN_UP_ARROW_ICON,
    STYLES_DIR,
)

class ThemeManager(QObject):

    theme_changed = Signal(str)

    def __init__(
        self,
        app: QApplication
    ):
        super().__init__()

        self._app = app
        self._styles_dir = STYLES_DIR

        self._active_theme = "space"

    @property
    def active_theme(self) -> str:
        return self._active_theme

    @property
    def preset(self):
        return THEMES[self._active_theme]

    def apply_theme(self, theme_name: str):

        qss_file = self._styles_dir / f"{theme_name}.qss"

        with open(qss_file, "r", encoding="utf-8") as f:
            stylesheet = f.read()

        stylesheet = stylesheet.replace(
            "__SPACE_DOWN_ARROW_ICON__",
            SPACE_DOWN_ARROW_ICON.as_posix(),
        )
        stylesheet = stylesheet.replace(
            "__SPACE_SPIN_UP_ARROW_ICON__",
            SPACE_SPIN_UP_ARROW_ICON.as_posix(),
        )
        stylesheet = stylesheet.replace(
            "__SPACE_SPIN_DOWN_ARROW_ICON__",
            SPACE_SPIN_DOWN_ARROW_ICON.as_posix(),
        )
        self._app.setStyleSheet(stylesheet)

        self._active_theme = theme_name

        self.theme_changed.emit(theme_name)
