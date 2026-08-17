import pytest
from unittest.mock import MagicMock, patch
from PySide6.QtCore import QObject, QProcess, Signal
from gui.app.engine.manager.engine_manager import EngineManager


class MockEngineService(QObject):
    """Mock implementation of EngineService inheriting from QObject to support real Qt signals."""

    engine_ready = Signal()
    engine_stopped = Signal(int, QProcess.ExitStatus)
    engine_error = Signal(str)
    best_move_updated = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.status = MagicMock()
        self.start = MagicMock()
        self.stop = MagicMock()
        self.send = MagicMock()
        self.update_settings = MagicMock()
        self.is_running = MagicMock()
        self.is_ready = MagicMock()
        self.set_position_startpos = MagicMock()
        self.set_position_fen = MagicMock()
        self.set_options = MagicMock()
        self.go = MagicMock()
        self.go_depth = MagicMock()
        self.go_infinite = MagicMock()
        self.go_time = MagicMock()
        self.go_nodes = MagicMock()
        self.stop_search = MagicMock()
        self.deleteLater = MagicMock()


class TestEngineManager:
    """Test suite for the EngineManager controller facade."""

    @pytest.fixture
    def mock_service_class(self):
        """Fixture to patch EngineService class inside the engine manager."""
        with patch("gui.app.engine.manager.engine_manager.EngineService") as mock_class:
            yield mock_class

    @pytest.fixture
    def engine_manager(self):
        """Fixture to provide a fresh, isolated EngineManager instance."""
        return EngineManager(parent=None)

    # --- Initialization & Bubbling Tests ---

    def test_initialization_and_added_removed_bubbling(self, engine_manager):
        """Verify that Engines model signal emissions bubble up through EngineManager."""
        added_emissions = []
        removed_emissions = []
        engine_manager.engine_added.connect(lambda name, status: added_emissions.append((name, status)))
        engine_manager.engine_removed.connect(removed_emissions.append)

        # Trigger Engines signals
        status = engine_manager.engines.add_engine("Stockfish")
        assert added_emissions == [("Stockfish", status)]

        engine_manager.engines.remove_engine("Stockfish")
        assert removed_emissions == ["Stockfish"]

    # --- Engine Registration & Multiplexing Tests ---

    def test_create_engine_success_and_signal_multiplexing(self, mock_service_class, engine_manager):
        """Verify create_engine wires all model signals and service signals to bubble up."""
        mock_service = MockEngineService()
        mock_service_class.return_value = mock_service

        # Track multiplexed manager signals
        info_emissions = []
        settings_emissions = []
        analysis_emissions = []
        ready_emissions = []
        stopped_emissions = []
        error_emissions = []
        best_move_emissions = []

        engine_manager.engine_info_updated.connect(lambda name, data: info_emissions.append((name, data)))
        engine_manager.engine_settings_updated.connect(lambda name, data: settings_emissions.append((name, data)))
        engine_manager.engine_analysis_updated.connect(lambda name, data: analysis_emissions.append((name, data)))
        engine_manager.engine_ready.connect(ready_emissions.append)
        engine_manager.engine_stopped.connect(lambda name, code, status: stopped_emissions.append((name, code, status)))
        engine_manager.engine_error.connect(lambda name, msg: error_emissions.append((name, msg)))
        engine_manager.best_move_updated.connect(lambda name, move: best_move_emissions.append((name, move)))

        assert engine_manager.create_engine("Stockfish") is True

        # Verify EngineService instantiation
        mock_service_class.assert_called_once()
        status_arg = mock_service_class.call_args[0][0]
        assert status_arg == engine_manager.engines.get_engine("Stockfish")

        # Test model signal bubbling
        status_arg.info.info_updated.emit()
        assert info_emissions == [("Stockfish", status_arg.info)]

        status_arg.settings.settings_updated.emit()
        assert settings_emissions == [("Stockfish", status_arg.settings)]

        status_arg.analysis.analysis_state_changed.emit()
        assert analysis_emissions == [("Stockfish", status_arg.analysis)]

        # Test service signal bubbling
        mock_service.engine_ready.emit()
        assert ready_emissions == ["Stockfish"]

        mock_service.engine_stopped.emit(0, QProcess.ExitStatus.NormalExit)
        assert stopped_emissions == [("Stockfish", 0, QProcess.ExitStatus.NormalExit)]

        mock_service.engine_error.emit("Failed")
        assert error_emissions == [("Stockfish", "Failed")]

        mock_service.best_move_updated.emit("e2e4")
        assert best_move_emissions == [("Stockfish", "e2e4")]

    def test_create_engine_already_exists(self, mock_service_class, engine_manager):
        """Verify create_engine returns True early and does not recreate if already registered."""
        mock_service = MockEngineService()
        mock_service_class.return_value = mock_service

        assert engine_manager.create_engine("Stockfish") is True
        assert engine_manager.create_engine("Stockfish") is True
        assert mock_service_class.call_count == 1

    def test_remove_engine(self, mock_service_class, engine_manager):
        """Verify remove_engine stops the service, deletes it, and removes it from model registry."""
        mock_service = MockEngineService()
        mock_service_class.return_value = mock_service

        engine_manager.create_engine("Stockfish")
        assert "Stockfish" in engine_manager._services

        engine_manager.remove_engine("Stockfish")

        mock_service.stop.assert_called_once()
        mock_service.deleteLater.assert_called_once()
        assert "Stockfish" not in engine_manager._services
        assert "Stockfish" not in engine_manager.engines.active_engines

    def test_remove_engine_missing(self, engine_manager):
        """Verify remove_engine logs warning and fails safely for unregistered keys."""
        engine_manager.remove_engine("NonExistent")

    def test_shutdown(self, mock_service_class, engine_manager):
        """Verify shutdown stops all services, clears registries, and cleans up resource handles."""
        mock_service1 = MockEngineService()
        mock_service2 = MockEngineService()
        mock_service_class.side_effect = [mock_service1, mock_service2]

        engine_manager.create_engine("Stockfish")
        engine_manager.create_engine("Leela")

        engine_manager.shutdown()

        mock_service1.stop.assert_called_once()
        mock_service2.stop.assert_called_once()
        assert engine_manager._services == {}
        assert engine_manager.engines.active_engines == []

    # --- Service Command Delegation Tests ---

    def test_setup_engine(self, mock_service_class, engine_manager):
        """Verify setup_engine creates and starts the engine process."""
        mock_service = MockEngineService()
        mock_service_class.return_value = mock_service
        mock_service.start.return_value = True

        engine_manager.setup_engine("Stockfish", "path/to/exe")

        mock_service.start.assert_called_once_with("path/to/exe")

    def test_delegation_commands(self, mock_service_class, engine_manager):
        """Verify that basic queries and commands delegate directly to the underlying service."""
        mock_service = MockEngineService()
        mock_service_class.return_value = mock_service

        engine_manager.create_engine("Stockfish")

        # start
        mock_service.start.return_value = True
        assert engine_manager.start("Stockfish", "fallback") is True
        mock_service.start.assert_called_once_with("fallback")

        # stop
        engine_manager.stop("Stockfish")
        mock_service.stop.assert_called_once()

        # send
        engine_manager.send("Stockfish", "uci_cmd")
        mock_service.send.assert_called_once_with("uci_cmd")

        # update_settings
        engine_manager.update_settings("Stockfish", threads=4)
        mock_service.update_settings.assert_called_once_with(threads=4)

        # is_running
        mock_service.is_running.return_value = True
        assert engine_manager.is_running("Stockfish") is True
        mock_service.is_running.assert_called_once()

        # is_ready
        engine_manager.is_ready("Stockfish")
        mock_service.is_ready.assert_called_once()

        # set_position_startpos
        engine_manager.set_position_startpos("Stockfish")
        mock_service.set_position_startpos.assert_called_once()

        # set_position_fen
        engine_manager.set_position_fen("Stockfish", "fen_string")
        mock_service.set_position_fen.assert_called_once_with("fen_string")

        # go
        engine_manager.go("Stockfish")
        mock_service.go.assert_called_once()

        # go_depth
        engine_manager.go_depth("Stockfish", 12)
        mock_service.go_depth.assert_called_once_with(12)

        # go_infinite
        engine_manager.go_infinite("Stockfish")
        mock_service.go_infinite.assert_called_once()

        # go_time
        engine_manager.go_time("Stockfish", 1000)
        mock_service.go_time.assert_called_once_with(1000)

        # go_nodes
        engine_manager.go_nodes("Stockfish", 5000)
        mock_service.go_nodes.assert_called_once_with(5000)

        # stop_search
        engine_manager.stop_search("Stockfish")
        mock_service.stop_search.assert_called_once()

    def test_set_options(self, mock_service_class, engine_manager):
        """Verify set_options updates settings for positive numbers and calls set_options on the service."""
        mock_service = MockEngineService()
        mock_service_class.return_value = mock_service

        engine_manager.create_engine("Stockfish")

        # Test both positive options
        engine_manager.set_options("Stockfish", hash=256, threads=4)
        mock_service.update_settings.assert_any_call(hash_size=256)
        mock_service.update_settings.assert_any_call(threads=4)
        mock_service.set_options.assert_called_once()

        # Test invalid values (should not update settings)
        mock_service.update_settings.reset_mock()
        mock_service.set_options.reset_mock()
        engine_manager.set_options("Stockfish", hash=-1, threads=-1)
        mock_service.update_settings.assert_not_called()
        mock_service.set_options.assert_called_once()


    # --- Export and Load Settings Tests ---

    def test_export_and_serialization(self, mock_service_class, engine_manager):
        """Verify serialization and profile exporting retrieve state details of active engines."""
        mock_service1 = MockEngineService()
        mock_service2 = MockEngineService()
        mock_service_class.side_effect = [mock_service1, mock_service2]

        engine_manager.create_engine("Stockfish")
        engine_manager.create_engine("Leela")

        mock_service1.status.asdict.return_value = {"threads": 4}
        mock_service2.status.asdict.return_value = {"threads": 2}

        # asdict
        assert engine_manager.asdict("Stockfish") == {"threads": 4}
        mock_service1.status.asdict.assert_called_once()

        # get_export_state
        expected_state = {
            "Stockfish": {"threads": 4},
            "Leela": {"threads": 2},
        }
        assert engine_manager.get_export_state() == expected_state

    def test_load_settings(self, mock_service_class, engine_manager):
        """Verify load_settings registers engines and dispatches setting updates."""
        mock_service = MockEngineService()
        mock_service_class.return_value = mock_service

        settings_dict = {
            "Stockfish": {"settings": {"threads": 4, "hash_size": 128}}
        }

        engine_manager.load_settings(settings_dict)

        assert "Stockfish" in engine_manager._services
        mock_service.update_settings.assert_called_once_with(threads=4, hash_size=128)

    def test_create_engine_failure(self, engine_manager):
        """Verify create_engine returns False if add_engine fails (returns None)."""
        # Arrange
        with patch.object(engine_manager.engines, "add_engine", return_value=None):
            # Act
            result = engine_manager.create_engine("Stockfish")

            # Assert
            assert result is False

    def test_missing_engine_operations(self, engine_manager):
        """Verify calling operations on a missing engine returns default values safely."""
        # Act & Assert
        assert engine_manager.start("NonExistentEngine") is False
        assert engine_manager.is_running("NonExistentEngine") is False
        assert engine_manager.asdict("NonExistentEngine") is None

    def test_setup_engine_failure_cases(self, engine_manager):
        """Verify setup_engine handles creation or start failure scenarios gracefully."""
        # Arrange
        with patch.object(engine_manager, "create_engine", return_value=False), \
             patch.object(engine_manager, "start", return_value=False):
            # Act / Assert (should complete without raising exception)
            engine_manager.setup_engine("Stockfish", "/invalid/path")

