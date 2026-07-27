import json
import pytest
from unittest.mock import patch
from gui.app.settings.services.preferences_service import PreferencesService


class TestPreferencesService:
    """Test suite for PreferencesService static utility operations."""

    @pytest.fixture
    def mock_preferences_file(self, tmp_path):
        """Fixture to patch PREFERENCES_FILE to point to a temporary test file."""
        temp_file = tmp_path / "config" / "preferences.json"
        with patch("gui.app.settings.services.preferences_service.PREFERENCES_FILE", temp_file):
            yield temp_file

    # --- Load Tests ---

    def test_load_file_not_found(self, mock_preferences_file):
        """Verify load returns None if preferences file does not exist."""
        assert PreferencesService.load() is None

    def test_load_success(self, mock_preferences_file):
        """Verify load reads and parses existing JSON configurations correctly."""
        mock_preferences_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"theme": "dark", "sound": True}
        with open(mock_preferences_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

        loaded_data = PreferencesService.load()
        assert loaded_data == data

    def test_load_malformed_json(self, mock_preferences_file):
        """Verify load fails safely and returns None if JSON content is malformed."""
        mock_preferences_file.parent.mkdir(parents=True, exist_ok=True)
        with open(mock_preferences_file, "w", encoding="utf-8") as f:
            f.write("invalid json { content")

        assert PreferencesService.load() is None

    # --- Save Tests ---

    def test_save_new_configurations(self, mock_preferences_file):
        """Verify save creates new JSON file containing configuration dictionary when settings is None."""
        new_data = {"theme": "light", "volume": 80}

        success = PreferencesService.save(settings=None, new_settings=new_data)

        assert success is True
        assert mock_preferences_file.exists()
        with open(mock_preferences_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        assert saved_data == new_data

    def test_save_merge_existing_configurations(self, mock_preferences_file):
        """Verify save merges new settings into the existing settings dictionary prior to saving."""
        existing_data = {"theme": "dark", "sound": True}
        new_data = {"sound": False, "volume": 50}

        success = PreferencesService.save(settings=existing_data, new_settings=new_data)

        assert success is True
        assert existing_data == {"theme": "dark", "sound": False, "volume": 50}

        with open(mock_preferences_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)
        assert saved_data == existing_data

    def test_save_failure_handling(self, mock_preferences_file):
        """Verify save returns False if writing to file system encounters an exception."""
        mock_preferences_file.parent.mkdir(parents=True, exist_ok=True)
        mock_preferences_file.mkdir()

        success = PreferencesService.save(settings=None, new_settings={"a": 1})
        assert success is False
