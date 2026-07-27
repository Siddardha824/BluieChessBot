import pytest
from gui.app.theme.models.theme_state import ThemeState


class TestThemeState:
    """Test suite for the ThemeState dataclass."""

    @pytest.fixture
    def theme_data(self):
        """Fixture to provide a valid dictionary of theme key-values."""
        return {
            "name": "test_theme",
            "bg_window": "#111111",
            "bg_base": "#222222",
            "bg_panel": "#333333",
            "border_panel": "#444444",
            "text_primary": "#ffffff",
            "text_secondary": "#aaaaaa",
            "accent_primary": "#00ff00",
            "accent_secondary": "#008800",
            "status_searching": "#ff0000",
            "status_idle": "#ffff00",
            "status_connected": "#00ff00",
            "status_disconnected": "#777777",
            "board_light": "#f0d9b5",
            "board_dark": "#b58863",
            "move_highlight": "#33ff33",
            "selected_square": "#ffaa33",
            "arrow_color": "#ff3333",
            "eval_positive": "#00aa00",
            "eval_negative": "#aa0000",
            "coord_light": "#121212",
            "coord_dark": "#343434",
        }

    def test_direct_instantiation(self, theme_data):
        """Verify that ThemeState fields are assigned correctly upon construction."""
        theme = ThemeState(**theme_data)

        assert theme.name == "test_theme"
        assert theme.bg_window == "#111111"
        assert theme.bg_base == "#222222"
        assert theme.board_light == "#f0d9b5"
        assert theme.board_dark == "#b58863"

    def test_from_dict_filtering(self, theme_data):
        """Verify that from_dict successfully parses valid fields and filters out invalid keys."""
        extended_data = theme_data.copy()
        extended_data["extra_unsupported_key"] = "some_value"
        extended_data["another_unsupported_key"] = "#123456"

        theme = ThemeState.from_dict(extended_data)

        assert theme.name == "test_theme"
        assert theme.bg_window == "#111111"
        assert not hasattr(theme, "extra_unsupported_key")
