"""Game session state model and enums.

This module provides the GameState class and corresponding GameMode and
MatchStatus enums representing the state of an active chess session.
"""

from PySide6.QtCore import QObject, Signal
from enum import Enum, auto
import chess
from gui.utils import get_logger

logger = get_logger(__name__)


class GameMode(Enum):
    """Represent the chess game mode (e.g. play white, analysis, etc.)."""

    PLAY_WHITE = auto()
    PLAY_BLACK = auto()
    ENGINE_VS_ENGINE = auto()
    ANALYSIS = auto()


class MatchStatus(Enum):
    """Represent the status of the chess match (e.g. checkmate, active, draw)."""

    ACTIVE = auto()
    DRAW = auto()
    CHECKMATE = auto()
    STALEMATE = auto()
    RESIGNED = auto()
    ABORTED = auto()


class GameState(QObject):
    """Store the configurations, clocks, turn, and status of an active game session.

    This model serves as a reactive state container, emitting Qt signals when the
    turn, clocks, game mode, or match status are changed.

    Signals:
        game_mode_changed: Emitted when the GameMode is updated.
        match_status_changed: Emitted when the MatchStatus is updated.
        turn_changed: Emitted when the active turn switches (True for White, False for Black).
        clocks_updated: Emitted when the player clock times are updated (white_time, black_time).
    """

    # Signals for UI/ViewModel reactivity
    game_mode_changed = Signal(GameMode)
    match_status_changed = Signal(MatchStatus)
    turn_changed = Signal(bool)             # chess.WHITE (True) or chess.BLACK (False)
    clocks_updated = Signal(float, float)   # white_time, black_time

    def __init__(self, parent):
        """Initialize the game state model.

        Args:
            parent: Qt parent object for memory management.
        """
        super().__init__(parent)
        self._game_mode = GameMode.ANALYSIS
        self._match_status = MatchStatus.ACTIVE
        self._current_turn = chess.WHITE
        self._white_time = 0.0
        self._black_time = 0.0

        self.game_mode_changed.emit(self._game_mode)

    @property
    def mode(self) -> GameMode:
        """Return the current game mode."""
        return self._game_mode

    @mode.setter
    def mode(self, val: GameMode):
        """Set the current game mode.

        Args:
            val: The new GameMode value.
        """
        if self._game_mode != val:
            logger.info("Game mode changed: %s -> %s", self._game_mode.name, val.name)
            self._game_mode = val
            self.game_mode_changed.emit(val)

    @property
    def match_status(self) -> MatchStatus:
        """Return the current match status."""
        return self._match_status

    @match_status.setter
    def match_status(self, val: MatchStatus):
        """Set the current match status.

        Args:
            val: The new MatchStatus value.
        """
        if self._match_status != val:
            logger.info("Match status changed: %s -> %s", self._match_status.name, val.name)
            self._match_status = val
            self.match_status_changed.emit(val)

    @property
    def current_turn(self) -> chess.Color:
        """Return the current turn side (True for White, False for Black)."""
        return self._current_turn

    @current_turn.setter
    def current_turn(self, val: chess.Color):
        """Set the current turn side.

        Args:
            val: The new chess.Color turn side.
        """
        if self._current_turn != val:
            self._current_turn = val
            self.turn_changed.emit(val)

    def update_clocks(self, white_time: float, black_time: float):
        """Update clocks for both players and emit a clocks_updated signal.

        Args:
            white_time: Remaining time for white in seconds.
            black_time: Remaining time for black in seconds.
        """
        self._white_time = white_time
        self._black_time = black_time
        self.clocks_updated.emit(white_time, black_time)

    def reset(self):
        """Reset the match status, turn side, and clocks for a new game."""
        self._match_status = MatchStatus.ACTIVE
        self._current_turn = chess.WHITE
        self.update_clocks(0.0, 0.0)

        # Emit signals to notify any observers of the reset state
        self.match_status_changed.emit(self._match_status)
        self.turn_changed.emit(self._current_turn)
        self.clocks_updated.emit(self._white_time, self._black_time)
