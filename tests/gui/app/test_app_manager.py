import pytest
from unittest.mock import MagicMock, patch
import chess
from PySide6.QtCore import QProcess
from gui.app.app_manager import AppManager
from gui.app.game.models.game_state import GameMode, MatchStatus


class TestAppManager:
    """Test suite for the root AppManager coordinator facade."""

    @pytest.fixture(autouse=True)
    def mock_theme_service(self):
        """Automatically mock stylesheet application to avoid modifying the Pytest QApp styling."""
        with patch("gui.app.theme.services.theme_sevice.ThemeService.apply_stylesheet") as mock_apply:
            mock_apply.return_value = True
            yield mock_apply

    @pytest.fixture(autouse=True)
    def mock_preferences_service(self):
        """Automatically patch PreferencesService to prevent disk reads/writes during app manager tests."""
        with patch("gui.app.settings.manager.settings_manager.PreferencesService") as mock_prefs:
            mock_prefs.load.return_value = {}
            mock_prefs.save.return_value = True
            yield mock_prefs

    @pytest.fixture
    def mock_process_and_fs(self):
        """Mock QProcess state transitions and os.path.exists to allow mock connectors to start successfully."""
        with patch("gui.app.engine.services.engine_connector.QProcess") as mock_qproc_class, \
             patch("gui.app.engine.services.engine_connector.os.path.exists") as mock_exists:

            # Setup mock QProcess
            mock_proc = MagicMock()
            mock_proc.state.return_value = QProcess.ProcessState.NotRunning
            mock_proc.waitForStarted.return_value = True
            mock_qproc_class.return_value = mock_proc
            mock_qproc_class.ProcessState = QProcess.ProcessState
            mock_qproc_class.ProcessChannelMode = QProcess.ProcessChannelMode

            # Setup os.path.exists to always approve engine executables
            mock_exists.return_value = True

            yield mock_proc

    # --- Subsystem Initialization & Connection Tests ---

    def test_subsystem_initialization(self):
        """Verify that all major components are instantiated and parented correctly."""
        app = AppManager(parent=None)

        assert app.board is not None
        assert app.engines is not None
        assert app.theme is not None
        assert app.settings is not None
        assert app.game is not None

        # Verify QObject hierarchy parenting
        assert app.board.parent() == app
        assert app.engines.parent() == app
        assert app.theme.parent() == app
        assert app.settings.parent() == app
        assert app.game.parent() == app

    def test_signal_multiplexing_wiring(self):
        """Verify that subsystem notifications successfully bubble up through the AppManager facade."""
        app = AppManager(parent=None)

        # Track multiplexed emissions
        # Use local flags or simple assignments
        theme_flag = []
        app.theme_changed.connect(lambda: theme_flag.append(True))
        
        game_start_flag = []
        app.game_started.connect(lambda: game_start_flag.append(True))

        board_change_list = []
        app.board_state_changed.connect(board_change_list.append)

        # Trigger subsystem signals
        app.theme.theme_changed.emit(MagicMock())
        assert theme_flag == [True]

        app.game.game_started.emit()
        assert game_start_flag == [True]

        mock_node = MagicMock()
        app.board.view_changed.emit(mock_node)
        assert board_change_list == [mock_node]

    # --- Settings Load & Apply Integration Tests ---

    def test_startup_and_settings_application(self, mock_preferences_service):
        """Verify settings loaded from persistent config dynamically updates theme and engine settings."""
        # Setup mock settings file data
        settings_data = {
            "theme": {
                "name": "lichess",
                "bg_window": "#f0f0f0",
                "bg_base": "#ffffff",
                "bg_panel": "#e0e0e0",
                "border_panel": "#cccccc",
                "text_primary": "#000000",
                "text_secondary": "#555555",
                "accent_primary": "#0055ff",
                "accent_secondary": "#0022aa",
                "status_searching": "#ff0000",
                "status_idle": "#aaaa00",
                "status_connected": "#00aa00",
                "status_disconnected": "#555555",
                "board_light": "#f0d9b5",
                "board_dark": "#b58863",
                "move_highlight": "#33ff33",
                "selected_square": "#ffaa33",
                "arrow_color": "#ff3333",
                "eval_positive": "#00aa00",
                "eval_negative": "#aa0000",
                "coord_light": "#121212",
                "coord_dark": "#343434",
            },
            "engines": {
                "Stockfish": {
                    "settings": {
                        "constraint_mode": "depth",
                        "max_depth": 12,
                        "threads": 4,
                        "hash_size": 256,
                        "engine_path": "path/to/stockfish"
                    }
                }
            }
        }
        mock_preferences_service.load.return_value = settings_data

        app = AppManager(parent=None)

        # Assert custom theme settings were applied
        assert app.theme._active_theme.name == "lichess"
        assert app.theme._active_theme.bg_window == "#f0f0f0"

        # Assert custom engines registry settings were configured
        assert "Stockfish" in app.engines.engines.active_engines
        engine_status = app.engines.engines.get_engine("Stockfish")
        assert engine_status is not None
        assert engine_status.settings.max_depth == 12
        assert engine_status.settings.threads == 4
        assert engine_status.settings.engine_path == "path/to/stockfish"

    # --- End-To-End Play Loop Integration Tests ---

    def test_game_play_loop_integration(self, mock_process_and_fs):
        """Verify the complete integration play loop between board, game, and engine managers."""
        app = AppManager(parent=None)
        app.game.mode = GameMode.ENGINE_VS_ENGINE

        # Start game in Engine vs Engine mode
        app.game.start_game(white_path="white/path", black_path="black/path")

        # Both engines must be configured, registered, and running
        assert "White" in app.engines.engines.active_engines
        assert "Black" in app.engines.engines.active_engines

        # Simulate White engine producing bestmove "e2e4"
        app.engines.best_move_updated.emit("White", "e2e4")

        # Verify board applied the move and FEN / turn updated
        assert app.board.get_fen() == "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
        assert app.board._state.turn == chess.BLACK

        # Simulate Black engine producing bestmove "e7e5"
        app.engines.best_move_updated.emit("Black", "e7e5")

        # Verify board applied the second move and FEN / turn updated back to White
        assert app.board.get_fen() == "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
        assert app.board._state.turn == chess.WHITE

    # --- PGN Export Tests ---

    @patch("gui.app.game.services.game_saver.GameSaver.save_pgn")
    def test_export_pgn(self, mock_save_pgn, mock_process_and_fs):
        """Verify export_pgn compiles active engine states, board moves history, and saves PGN."""
        app = AppManager(parent=None)
        app.game.mode = GameMode.ENGINE_VS_ENGINE
        app.game.start_game(white_path="white/path", black_path="black/path")

        mock_save_pgn.return_value = True

        app.export_pgn("exported_match.pgn")

        # Verify GameSaver was called with the active engine specs (White & Black asdict properties)
        mock_save_pgn.assert_called_once()
        saved_filepath = mock_save_pgn.call_args[0][0]
        saved_engine_info = mock_save_pgn.call_args[0][2]

        assert saved_filepath == "exported_match.pgn"
        assert "White" in saved_engine_info
        assert "Black" in saved_engine_info

    # --- Shutdown Teardown Tests ---

    def test_shut_down(self, mock_preferences_service, mock_process_and_fs):
        """Verify shut_down stops matches, exports configurations, and terminates engine processes."""
        app = AppManager(parent=None)
        app.game.mode = GameMode.ENGINE_VS_ENGINE
        app.game.start_game(white_path="white/path", black_path="black/path")

        # Active engines should be running initially
        assert len(app.engines.engines.active_engines) == 2

        app.shut_down()

        # Settings must be saved
        mock_preferences_service.save.assert_called_once()

        # Engine services should be completely shut down
        assert len(app.engines.engines.active_engines) == 0
        assert app.engines._services == {}
