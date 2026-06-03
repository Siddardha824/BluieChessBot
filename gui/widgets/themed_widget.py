# gui/widgets/themed_widget.py

from PySide6.QtWidgets import QWidget

from gui.utils.logger import get_logger


class ThemedWidget(QWidget):
    """
    Base class for all BluieChessBot widgets.

    Responsibilities:
    - Theme management
    - Consistent initialization lifecycle
    - Logging
    - Optional clear hook
    """

    def __init__(self, theme, parent=None):
        super().__init__(parent)

        self.theme = theme
        self.logger = get_logger(self.__class__.__name__)

        self.logger.debug("Initializing widget")

        self.setup_ui()
        self.connect_signals()
        self.apply_theme()

    # ==========================================================
    # Initialization Hooks
    # ==========================================================

    def setup_ui(self) -> None:
        """Create child widgets and layouts."""
        raise NotImplementedError

    def connect_signals(self) -> None:
        """Connect Qt signals."""
        pass

    # ==========================================================
    # Theme Management
    # ==========================================================

    def apply_theme(self) -> None:
        """Apply stylesheets and theme-dependent properties."""
        raise NotImplementedError

    def update_theme(self, theme) -> None:
        self.theme = theme

        self.logger.debug("Theme updated")

        self.apply_theme()

    # ==========================================================
    # State Management
    # ==========================================================

    def clear(self) -> None:
        """Optional reset hook."""
        pass

    # ==========================================================
    # Logging Helpers
    # ==========================================================

    def log_debug(self, message: str) -> None:
        self.logger.debug(message)

    def log_info(self, message: str) -> None:
        self.logger.info(message)

    def log_warning(self, message: str) -> None:
        self.logger.warning(message)

    def log_error(self, message: str) -> None:
        self.logger.error(message)

    def log_exception(self, message: str) -> None:
        self.logger.exception(message)