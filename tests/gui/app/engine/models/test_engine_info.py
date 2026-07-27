import pytest
from gui.app.engine.models.engine_info import EngineInfo


class TestEngineInfo:
    """Test suite for the reactive EngineInfo model."""

    @pytest.fixture
    def engine_info(self):
        """Fixture to provide a fresh, default EngineInfo model."""
        return EngineInfo(parent=None)

    # --- Initialization Tests ---

    def test_default_initialization(self, engine_info):
        """Verify that the engine info model initializes with correct default values."""
        assert engine_info.name == ""
        assert engine_info.author == ""
        assert engine_info.connection_status == "NotRunning"
        assert engine_info.search_status == "Offline"

    def test_custom_initialization(self):
        """Verify that custom name and author parameters can be passed during initialization."""
        custom_info = EngineInfo(parent=None, name="Stockfish 16", author="The Stockfish Developers")
        assert custom_info.name == "Stockfish 16"
        assert custom_info.author == "The Stockfish Developers"
        assert custom_info.connection_status == "NotRunning"
        assert custom_info.search_status == "Offline"

    # --- Property Getters and Setters Tests ---

    def test_property_setters_and_getters(self, engine_info):
        """Verify that name, author, connection_status, and search_status properties can be updated correctly."""
        engine_info.name = "Leela Chess Zero"
        engine_info.author = "Lcz Developers"
        engine_info.connection_status = "SyncingSettings"
        engine_info.search_status = "Searching"

        assert engine_info.name == "Leela Chess Zero"
        assert engine_info.author == "Lcz Developers"
        assert engine_info.connection_status == "SyncingSettings"
        assert engine_info.search_status == "Searching"

    # --- Signal and Notification Tests ---

    def test_setters_do_not_emit_signals(self, engine_info, qtbot):
        """Verify that modifying individual properties does not trigger signals to prevent signal storms."""
        with qtbot.assertNotEmitted(engine_info.info_updated):
            engine_info.name = "Stockfish"
            engine_info.connection_status = "Starting"

    def test_notify_updated_emits_signal(self, engine_info, qtbot):
        """Verify that notify_updated explicitly emits info_updated signal."""
        with qtbot.waitSignal(engine_info.info_updated, timeout=1000):
            engine_info.notify_updated()

    # --- Serialization Tests ---

    def test_asdict_conversion(self, engine_info):
        """Verify that asdict dynamically serializes the current properties into a dictionary."""
        engine_info.name = "Stockfish 16"
        engine_info.author = "T. Romstad"
        engine_info.connection_status = "Running"
        engine_info.search_status = "Idle"

        expected_dict = {
            "name": "Stockfish 16",
            "author": "T. Romstad",
            "connection_status": "Running",
            "search_status": "Idle",
        }

        assert engine_info.asdict() == expected_dict
