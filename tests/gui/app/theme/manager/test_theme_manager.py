"""Unit test suite for the ThemeManager controller facade."""

import pytest
from unittest.mock import MagicMock, patch
from gui.app.theme.models.theme_state import ThemeState
from gui.app.theme.manager.theme_manager import ThemeManager


class TestThemeManager:
    """Test suite for the ThemeManager controller facade."""

    @pytest.fixture
    def space_theme(self):
        """Provide a dummy space theme configuration."""
        return ThemeState(
            name="space",
            bg_window="#121212",
            bg_base="#181818",
            bg_panel="#242424",
            border_panel="#303030",
            text_primary="#ffffff",
            text_secondary="#aaaaaa",
            accent_primary="#00ff00",
            accent_secondary="#008800",
            status_searching="#ff0000",
            status_idle="#ffff00",
            status_connected="#00ff00",
            status_disconnected="#777777",
            board_light="#f0d9b5",
            board_dark="#b58863",
            move_highlight="#33ff33",
            selected_square="#ffaa33",
            arrow_color="#ff3333",
            eval_positive="#00aa00",
            eval_negative="#aa0000",
            coord_light="#121212",
            coord_dark="#343434",
        )

    @pytest.fixture
    def mock_service(self, space_theme):
        """Provide a mocked ThemeService instance."""
        with patch("gui.app.theme.manager.theme_manager.ThemeService") as mock_class:
            mock_svc = MagicMock()
            mock_svc.load_presets.return_value = {"space": space_theme}
            mock_svc.apply_stylesheet.return_value = True
            mock_class.return_value = mock_svc
            yield mock_svc

    # --- Initialization Tests ---

    def test_initialization(self, mock_service, space_theme):
        """Verify that initialization loads the default theme and sets up dependencies."""
        # Act
        manager = ThemeManager(parent=None, name="space")

        # Assert
        assert manager._theme_service == mock_service
        assert manager._active_theme == space_theme
        mock_service.load_presets.assert_called_once()
        mock_service.apply_stylesheet.assert_called_once_with(space_theme)

    # --- Load and Apply Theme Tests ---

    def test_load_theme_valid(self, mock_service, space_theme):
        """Verify that loading a valid preset theme updates active theme and applies it."""
        # Arrange
        dark_theme = ThemeState(
            name="dark",
            bg_window="#000000",
            bg_base="#111111",
            bg_panel="#222222",
            border_panel="#333333",
            text_primary="#ffffff",
            text_secondary="#888888",
            accent_primary="#ff00ff",
            accent_secondary="#880088",
            status_searching="#ff0000",
            status_idle="#ffff00",
            status_connected="#00ff00",
            status_disconnected="#777777",
            board_light="#f0d9b5",
            board_dark="#b58863",
            move_highlight="#33ff33",
            selected_square="#ffaa33",
            arrow_color="#ff3333",
            eval_positive="#00aa00",
            eval_negative="#aa0000",
            coord_light="#121212",
            coord_dark="#343434"
        )
        mock_service.load_presets.return_value = {"space": space_theme, "dark": dark_theme}
        manager = ThemeManager(parent=None, name="space")
        mock_service.apply_stylesheet.reset_mock()

        # Act
        manager.load_theme("dark")

        # Assert
        assert manager._active_theme == dark_theme
        mock_service.apply_stylesheet.assert_called_once_with(dark_theme)

    def test_load_theme_invalid(self, mock_service):
        """Verify that loading an invalid theme name does nothing."""
        # Arrange
        manager = ThemeManager(parent=None, name="space")
        mock_service.apply_stylesheet.reset_mock()

        # Act
        manager.load_theme("invalid_theme_name")

        # Assert
        mock_service.apply_stylesheet.assert_not_called()

    def test_load_theme_from_settings(self, mock_service):
        """Verify that custom theme dictionaries are decoded, applied, and active_theme is updated."""
        # Arrange
        manager = ThemeManager(parent=None, name="space")
        custom_dict = {
            "name": "custom",
            "bg_window": "#000000",
            "bg_base": "#050505",
            "bg_panel": "#101010",
            "border_panel": "#151515",
            "text_primary": "#ffffff",
            "text_secondary": "#cccccc",
            "accent_primary": "#0000ff",
            "accent_secondary": "#000088",
            "status_searching": "#ff0000",
            "status_idle": "#ffff00",
            "status_connected": "#00ff00",
            "status_disconnected": "#777777",
            "board_light": "#ffffff",
            "board_dark": "#000000",
            "move_highlight": "#33ff33",
            "selected_square": "#ffaa33",
            "arrow_color": "#ff3333",
            "eval_positive": "#00aa00",
            "eval_negative": "#aa0000",
            "coord_light": "#121212",
            "coord_dark": "#343434",
        }
        mock_service.apply_stylesheet.reset_mock()

        # Act
        manager.load_theme_from_settings(custom_dict)

        # Assert
        assert manager._active_theme.name == "custom"
        assert manager._active_theme.bg_window == "#000000"
        mock_service.apply_stylesheet.assert_called_once_with(manager._active_theme)

    def test_apply_theme_signals(self, mock_service, space_theme, qtbot):
        """Verify that apply_theme emits theme_changed signal on success, but not on failure."""
        # Arrange
        manager = ThemeManager(parent=None, name="space")

        # Act & Assert (Success Case)
        mock_service.apply_stylesheet.return_value = True
        with qtbot.waitSignal(manager.theme_changed, timeout=1000) as blocker:
            manager.apply_theme(space_theme)

        assert blocker.args[0] == space_theme

        # Act & Assert (Failure Case)
        mock_service.apply_stylesheet.return_value = False
        with qtbot.assertNotEmitted(manager.theme_changed):
            manager.apply_theme(space_theme)

    # --- Property Accessor Tests ---

    def test_properties(self, mock_service):
        """Verify available_themes and active_theme_name properties return correct values."""
        # Arrange
        mock_service.available_themes = ["space", "dark", "light"]
        manager = ThemeManager(parent=None, name="space")

        # Act & Assert
        assert manager.available_themes == ["space", "dark", "light"]
        assert manager.active_theme_name == "space"

    # --- Serialization Tests ---

    def test_get_export_state(self, mock_service, space_theme):
        """Verify that get_export_state serializes the active theme correctly."""
        # Arrange
        manager = ThemeManager(parent=None, name="space")

        # Act
        export_state = manager.get_export_state()

        # Assert
        assert export_state["name"] == "space"
        assert export_state["bg_window"] == "#121212"
