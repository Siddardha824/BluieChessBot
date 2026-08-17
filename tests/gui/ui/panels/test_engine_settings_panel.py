"""Unit test suite for the EngineSettingsPanel UI component."""

import pytest
from PySide6.QtCore import Qt
from unittest.mock import patch
from gui.ui.panels.engine_settings_panel import EngineSettingsPanel


class TestEngineSettingsPanel:
    """Test suite for the isolated EngineSettingsPanel UI component."""

    def test_initialization_and_theming_hooks(self, qtbot):
        """Verify widget initializes with correct styling object name."""
        # Act
        panel = EngineSettingsPanel(parent=None)
        qtbot.addWidget(panel)

        # Assert
        assert panel.objectName() == "engineSettingsPanel"
        assert panel.constraint_combo.count() == 3
        assert panel.constraint_spinbox.value() == 20

    def test_set_initial_values(self, qtbot):
        """Verify that set_initial_values correctly updates the widget state."""
        # Arrange
        panel = EngineSettingsPanel(parent=None)
        qtbot.addWidget(panel)

        # Act
        panel.set_initial_values("Time (ms)", 1500, "/usr/bin/stockfish")

        # Assert
        assert panel.constraint_combo.currentText() == "Time (ms)"
        assert panel.constraint_spinbox.value() == 1500
        assert panel.engine_path_edit.text() == "/usr/bin/stockfish"
        assert panel.engine_path_edit.toolTip() == "/usr/bin/stockfish"

    def test_browse_for_engine(self, qtbot):
        """Verify browsing for engine path updates the edit line and tooltip."""
        # Arrange
        panel = EngineSettingsPanel(parent=None)
        qtbot.addWidget(panel)

        # Act
        with patch("gui.ui.panels.engine_settings_panel.QFileDialog.getOpenFileName") as mock_dialog:
            mock_dialog.return_value = ("/absolute/path/to/my/cool/chess_engine.exe", "")
            qtbot.mouseClick(panel.engine_browse_btn, Qt.MouseButton.LeftButton)

        # Assert
        mock_dialog.assert_called_once()
        assert panel.engine_path_edit.toolTip() == "/absolute/path/to/my/cool/chess_engine.exe"

    def test_save_intent_emission(self, qtbot):
        """Verify clicking the save button emits engine_settings_changed signal with inputs."""
        # Arrange
        panel = EngineSettingsPanel(parent=None)
        qtbot.addWidget(panel)
        panel.set_initial_values("Nodes (kN)", 50000, "/usr/bin/stockfish")

        # Act & Assert
        with qtbot.waitSignal(panel.engine_settings_changed, timeout=1000) as blocker:
            qtbot.mouseClick(panel.save_btn, Qt.MouseButton.LeftButton)

        assert blocker.args == [{
            "constraint_mode": "Nodes (kN)",
            "constraint_value": 50000,
            "engine_path": "/usr/bin/stockfish"
        }]
