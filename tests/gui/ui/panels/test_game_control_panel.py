"""Unit test suite for the GameControlPanel UI component."""

import pytest
from PySide6.QtCore import Qt
from gui.ui.panels.game_control_panel import GameControlPanel


class TestGameControlPanel:
    """Test suite for the isolated GameControlPanel UI component."""

    def test_initialization_and_theming_hooks(self, qtbot):
        """Verify the widget initializes with default state, layout, and styling object names."""
        # Arrange & Act
        panel = GameControlPanel(parent=None)
        qtbot.addWidget(panel)

        # Assert
        assert panel.objectName() == "gameControlPanel"
        assert panel.mode_combo.objectName() == "modeComboBox"
        assert panel.start_btn.objectName() == "actionButtonPrimary"
        assert panel.stop_btn.objectName() == "actionButtonDanger"

        # Verify default enabled state
        assert panel.start_btn.isEnabled() is True
        assert panel.stop_btn.isEnabled() is False
        assert panel.mode_combo.isEnabled() is True

    def test_set_game_modes(self, qtbot):
        """Verify that set_game_modes populates modes combo box and selects current mode."""
        # Arrange
        panel = GameControlPanel(parent=None)
        qtbot.addWidget(panel)
        game_modes = ["Player vs Player", "Player vs Engine", "Engine vs Engine"]

        # Act
        panel.set_game_modes(game_modes, "Player vs Engine")

        # Assert
        assert panel.mode_combo.count() == 3
        assert panel.mode_combo.itemText(0) == "Player vs Player"
        assert panel.mode_combo.itemText(1) == "Player vs Engine"
        assert panel.mode_combo.itemText(2) == "Engine vs Engine"
        assert panel.mode_combo.currentText() == "Player vs Engine"

    def test_update_game_state_active(self, qtbot):
        """Verify that updating game state to active disables inputs and enables stop button."""
        # Arrange
        panel = GameControlPanel(parent=None)
        qtbot.addWidget(panel)

        # Act
        panel.update_game_state(is_active=True)

        # Assert
        assert panel.start_btn.isEnabled() is False
        assert panel.stop_btn.isEnabled() is True
        assert panel.mode_combo.isEnabled() is False

    def test_update_game_state_inactive(self, qtbot):
        """Verify that updating game state to inactive enables inputs and disables stop button."""
        # Arrange
        panel = GameControlPanel(parent=None)
        qtbot.addWidget(panel)
        panel.update_game_state(is_active=True)  # Set active first

        # Act
        panel.update_game_state(is_active=False)

        # Assert
        assert panel.start_btn.isEnabled() is True
        assert panel.stop_btn.isEnabled() is False
        assert panel.mode_combo.isEnabled() is True

    def test_start_requested_signal_emission(self, qtbot):
        """Verify clicking the start button emits the start_requested signal with selected mode."""
        # Arrange
        panel = GameControlPanel(parent=None)
        qtbot.addWidget(panel)
        game_modes = ["Player vs Player", "Player vs Engine"]
        panel.set_game_modes(game_modes, "Player vs Engine")

        # Act & Assert
        with qtbot.waitSignal(panel.start_requested, timeout=1000) as blocker:
            qtbot.mouseClick(panel.start_btn, Qt.MouseButton.LeftButton)

        assert blocker.args == ["Player vs Engine"]

    def test_stop_requested_signal_emission(self, qtbot):
        """Verify clicking the stop button emits the stop_requested signal."""
        # Arrange
        panel = GameControlPanel(parent=None)
        qtbot.addWidget(panel)
        panel.update_game_state(is_active=True)  # Enable stop button

        # Act & Assert
        with qtbot.waitSignal(panel.stop_requested, timeout=1000) as blocker:
            qtbot.mouseClick(panel.stop_btn, Qt.MouseButton.LeftButton)

        assert blocker.args == []
