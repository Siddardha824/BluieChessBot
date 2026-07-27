import pytest
from gui.app.engine.models.engine_status import EngineStatus
from gui.app.engine.models.engine_info import EngineInfo
from gui.app.engine.models.engine_settings import EngineSettings
from gui.app.engine.models.analysis_state import AnalysisState


class TestEngineStatus:
    """Test suite for the structural EngineStatus model."""

    @pytest.fixture
    def status(self):
        """Fixture to provide a fresh, isolated EngineStatus model."""
        return EngineStatus(parent=None)

    # --- Initialization Tests ---

    def test_initialization(self, status):
        """Verify that EngineStatus constructs and aggregates all child models correctly."""
        assert isinstance(status.info, EngineInfo)
        assert isinstance(status.settings, EngineSettings)
        assert isinstance(status.analysis, AnalysisState)

        # Verify QObject parenting (child models are parented to the status model)
        assert status.info.parent() == status
        assert status.settings.parent() == status
        assert status.analysis.parent() == status

    # --- Serialization Tests ---

    def test_asdict_conversion(self, status):
        """Verify that asdict aggregates serialized dicts of info and settings sub-models."""
        # Setup settings and info with custom values
        status.info.name = "Stockfish"
        status.info.connection_status = "Running"
        status.settings.threads = 4
        status.settings.engine_path = "/path/to/stockfish"

        expected_dict = {
            "info": status.info.asdict(),
            "settings": status.settings.asdict(),
        }

        assert status.asdict() == expected_dict
