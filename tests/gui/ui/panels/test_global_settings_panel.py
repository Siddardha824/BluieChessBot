"""Unit test suite for the GlobalSettingsPanel UI component."""

import pytest
from PySide6.QtCore import Qt
from unittest.mock import patch
from gui.ui.panels.global_settings_panel import GlobalSettingsPanel


class TestGlobalSettingsPanel:
    """Test suite for the isolated GlobalSettingsPanel UI component."""

    def test_initialization_and_theming_hooks(self, qtbot):
        """Verify widget initializes with correct styling object name."""
        # Act
        panel = GlobalSettingsPanel(parent=None)
        qtbot.addWidget(panel)

        # Assert
        assert panel.objectName() == "settingsPanel"

    def test_set_available_themes(self, qtbot):
        """Verify that set_available_themes populates themes combo and selects active."""
        # Arrange
        panel = GlobalSettingsPanel(parent=None)
        qtbot.addWidget(panel)
        themes = ["space", "dark", "light"]

        # Act
        panel.set_available_themes(themes, "dark")

        # Assert
        assert panel.theme_combo.count() == 3
        assert panel.theme_combo.currentText() == "dark"

    def test_set_initial_values(self, qtbot):
        """Verify that set_initial_values populates themes, active selection, and PGN path."""
        # Arrange
        panel = GlobalSettingsPanel(parent=None)
        qtbot.addWidget(panel)
        themes = ["space", "dark", "light"]

        # Act
        panel.set_initial_values(themes, "light", "/home/user/pgns")

        # Assert
        assert panel.theme_combo.currentText() == "light"
        assert panel.pgn_path_edit.text() == "/home/user/pgns"
        assert panel.pgn_path_edit.toolTip() == "/home/user/pgns"

    def test_browse_for_pgn_dir(self, qtbot):
        """Verify browsing for PGN directory updates the path edit and tooltip."""
        # Arrange
        panel = GlobalSettingsPanel(parent=None)
        qtbot.addWidget(panel)

        # Act
        with patch("gui.ui.panels.global_settings_panel.QFileDialog.getExistingDirectory") as mock_dialog:
            mock_dialog.return_value = "/absolute/path/to/pgn_folder"
            qtbot.mouseClick(panel.browse_btn, Qt.MouseButton.LeftButton)

        # Assert
        mock_dialog.assert_called_once()
        assert panel.pgn_path_edit.toolTip() == "/absolute/path/to/pgn_folder"

    def test_save_intent_emission(self, qtbot):
        """Verify clicking the save button emits global_settings_changed signal with inputs."""
        # Arrange
        panel = GlobalSettingsPanel(parent=None)
        qtbot.addWidget(panel)
        themes = ["space", "dark", "light"]
        panel.set_initial_values(themes, "space", "/home/user/pgns")

        # Act & Assert
        with qtbot.waitSignal(panel.global_settings_changed, timeout=1000) as blocker:
            qtbot.mouseClick(panel.save_btn, Qt.MouseButton.LeftButton)

        assert blocker.args == [{
            "theme_name": "space",
            "game_save_path": "/home/user/pgns"
        }]
