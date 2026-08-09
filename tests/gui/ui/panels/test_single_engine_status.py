"""
Unit tests for the SingleEngineStatus panel component.

This module verifies that the SingleEngineStatus widget correctly initializes,
updates its status labels, and emits user interface intents via signals.
"""

import pytest
from PySide6.QtCore import Qt
from gui.ui.panels.single_engine_status import SingleEngineStatus


class TestSingleEngineStatus:
    """Test suite for the isolated SingleEngineStatus UI component.

    This suite verifies that initialization via _setup_ui sets up child widgets
    correctly and updates status labels, button properties, and signal emissions.
    """

    def test_initialization_and_theming_hooks(self, qtbot):
        """Verify the widget initializes with default text and correct QSS object name."""
        # Arrange & Act
        card = SingleEngineStatus(engine_role="White", parent=None)
        qtbot.addWidget(card)

        # Assert
        assert card.objectName() == "engineCard"
        assert card._role_label.text() == "White Engine"
        assert card._status_label.text() == "Disconnected"
        assert card._settings_button.text() == "Settings..."

    def test_update_status_disconnected_ignores_constraints(self, qtbot):
        """Verify that updating status to Disconnected ignores constraints."""
        # Arrange
        card = SingleEngineStatus(engine_role="Black", parent=None)
        qtbot.addWidget(card)

        # Act
        card.update_status(connection_status="Disconnected", constraint_type="Depth", constraint_value=20)

        # Assert
        assert card._status_label.text() == "Disconnected"

    def test_update_status_connected_with_valid_constraints(self, qtbot):
        """Verify that status updates with valid constraints include constraint details."""
        # Arrange
        card = SingleEngineStatus(engine_role="White", parent=None)
        qtbot.addWidget(card)

        # Act
        card.update_status(connection_status="Connected", constraint_type="Depth", constraint_value=15)

        # Assert
        assert card._status_label.text() == "Connected | Depth: 15"

    def test_update_status_connected_without_constraints(self, qtbot):
        """Verify that status updates without constraints or with invalid constraint values omit details."""
        # Arrange
        card = SingleEngineStatus(engine_role="Black", parent=None)
        qtbot.addWidget(card)

        # Act & Assert - Case 1: No constraint type
        card.update_status(connection_status="Connected", constraint_value=15)
        assert card._status_label.text() == "Connected"

        # Act & Assert - Case 2: Constraint value is zero
        card.update_status(connection_status="Connected", constraint_type="Depth", constraint_value=0)
        assert card._status_label.text() == "Connected"

        # Act & Assert - Case 3: Constraint value is negative
        card.update_status(connection_status="Connected", constraint_type="Depth", constraint_value=-5)
        assert card._status_label.text() == "Connected"

    def test_settings_requested_intent_emission(self, qtbot):
        """Verify that clicking the settings button emits settings_requested with the correct role."""
        # Arrange
        card = SingleEngineStatus(engine_role="White", parent=None)
        qtbot.addWidget(card)

        # Act & Assert
        with qtbot.waitSignal(card.settings_requested, timeout=1000) as blocker:
            qtbot.mouseClick(card._settings_button, Qt.MouseButton.LeftButton)

        assert blocker.args == ["White"]
