import pytest
from gui.app.engine.models.engine_settings import EngineSettings


class TestEngineSettings:
    """Test suite for the reactive EngineSettings model."""

    @pytest.fixture
    def settings(self):
        """Fixture to provide a fresh, default EngineSettings model."""
        return EngineSettings(parent=None)

    # --- Initialization Tests ---

    def test_initialization(self, settings):
        """Verify that the engine settings model initializes with correct default values."""
        assert settings.constraint_mode == "depth"
        assert settings.max_depth == 3
        assert settings.max_time_ms == 1000
        assert settings.max_nodes == 10000
        assert settings.hash_size == 64
        assert settings.threads == 1
        assert settings.engine_path == ""

    # --- Constraint Mode Tests ---

    @pytest.mark.parametrize(
        "input_val, expected_stored",
        [
            ("depth", "depth"),
            ("time", "time"),
            ("nodes", "nodes"),
            ("infinite", "infinite"),
            ("DEPTH", "depth"),  # Case insensitivity check
            ("TiMe", "time"),
        ]
    )
    def test_constraint_mode_valid(self, input_val, expected_stored, settings):
        """Verify that valid search constraint modes are normalized and accepted."""
        settings.constraint_mode = input_val
        assert settings.constraint_mode == expected_stored

    @pytest.mark.parametrize(
        "invalid_val",
        [
            "invalid_mode",
            "",
            "depth_limit",
        ]
    )
    def test_constraint_mode_invalid(self, invalid_val, settings):
        """Verify that invalid search constraint modes raise ValueError."""
        with pytest.raises(ValueError, match="Invalid constraint mode"):
            settings.constraint_mode = invalid_val

    # --- Numeric Settings Validation Tests ---

    @pytest.mark.parametrize(
        "property_name, valid_val",
        [
            ("max_depth", 1),
            ("max_depth", 100),
            ("max_time_ms", 1),
            ("max_time_ms", 5000),
            ("max_nodes", 1),
            ("max_nodes", 1000000),
            ("hash_size", 1),
            ("hash_size", 1024),
            ("threads", 1),
            ("threads", 64),
        ]
    )
    def test_numeric_properties_valid(self, property_name, valid_val, settings):
        """Verify that positive integers are accepted for all numeric properties."""
        setattr(settings, property_name, valid_val)
        assert getattr(settings, property_name) == valid_val

    @pytest.mark.parametrize(
        "property_name, invalid_val, expected_error_msg",
        [
            ("max_depth", 0, "Max depth must be a positive integer"),
            ("max_depth", -5, "Max depth must be a positive integer"),
            ("max_time_ms", 0, r"Max time \(ms\) must be a positive integer"),
            ("max_time_ms", -10, r"Max time \(ms\) must be a positive integer"),
            ("max_nodes", 0, "Max nodes must be a positive integer"),
            ("max_nodes", -100, "Max nodes must be a positive integer"),
            ("hash_size", 0, "Hash size should be positive integer"),
            ("hash_size", -2, "Hash size should be positive integer"),
            ("threads", 0, "No of Threads should be a positive integer"),
            ("threads", -1, "No of Threads should be a positive integer"),
        ]
    )

    def test_numeric_properties_invalid(self, property_name, invalid_val, expected_error_msg, settings):
        """Verify that numeric values less than 1 raise a ValueError with specific messages."""
        with pytest.raises(ValueError, match=expected_error_msg):
            setattr(settings, property_name, invalid_val)

    # --- Engine Path Validation Tests ---

    def test_engine_path_valid(self, settings):
        """Verify that a string value is accepted as the engine path."""
        settings.engine_path = "path/to/stockfish"
        assert settings.engine_path == "path/to/stockfish"

    @pytest.mark.parametrize(
        "invalid_path",
        [
            None,
            123,
            ["path"],
            {"path": "val"},
        ]
    )
    def test_engine_path_invalid(self, invalid_path, settings):
        """Verify that passing non-string values as engine path raises a ValueError."""
        with pytest.raises(ValueError, match="Engine path must be a string"):
            settings.engine_path = invalid_path

    # --- Signal and Notification Tests ---

    def test_setters_do_not_emit_signals(self, settings, qtbot):
        """Verify that modifying individual properties does not trigger signals to prevent signal storms."""
        with qtbot.assertNotEmitted(settings.settings_updated):
            settings.max_depth = 5
            settings.threads = 4
            settings.engine_path = "stockfish"

    def test_notify_updated_emits_signal(self, settings, qtbot):
        """Verify that notify_updated explicitly emits settings_updated signal."""
        with qtbot.waitSignal(settings.settings_updated, timeout=1000):
            settings.notify_updated()

    # --- Serialization Tests ---

    def test_asdict_conversion(self, settings):
        """Verify that asdict dynamically serializes settings into a dictionary."""
        settings.constraint_mode = "time"
        settings.max_time_ms = 2000
        settings.threads = 4
        settings.engine_path = "path/to/lc0"

        expected_dict = {
            "constraint_mode": "time",
            "max_depth": 3,
            "max_time_ms": 2000,
            "max_nodes": 10000,
            "hash_size": 64,
            "threads": 4,
            "engine_path": "path/to/lc0",
        }

        assert settings.asdict() == expected_dict
