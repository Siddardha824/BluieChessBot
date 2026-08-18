"""
Single engine status panel component for the chess engine setup user interface.

This module provides the SingleEngineStatus widget, which displays connection
status and the current calculation constraint for a single chess engine (White or Black),
and emits user intents to open the engine-specific settings dialog.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from gui.ui.core import StyledWidget


class SingleEngineStatus(StyledWidget):
    """
    Card widget displaying the connection state and configuration of a single chess engine.

    This component serves as a View Widget in the MVVM architecture, representing
    the status of one specific engine role (e.g., "White" or "Black"). It exposes
    a settings control and delegates dialog requests to parent controllers.

    Styling:
        Relies on the `#engineCard` object name for QSS styling.
    """

    # --- Signals ---

    # Emitted when the user clicks the settings button. Payload: engine_role (str)
    settings_requested = Signal(str)

    # --- UI Initialization ---

    def __init__(self, engine_role: str, parent):
        """Initialize the single engine status card.

        Args:
            engine_role: The role of the engine (e.g., "White" or "Black").
            parent: The parent QWidget.
        """
        self._engine_role = engine_role
        # Must be initialized before super().__init__() since it triggers _setup_ui()
        super().__init__(object_name="engineCard", parent=parent)


    # --- Layout Setup ---

    def _setup_ui(self):
        """Set up the layout structure and instantiate child widgets."""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)

        # --- Header Layout (Role and Status) ---
        self._header_layout = QHBoxLayout()
        self._role_label = QLabel(f"{self._engine_role} Engine")
        
        self._status_label = QLabel("Disconnected")
        
        self._header_layout.addWidget(self._role_label)
        self._header_layout.addStretch()
        self._header_layout.addWidget(self._status_label)

        # --- Controls Layout (Settings Button) ---
        self._controls_layout = QHBoxLayout()
        self._settings_button = QPushButton("Settings...")
        self._settings_button.clicked.connect(self._on_settings_clicked)
        
        self._controls_layout.addStretch()
        self._controls_layout.addWidget(self._settings_button)

        self._layout.addLayout(self._header_layout)
        self._layout.addLayout(self._controls_layout)

    # --- Private Slots (User Intents) ---

    def _on_settings_clicked(self):
        """Emit a request signal to open the settings dialog."""
        self.settings_requested.emit(self._engine_role)

    # --- Public Slots (State Updates) ---

    def update_status(self, connection_status: str, constraint_type: str = "", constraint_value: int = 0):
        """Update the connection status and constraint text label.

        Args:
            connection_status: The base status string (e.g., "Connected", "Running", "Disconnected").
            constraint_type: The type of constraint (e.g., "Depth", "Time (ms)").
            constraint_value: The value of the constraint.
        """
        if constraint_type and constraint_value > 0 and connection_status != "Disconnected":
            # Example Output: "Connected | Depth: 20"
            display_text = f"{connection_status} | {constraint_type}: {constraint_value}"
        else:
            display_text = connection_status
            
        self._status_label.setText(display_text)