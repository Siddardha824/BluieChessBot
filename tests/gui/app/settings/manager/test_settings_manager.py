import pytest
from unittest.mock import patch, MagicMock
from gui.app.settings.manager.settings_manager import SettingsManager


class TestSettingsManager:
    """Test suite for the SettingsManager reactive controller facade."""

    # --- Initialization & Load Tests ---

    @patch("gui.app.settings.manager.settings_manager.PreferencesService")
    def test_initialization_with_loaded_settings(self, mock_prefs):
        """Verify that initialization loads existing settings and emits the loaded signal."""
        mock_data = {"theme": "dark", "sound": True}
        mock_prefs.load.return_value = mock_data

        received_data = None
        def on_loaded(data):
            nonlocal received_data
            received_data = data

        class SpiedSettingsManager(SettingsManager):
            def load(self):
                self.loaded.connect(on_loaded)
                super().load()

        manager = SpiedSettingsManager(parent=None)

        assert manager._settings == mock_data
        assert received_data == mock_data
        mock_prefs.load.assert_called_once()


    @patch("gui.app.settings.manager.settings_manager.PreferencesService")
    def test_initialization_with_no_settings(self, mock_prefs, qtbot):
        """Verify that initialization handles missing configuration files gracefully without emitting signals."""
        mock_prefs.load.return_value = None

        # Manager should construct cleanly without emitting loaded signal
        manager = SettingsManager(parent=None)

        assert manager._settings is None
        mock_prefs.load.assert_called_once()

    # --- Save Tests ---

    @patch("gui.app.settings.manager.settings_manager.PreferencesService")
    def test_save_success(self, mock_prefs, qtbot):
        """Verify that save updates configurations and emits the saved signal on success."""
        mock_prefs.load.return_value = {"theme": "dark"}
        manager = SettingsManager(parent=None)

        mock_prefs.save.return_value = True

        with qtbot.waitSignal(manager.saved, timeout=1000):
            manager.save(theme="light", volume=100)

        mock_prefs.save.assert_called_once_with({"theme": "dark"}, {"theme": "light", "volume": 100})

    @patch("gui.app.settings.manager.settings_manager.PreferencesService")
    def test_save_failure(self, mock_prefs, qtbot):
        """Verify that save does not emit the saved signal if preferences storage fails."""
        mock_prefs.load.return_value = {"theme": "dark"}
        manager = SettingsManager(parent=None)

        mock_prefs.save.return_value = False

        with qtbot.assertNotEmitted(manager.saved):
            manager.save(theme="light")

        mock_prefs.save.assert_called_once_with({"theme": "dark"}, {"theme": "light"})

    @patch("gui.app.settings.manager.settings_manager.PreferencesService")
    def test_save_empty_ignored(self, mock_prefs, qtbot):
        """Verify that calling save with no arguments does not execute storage transactions or emit signals."""
        mock_prefs.load.return_value = {"theme": "dark"}
        manager = SettingsManager(parent=None)

        with qtbot.assertNotEmitted(manager.saved):
            manager.save()

        mock_prefs.save.assert_not_called()
