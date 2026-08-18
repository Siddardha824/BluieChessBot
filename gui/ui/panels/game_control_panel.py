"""
Game control panel widget providing controls to start and stop games and select game modes.

This module provides the GameControlPanel class, which enables users to configure
the game mode via a dropdown and trigger start/stop events. It communicates interactions
upwards via Qt signals.
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton

from gui.ui.core import StyledWidget


class GameControlPanel(StyledWidget):
    """
    Panel widget containing chess game start, stop, and mode controls.

    This panel houses a game mode selection combo box along with action buttons
    to start and stop chess games. It communicates user intents upwards using
    custom Qt signals and updates its visual state dynamically based on active
    game status.

    Signals:
        start_requested (Signal[str]): Emitted when the start button is clicked.
            Payload: The selected game mode string.
        stop_requested (Signal): Emitted when the stop button is clicked.

    Styling:
        Relies on the `#gameControlPanel` object name for QSS styling.
    """

    # --- Signals ---

    # Emitted when the user requests to start a game. Payload: selected_mode (str)
    start_requested = Signal(str)

    # Emitted when the user requests to stop the running game.
    stop_requested = Signal()

    # --- UI Initialization ---

    def __init__(self, parent):
        """Initialize the game control panel.

        Args:
            parent: The parent QWidget.
        """
        super().__init__(object_name="gameControlPanel", parent=parent)

    # --- Layout Setup ---

    def _setup_ui(self):
        """Set up the layout, dropdowns, and button widgets."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        mode_layout = QVBoxLayout()
        mode_layout.setSpacing(5)

        mode_label = QLabel("Game Mode: ")
        mode_label.setObjectName("headerLabel")

        self.mode_combo = QComboBox()
        self.mode_combo.setObjectName("modeComboBox")
        # Initialize with an empty list of game modes
        self.mode_combo.addItems([])

        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)

        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("actionButtonPrimary")

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("actionButtonDanger")
        self.stop_btn.setEnabled(False)

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(mode_layout)
        layout.addLayout(button_layout)
        layout.addStretch()

        self._connect_signals()

    def _connect_signals(self):
        """Connect UI widget event handlers to slots and signals."""
        self.start_btn.clicked.connect(self._on_start_clicked)
        self.stop_btn.clicked.connect(self.stop_requested.emit)

    # --- Private Slots (User Intents) ---

    def _on_start_clicked(self):
        """Handle start button clicks by emitting the start_requested signal."""
        selected_mode = self.mode_combo.currentText()
        self.start_requested.emit(selected_mode)

    # --- Public Slots (State Updates) ---

    def set_game_modes(self, game_modes: list[str], current_mode: str):
        """Populate the game modes dropdown and set the active selection.

        Args:
            game_modes: A list of available game mode names.
            current_mode: The game mode that should be set as selected.
        """
        self.mode_combo.clear()
        self.mode_combo.addItems(game_modes)
        self.mode_combo.setCurrentText(current_mode)

    def update_game_state(self, is_active: bool):
        """Update widget enablement states based on whether a game is active.

        Args:
            is_active: True if a chess game is currently running, False otherwise.
        """
        self.start_btn.setEnabled(not is_active)
        self.stop_btn.setEnabled(is_active)
        self.mode_combo.setEnabled(not is_active)