"""Engine settings model for chess engine configuration and search constraints.

This module provides the EngineSettings data model for storing settings as
specified by the UI. All settings are validated on assignment to ensure only
valid configurations are stored and passed to the engine service.

Validation occurs at property setter level to catch configuration errors early.
"""

from PySide6.QtCore import QObject, Signal
import inspect


class EngineSettings(QObject):
    """Manage UCI chess engine search constraints and configuration.

    This model stores user-configurable engine settings and search parameters.
    All properties use setters with validation to ensure:
    - Only valid constraint modes are accepted (depth, time, nodes, infinite).
    - All numeric values are positive integers.
    - Engine path is properly formatted.

    Settings are applied to the engine via the EngineService when changed.

    Signals:
        settings_updated: Emitted when engine configuration settings are updated.

    Attributes:
        constraint_mode: Search constraint type (depth, time, nodes, or infinite).
        max_depth: Maximum search depth in plies (1+).
        max_time_ms: Maximum search time in milliseconds (1+).
        max_nodes: Maximum nodes to evaluate (1+).
        hash_size: Transposition table size in MB (1+).
        threads: Number of worker threads (1+).
        engine_path: File system path to the chess engine executable.
    """


    settings_updated = Signal()

    def __init__(self, parent):
        """Initialize engine settings with default values.

        Default configuration:
        - Depth-limited search at 3 plies.
        - 64 MB transposition table.
        - 1 worker thread.
        - No engine path specified.

        Args:
            parent: Qt parent object for memory management.
        """
        super().__init__(parent)
        self._constraint_mode: str = "depth"
        self._max_depth: int = 3
        self._max_time_ms: int = 1000
        self._max_nodes: int = 10000
        self._hash_size: int = 64
        self._threads: int = 1
        self._engine_path: str = ""

    @property
    def constraint_mode(self) -> str:
        """Return the current search constraint mode (lowercase)."""
        return self._constraint_mode

    @constraint_mode.setter
    def constraint_mode(self, val: str):
        """Set the search constraint mode with validation.

        Args:
            val: One of "depth", "time", "nodes", "infinite" (case-insensitive).

        Raises:
            ValueError: If val is not one of the valid constraint modes.
        """
        # Validate against allowed constraint modes
        if val.lower() in ["depth", "time", "nodes", "infinite"]:
            self._constraint_mode = val.lower()
        else:
            raise ValueError(f"Invalid constraint mode: {val}. Must be one of: depth, time, nodes, infinite.")

    @property
    def max_depth(self) -> int:
        """Return the maximum search depth in plies (1+)."""
        return self._max_depth

    @max_depth.setter
    def max_depth(self, val: int):
        """Set the maximum search depth with validation.

        Args:
            val: Positive integer depth in plies.

        Raises:
            ValueError: If val is less than 1.
        """
        # Enforce positive depth
        if val < 1:
            raise ValueError("Max depth must be a positive integer.")
        self._max_depth = val

    @property
    def max_time_ms(self) -> int:
        """Return the maximum search time in milliseconds (1+)."""
        return self._max_time_ms

    @max_time_ms.setter
    def max_time_ms(self, val: int):
        """Set the maximum search time with validation.

        Args:
            val: Positive integer time in milliseconds.

        Raises:
            ValueError: If val is less than 1.
        """
        # Enforce positive time
        if val < 1:
            raise ValueError("Max time (ms) must be a positive integer.")
        self._max_time_ms = val

    @property
    def max_nodes(self) -> int:
        """Return the maximum nodes to evaluate during search (1+)."""
        return self._max_nodes

    @max_nodes.setter
    def max_nodes(self, val: int):
        """Set the maximum nodes to evaluate with validation.

        Args:
            val: Positive integer node count.

        Raises:
            ValueError: If val is less than 1.
        """
        # Enforce positive node count
        if val < 1:
            raise ValueError("Max nodes must be a positive integer.")
        self._max_nodes = val

    @property
    def hash_size(self) -> int:
        """Return the transposition table size in megabytes (1+)."""
        return self._hash_size

    @hash_size.setter
    def hash_size(self, val: int):
        """Set the transposition table size with validation.

        Args:
            val: Positive integer hash size in MB.

        Raises:
            ValueError: If val is less than 1.
        """
        # Enforce positive hash size
        if val < 1:
            raise ValueError("Hash size should be positive integer.")
        self._hash_size = val

    @property
    def threads(self) -> int:
        """Return the number of worker threads for parallel search (1+)."""
        return self._threads

    @threads.setter
    def threads(self, val: int):
        """Set the number of worker threads with validation.

        Args:
            val: Positive integer thread count.

        Raises:
            ValueError: If val is less than 1.
        """
        # Enforce positive thread count
        if val < 1:
            raise ValueError("No of Threads should be a positive integer.")
        self._threads = val

    @property
    def engine_path(self) -> str:
        """Return the file system path to the chess engine executable."""
        return self._engine_path

    @engine_path.setter
    def engine_path(self, val: str):
        """Set the engine executable path with validation.

        Args:
            val: String path to the engine executable.

        Raises:
            ValueError: If val is not a string.
        """
        # Validate path is a string
        if not isinstance(val, str):
            raise ValueError("Engine path must be a string.")
        self._engine_path = val

    def notify_updated(self) -> None:
        """Emit the settings_updated signal to notify listeners that configuration changed."""
        self.settings_updated.emit()


    def asdict(self) -> dict:
        """Convert all settings to a dictionary.

        Use introspection to dynamically discover all @property members and
        return their current values as a dictionary.

        Returns:
            A dictionary with property names as keys and current values.

        Example:
            >>> settings.asdict()
            {'constraint_mode': 'depth', 'max_depth': 3, 'max_time_ms': 1000,
             'max_nodes': 10000, 'hash_size': 64, 'threads': 1, 'engine_path': ''}
        """
        # Use introspection to find all property members on the class
        properties = [
            name for name, val in inspect.getmembers(type(self), lambda v: isinstance(v, property))
        ]

        # Build dictionary by getting current value of each property
        return {
            key: getattr(self, key) for key in properties
        }