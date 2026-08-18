"""
Engines status panel component for coordinating multiple engine card views.

This module provides the EnginesStatusPanel container class, which aggregates individual
SingleEngineStatus widgets and forwards user settings requests to the parent layout.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QLabel
from gui.ui.core import StyledWidget

from .single_engine_status import SingleEngineStatus


class EnginesStatusPanel(StyledWidget):
    """
    Panel widget containing connection cards for both White and Black chess engines.

    This class serves as a View Widget in the MVVM architecture, grouping engine status
    views together and multiplexing engine settings requests.

    Signals:
        settings_requested (Signal): Emitted when a request to open engine settings is made. 
                                     Payload: engine_role (str).

    Styling:
        Relies on the `#enginesStatusPanel` object name for QSS styling.
    """

    # --- Signals ---

    # Emitted when the user requests to configure an engine. Payload: engine_role (str, "White" | "Black")
    settings_requested = Signal(str)

    # --- UI Initialization ---

    def __init__(self, parent):
        """Initialize the engines status panel container.

        Args:
            parent: The parent QWidget.
        """
        super().__init__(object_name="enginesStatusPanel", parent=parent)

        # Wire up child card signals after widgets have been constructed in _setup_ui
        self._white_card.settings_requested.connect(self.settings_requested.emit)
        self._black_card.settings_requested.connect(self.settings_requested.emit)

    # --- Layout Setup ---

    def _setup_ui(self):
        """Set up the layout and add child engine cards."""
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(15)

        # Child status cards must be instantiated prior to being added to the layout
        self._white_card = SingleEngineStatus(engine_role="White", parent=self)
        self._black_card = SingleEngineStatus(engine_role="Black", parent=self)

        title = QLabel("<b>Engine Status</b>")
        self._layout.addWidget(title)
        self._layout.addWidget(self._white_card)
        self._layout.addWidget(self._black_card)
        self._layout.addStretch()

    # --- Public Slots (State Updates) ---

    def update_engine_data(self, engine_role: str, status: str, constraint_type: str = "", constraint_value: int = 0):
        """Update connection status and constraint info for a specific engine.

        Args:
            engine_role: The targeted engine role ("White" or "Black").
            status: The connection state description (e.g., "Connected", "Running", "Disconnected").
            constraint_type: The type of constraint (e.g., "Depth", "Time (ms)"). Defaults to empty string.
            constraint_value: The value of the constraint. Defaults to 0.
        """
        if engine_role == "White":
            self._white_card.update_status(status, constraint_type, constraint_value)
        elif engine_role == "Black":
            self._black_card.update_status(status, constraint_type, constraint_value)