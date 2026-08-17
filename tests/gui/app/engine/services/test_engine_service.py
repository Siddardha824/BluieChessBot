import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QProcess
from gui.app.engine.models.engine_status import EngineStatus
from gui.app.engine.services.engine_service import EngineService


class TestEngineService:
    """Test suite for the EngineService chess engine lifecycle coordinator."""

    @pytest.fixture
    def mock_connector(self):
        """Fixture to patch and mock the EngineConnector inside EngineService."""
        with patch("gui.app.engine.services.engine_service.EngineConnector") as mock_class:
            mock_conn = MagicMock()
            mock_process = MagicMock()
            mock_conn.process = mock_process
            mock_class.return_value = mock_conn
            yield mock_conn

    @pytest.fixture
    def engine_status(self):
        """Fixture to provide a fresh, isolated EngineStatus model."""
        return EngineStatus(parent=None)

    @pytest.fixture
    def service(self, engine_status, mock_connector):
        """Fixture to provide a fresh EngineService instance using the mocked connector."""
        return EngineService(engine_status, parent=None)

    # --- Initialization Tests ---

    def test_initialization(self, mock_connector, engine_status, service):
        """Verify that the engine service wires all connector signals to internal slots."""
        assert service.status == engine_status
        assert service._connector == mock_connector

        mock_connector.stdout_received.connect.assert_called_once_with(service._on_stdout)
        mock_connector.process_finished.connect.assert_called_once_with(service._on_process_finished)
        mock_connector.process_error.connect.assert_called_once_with(service._on_process_error)
        mock_connector.process.stateChanged.connect.assert_called_once_with(service._on_process_state_changed)

    # --- Process State Changed Tests ---

    @pytest.mark.parametrize(
        "qprocess_state, expected_status_string",
        [
            (QProcess.ProcessState.NotRunning, "NotRunning"),
            (QProcess.ProcessState.Starting, "Starting"),
            (QProcess.ProcessState.Running, "Running"),
        ]
    )
    def test_on_process_state_changed(self, qprocess_state, expected_status_string, service, engine_status):
        """Verify that the model's connection status updates reactively on state transitions."""
        received_updates = 0
        def on_updated():
            nonlocal received_updates
            received_updates += 1
        engine_status.info.info_updated.connect(on_updated)

        service._on_process_state_changed(qprocess_state)

        assert engine_status.info.connection_status == expected_status_string
        assert received_updates == 1

    # --- Start Subprocess Tests ---

    def test_start_success_with_path(self, mock_connector, engine_status, service):
        """Verify start updates search status and sends uci handshake command on success."""
        engine_status.settings.engine_path = "path/to/engine"
        mock_connector.start.return_value = True

        assert service.start("fallback/path") is True
        assert engine_status.settings.engine_path == "path/to/engine"
        assert engine_status.info.search_status == "Connecting"
        mock_connector.start.assert_called_once_with("path/to/engine")
        mock_connector.send.assert_called_once_with("uci")

    def test_start_success_with_fallback(self, mock_connector, engine_status, service):
        """Verify start uses fallback_path if configured path is empty."""
        engine_status.settings.engine_path = ""
        mock_connector.start.return_value = True

        assert service.start("fallback/path") is True
        assert engine_status.settings.engine_path == "fallback/path"
        mock_connector.start.assert_called_once_with("fallback/path")
        mock_connector.send.assert_called_once_with("uci")

    def test_start_failure(self, mock_connector, engine_status, service):
        """Verify start returns False and does not send commands if connector fails to start."""
        engine_status.settings.engine_path = "invalid/path"
        mock_connector.start.return_value = False

        assert service.start() is False
        assert engine_status.info.search_status == "Offline"
        mock_connector.start.assert_called_once_with("invalid/path")
        mock_connector.send.assert_not_called()

    # --- Lifecycle and Send Tests ---

    def test_stop(self, mock_connector, service):
        """Verify stop delegates to connector."""
        service.stop()
        mock_connector.stop.assert_called_once()

    def test_send(self, mock_connector, service):
        """Verify send delegates to connector."""
        service.send("test_command")
        mock_connector.send.assert_called_once_with("test_command")

    # --- Update Settings Tests ---

    def test_update_settings_valid(self, engine_status, service, qtbot, mock_connector):
        """Verify update_settings successfully updates valid fields on settings model, notifies, and syncs options if running."""
        mock_connector.process.state.return_value = QProcess.ProcessState.Running

        with qtbot.waitSignal(engine_status.settings.settings_updated, timeout=1000):
            service.update_settings(threads=4, hash_size=128)

        assert engine_status.settings.threads == 4
        assert engine_status.settings.hash_size == 128
        mock_connector.send.assert_any_call("setoption name Threads value 4")
        mock_connector.send.assert_any_call("setoption name Hash value 128")
        mock_connector.send.assert_any_call("isready")
        assert engine_status.info.connection_status == "SyncingSettings"

        # Simulate readyok response
        service._on_stdout("readyok")
        assert engine_status.info.connection_status == "Running"

    def test_update_settings_valid_not_running(self, engine_status, service, qtbot, mock_connector):
        """Verify update_settings notifies but does not send setoptions if engine is not running."""
        mock_connector.process.state.return_value = QProcess.ProcessState.NotRunning

        with qtbot.waitSignal(engine_status.settings.settings_updated, timeout=1000):
            service.update_settings(threads=4, hash_size=128)

        assert engine_status.settings.threads == 4
        mock_connector.send.assert_not_called()

    def test_update_settings_invalid_ignored(self, engine_status, service):
        """Verify update_settings ignores unknown setting attributes gracefully."""
        service.update_settings(non_existent_key="value", threads=2)
        assert engine_status.settings.threads == 2


    # --- Utility Methods Tests ---

    def test_is_running(self, mock_connector, service):
        """Verify is_running maps to connector process state."""
        mock_connector.process.state.return_value = QProcess.ProcessState.Running
        assert service.is_running() is True

        mock_connector.process.state.return_value = QProcess.ProcessState.NotRunning
        assert service.is_running() is False

    def test_is_ready(self, mock_connector, service):
        """Verify is_ready sends isready command."""
        service.is_ready()
        mock_connector.send.assert_called_once_with("isready")

    def test_set_position_startpos(self, mock_connector, service):
        """Verify set_position_startpos sends position startpos command."""
        service.set_position_startpos()
        mock_connector.send.assert_called_once_with("position startpos")

    def test_set_position_fen(self, mock_connector, service):
        """Verify set_position_fen sends custom FEN command."""
        service.set_position_fen("fen_string")
        mock_connector.send.assert_called_once_with("position fen fen_string")

    def test_set_options(self, mock_connector, engine_status, service):
        """Verify set_options reads model threads and hash values and sends setoption commands."""
        engine_status.settings.threads = 8
        engine_status.settings.hash_size = 256

        # Test setting both (None parameter)
        service.set_options()
        mock_connector.send.assert_any_call("setoption name Threads value 8")
        mock_connector.send.assert_any_call("setoption name Hash value 256")
        mock_connector.send.assert_any_call("isready")
        assert mock_connector.send.call_count == 4

        # Reset mock calls
        mock_connector.send.reset_mock()

        # Test setting threads only
        service.set_options("threads")
        mock_connector.send.assert_any_call("setoption name Threads value 8")
        mock_connector.send.assert_any_call("isready")
        assert mock_connector.send.call_count == 2

        # Reset mock calls
        mock_connector.send.reset_mock()

        # Test setting hash_size only
        service.set_options("hash_size")
        mock_connector.send.assert_any_call("setoption name Hash value 256")
        mock_connector.send.assert_any_call("isready")
        assert mock_connector.send.call_count == 2

        # Reset mock calls
        mock_connector.send.reset_mock()

        # Test setting invalid option
        service.set_options("invalid_option")
        mock_connector.send.assert_not_called()



    # --- Search Commands Tests ---

    @pytest.mark.parametrize(
        "mode, setup_func, expected_command",
        [
            ("depth", lambda s: setattr(s.settings, "max_depth", 15), "go depth 15"),
            ("time", lambda s: setattr(s.settings, "max_time_ms", 5000), "go movetime 5000"),
            ("nodes", lambda s: setattr(s.settings, "max_nodes", 25000), "go nodes 25000"),
            ("infinite", lambda s: None, "go infinite"),
        ]
    )
    def test_go_dispatch(self, mode, setup_func, expected_command, mock_connector, engine_status, service):
        """Verify go dispatches correct command and updates search status based on constraint mode."""
        engine_status.settings.constraint_mode = mode
        setup_func(engine_status)

        service.go()

        assert engine_status.info.search_status == "Searching"
        mock_connector.send.assert_called_once_with(expected_command)

    def test_go_unrecognized_mode(self, mock_connector, engine_status, service):
        """Verify go logs warning and does nothing if constraint mode is unrecognized."""
        # Force invalid constraint mode bypass validation by modifying private field
        service.status.settings._constraint_mode = "invalid"

        service.go()

        assert engine_status.info.search_status == "Offline"
        mock_connector.send.assert_not_called()

    def test_stop_search(self, mock_connector, engine_status, service):
        """Verify stop_search sets search status to Idle and sends stop command."""
        engine_status.info.search_status = "Searching"

        service.stop_search()

        assert engine_status.info.search_status == "Idle"
        mock_connector.send.assert_called_once_with("stop")

    # --- Incoming stdout Slot Tests ---

    def test_on_stdout_uciok(self, engine_status, service):
        """Verify uciok updates search status to Idle."""
        engine_status.info.search_status = "Connecting"

        service._on_stdout("uciok")

        assert engine_status.info.search_status == "Idle"

    def test_on_stdout_readyok(self, service):
        """Verify readyok emits the engine_ready signal."""
        received_ready = False
        def on_ready():
            nonlocal received_ready
            received_ready = True
        service.engine_ready.connect(on_ready)

        service._on_stdout("readyok")

        assert received_ready is True

    def test_on_stdout_id(self, engine_status, service):
        """Verify id name and author updates info model attributes."""
        service._on_stdout("id name Stockfish 16")
        assert engine_status.info.name == "Stockfish 16"

        service._on_stdout("id author The Stockfish Developers")
        assert engine_status.info.author == "The Stockfish Developers"

    def test_on_stdout_info(self, engine_status, service):
        """Verify info line parses and triggers analysis model updates."""
        received_updates = 0
        def on_updated():
            nonlocal received_updates
            received_updates += 1
        engine_status.analysis.analysis_state_changed.connect(on_updated)

        service._on_stdout("info depth 8 score cp 80 nodes 500 nps 1000")

        assert engine_status.analysis.depth == 8
        assert engine_status.analysis.score == 0.8
        assert engine_status.analysis.nodes == 500
        assert engine_status.analysis.nps == 1000
        assert received_updates == 1

    def test_on_stdout_bestmove(self, engine_status, service):
        """Verify bestmove updates best_move, sets status to Idle, and emits signal."""
        engine_status.info.search_status = "Searching"

        received_best_move = None
        def on_best_move(move):
            nonlocal received_best_move
            received_best_move = move
        service.best_move_updated.connect(on_best_move)

        service._on_stdout("bestmove e2e4 ponder e7e5")

        assert engine_status.analysis.best_move == "e2e4"
        assert engine_status.info.search_status == "Idle"
        assert received_best_move == "e2e4"

    # --- Subprocess Lifecycle Callback Tests ---

    def test_on_process_finished(self, engine_status, service):
        """Verify process termination updates search status and emits stopped signal."""
        engine_status.info.search_status = "Idle"

        received_stopped = []
        service.engine_stopped.connect(lambda code, status: received_stopped.append((code, status)))

        service._on_process_finished(0, QProcess.ExitStatus.NormalExit)

        assert engine_status.info.search_status == "Offline"
        assert received_stopped == [(0, QProcess.ExitStatus.NormalExit)]

    def test_on_process_error(self, engine_status, service):
        """Verify process error updates statuses and emits error signal."""
        engine_status.info.connection_status = "Running"
        engine_status.info.search_status = "Searching"

        received_errors = []
        service.engine_error.connect(received_errors.append)

        service._on_process_error("Process crashed")

        assert engine_status.info.connection_status == "Error"
        assert engine_status.info.search_status == "Offline"
        assert received_errors == ["Process crashed"]

    def test_on_stdout_invalid_line(self, engine_status, service):
        """Verify on_stdout ignores invalid or unrecognized lines without modifying status."""
        # Arrange
        engine_status.info.search_status = "Searching"

        # Act
        service._on_stdout("invalid_line_garbage")

        # Assert
        assert engine_status.info.search_status == "Searching"

