import pytest
from unittest.mock import patch
from gui.app.engine.models.engines import Engines
from gui.app.engine.models.engine_status import EngineStatus


class TestEngines:
    """Test suite for the reactive Engines model registry."""

    @pytest.fixture
    def engines(self):
        """Fixture to provide a fresh, isolated Engines registry."""
        return Engines(parent=None)

    # --- Initialization Tests ---

    def test_initialization(self, engines):
        """Verify that the registry starts with an empty list of active engines."""
        assert engines.active_engines == []

    # --- Add Engine Tests ---

    def test_add_engine_success(self, engines, qtbot):
        """Verify that adding a new engine creates a status model, registers it, and emits a signal."""
        with qtbot.waitSignal(engines.engine_added, timeout=1000) as blocker:
            status = engines.add_engine("Stockfish")

        assert isinstance(status, EngineStatus)
        assert engines.active_engines == ["Stockfish"]
        assert engines.get_engine("Stockfish") == status

        assert blocker.args[0] == "Stockfish"
        assert blocker.args[1] == status

    def test_add_engine_empty_name(self, engines, qtbot):
        """Verify that adding an engine with an empty name fails safely and does not emit signals."""
        with qtbot.assertNotEmitted(engines.engine_added):
            status = engines.add_engine("")

        assert status is None
        assert engines.active_engines == []

    def test_add_engine_duplicate(self, engines, qtbot):
        """Verify that adding a duplicate engine returns the existing instance and does not emit duplicate signals."""
        status1 = engines.add_engine("Stockfish")
        assert engines.active_engines == ["Stockfish"]

        with qtbot.assertNotEmitted(engines.engine_added):
            status2 = engines.add_engine("Stockfish")

        assert status1 == status2
        assert engines.active_engines == ["Stockfish"]

    # --- Get Engine Tests ---

    def test_get_engine_missing(self, engines):
        """Verify that get_engine returns None if the engine is not registered."""
        assert engines.get_engine("NonExistent") is None

    # --- Remove Engine Tests ---

    def test_remove_engine_success(self, engines, qtbot):
        """Verify that removing an engine deletes it from registry and emits the removed signal."""
        status = engines.add_engine("Stockfish")
        assert engines.active_engines == ["Stockfish"]

        with patch.object(status, "deleteLater") as mock_delete_later:
            with qtbot.waitSignal(engines.engine_removed, timeout=1000) as blocker:
                engines.remove_engine("Stockfish")

            mock_delete_later.assert_called_once()
            assert blocker.args[0] == "Stockfish"

        assert engines.active_engines == []
        assert engines.get_engine("Stockfish") is None

    def test_remove_engine_missing(self, engines, qtbot):
        """Verify that removing a non-existent engine fails safely and does not emit signals."""
        with qtbot.assertNotEmitted(engines.engine_removed):
            engines.remove_engine("NonExistent")

    # --- Clear Tests ---

    def test_clear_all_engines(self, engines, qtbot):
        """Verify that clear removes all registered engines one by one, cleaning up resources."""
        status1 = engines.add_engine("Stockfish")
        status2 = engines.add_engine("Leela")
        assert len(engines.active_engines) == 2

        removed_list = []
        engines.engine_removed.connect(removed_list.append)

        with patch.object(status1, "deleteLater") as mock_del1, \
             patch.object(status2, "deleteLater") as mock_del2:

            engines.clear()

            mock_del1.assert_called_once()
            mock_del2.assert_called_once()

        assert engines.active_engines == []
        assert "Stockfish" in removed_list
        assert "Leela" in removed_list
        assert len(removed_list) == 2
