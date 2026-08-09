"""
Unit tests for the EnginesStatusPanel container component.

This module verifies that the EnginesStatusPanel correctly initializes its child
widgets, delegates status updates to them, and bubbles up settings request intents.
"""

from gui.ui.panels.engines_status_panel import EnginesStatusPanel
from gui.ui.panels.single_engine_status import SingleEngineStatus


class TestEnginesStatusPanel:
    """Test suite for the isolated EnginesStatusPanel UI component.

    This suite verifies that initialization via _setup_ui correctly constructs the
    child cards and layouts, and updates sub-widget states as expected.
    """

    def test_initialization_and_theming_hooks(self, qtbot):
        """Verify the widget initializes with two child status cards and correct object name."""
        # Arrange & Act
        panel = EnginesStatusPanel(parent=None)
        qtbot.addWidget(panel)

        # Assert
        assert panel.objectName() == "enginesStatusPanel"
        assert isinstance(panel._white_card, SingleEngineStatus)
        assert isinstance(panel._black_card, SingleEngineStatus)

    def test_update_engine_data(self, qtbot):
        """Verify update_engine_data updates the status of the correct child card."""
        # Arrange
        panel = EnginesStatusPanel(parent=None)
        qtbot.addWidget(panel)

        # Act - Update White engine card
        panel.update_engine_data(engine_role="White", status="Connected", constraint_type="Depth", constraint_value=20)

        # Assert - White card is updated, Black card is untouched
        assert panel._white_card._status_label.text() == "Connected | Depth: 20"
        assert panel._black_card._status_label.text() == "Disconnected"

        # Act - Update Black engine card
        panel.update_engine_data(engine_role="Black", status="Running", constraint_type="Time (ms)", constraint_value=1000)

        # Assert - Black card is updated
        assert panel._black_card._status_label.text() == "Running | Time (ms): 1000"

    def test_update_engine_data_invalid_role(self, qtbot):
        """Verify update_engine_data handles invalid role inputs gracefully."""
        # Arrange
        panel = EnginesStatusPanel(parent=None)
        qtbot.addWidget(panel)

        # Act
        panel.update_engine_data(engine_role="InvalidRole", status="Connected")

        # Assert - Both cards remain at default disconnected states
        assert panel._white_card._status_label.text() == "Disconnected"
        assert panel._black_card._status_label.text() == "Disconnected"

    def test_settings_requested_bubbling(self, qtbot):
        """Verify that child card settings request signals bubble up through settings_requested."""
        # Arrange
        panel = EnginesStatusPanel(parent=None)
        qtbot.addWidget(panel)

        # Act & Assert - Bubbling for White engine settings request
        with qtbot.waitSignal(panel.settings_requested, timeout=1000) as blocker:
            panel._white_card.settings_requested.emit("White")
        assert blocker.args == ["White"]

        # Act & Assert - Bubbling for Black engine settings request
        with qtbot.waitSignal(panel.settings_requested, timeout=1000) as blocker:
            panel._black_card.settings_requested.emit("Black")
        assert blocker.args == ["Black"]
