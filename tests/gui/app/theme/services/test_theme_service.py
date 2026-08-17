"""Unit test suite for the ThemeService stylesheet processor."""

import pytest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from gui.app.theme.models.theme_state import ThemeState
from gui.app.theme.services.theme_service import ThemeService


class TestThemeService:
    """Test suite for the ThemeService stylesheet processor."""

    @pytest.fixture
    def theme_service(self):
        """Provide a fresh ThemeService instance."""
        # Arrange / Act / Assert
        return ThemeService()

    @pytest.fixture
    def mock_qss_file(self, tmp_path):
        """Write a temporary placeholder QSS template."""
        # Arrange
        qss_file = tmp_path / "stylesheet.qss"
        content = (
            "QWidget { background-color: {{ bg_window }}; color: {{ text_primary }}; }\n"
            "QComboBox::drop-down { image: url(__SPACE_DOWN_ARROW_ICON__); }"
        )
        qss_file.write_text(content, encoding="utf-8")
        return qss_file

    @pytest.fixture
    def test_theme(self):
        """Provide a minimal ThemeState for testing."""
        # Arrange / Act / Assert
        return ThemeState(
            name="space_test",
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

    # --- Load Presets Tests ---

    def test_load_presets(self, theme_service):
        """Verify that presets dictionary is parsed and contains default themes."""
        # Act
        presets = theme_service.load_presets()

        # Assert
        assert isinstance(presets, dict)
        assert "space" in presets
        assert isinstance(presets["space"], ThemeState)

    def test_available_themes(self, theme_service):
        """Verify that available_themes property returns the list of preset themes."""
        # Act
        themes = theme_service.available_themes

        # Assert
        assert isinstance(themes, list)
        assert "space" in themes

    # --- Apply Stylesheet Tests ---

    def test_apply_stylesheet_success(self, theme_service, test_theme, mock_qss_file):
        """Verify that apply_stylesheet replaces placeholders and binds QSS to QApplication."""
        # Arrange
        theme_service._qss = mock_qss_file

        # Act
        result = theme_service.apply_stylesheet(test_theme)

        # Assert
        assert result is True

        # Verify stylesheet on the actual QApplication instance
        app = QApplication.instance()
        called_qss = app.styleSheet()
        assert "background-color: #121212" in called_qss
        assert "color: #ffffff" in called_qss
        assert "space_down_arrow.svg" in called_qss

        # Clean up stylesheet
        app.setStyleSheet("")

    def test_apply_stylesheet_file_not_found(self, theme_service, test_theme, tmp_path):
        """Verify apply_stylesheet returns False safely if stylesheet file path does not exist."""
        # Arrange
        theme_service._qss = tmp_path / "missing.qss"

        # Act
        result = theme_service.apply_stylesheet(test_theme)

        # Assert
        assert result is False

    def test_apply_stylesheet_app_not_running(self, theme_service, test_theme, mock_qss_file):
        """Verify apply_stylesheet returns False if QApplication instance is not available."""
        # Arrange
        theme_service._qss = mock_qss_file

        # Act & Assert
        with patch("gui.app.theme.services.theme_service.QApplication.instance") as mock_instance:
            mock_instance.return_value = None

            result = theme_service.apply_stylesheet(test_theme)
            assert result is False
