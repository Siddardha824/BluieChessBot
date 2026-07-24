import pytest
import chess
from gui.app.board.models.board_state import BoardState
from gui.app.board.services.move_node import MoveNode, ChildMoveNode


class TestBoardState:
    """Test suite for the reactive BoardState model."""

    @pytest.fixture
    def board_state(self, qtbot):
        """Fixture to provide a fresh BoardState instance.
        We pass None as the parent since QObject hierarchies aren't needed for isolated testing.
        """
        state = BoardState(parent=None)
        return state

    # --- Initialization & Properties Tests ---

    def test_initialization(self, board_state):
        """Verify the board initializes with the standard starting position and empty history."""
        assert board_state.is_start_pos is True
        assert board_state.fen == chess.STARTING_FEN
        assert board_state.turn == chess.WHITE
        assert board_state.fullmove_number == 1
        assert board_state.halfmove_clock == 0
        assert len(board_state.move_stack) == 0
        assert isinstance(board_state.game_tree, MoveNode)

    def test_board_properties_and_delegation(self, board_state):
        """Verify that convenience properties properly delegate to the underlying python-chess Board."""
        move = chess.Move.from_uci("e2e4")
        
        # Test legal moves and SAN formatting
        assert board_state.is_legal(move) is True
        assert board_state.san(move) == "e4"
        assert move in list(board_state.legal_moves)
        
        # Test isolation via .copy()
        board_copy = board_state.copy()
        assert isinstance(board_copy, chess.Board)
        
        # Modifying the copy should NOT affect the actual BoardState
        board_copy.push(move)
        assert board_state.is_start_pos is True 

    # --- FEN Management Tests ---

    def test_set_fen_emits_signal(self, board_state, qtbot):
        """Verify that setting a custom FEN updates the state and emits view_changed."""
        # Standard FEN after 1. e4 e5 2. Nf3 Nc6
        custom_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
        
        # Wait for the signal to be emitted during the set_fen call
        with qtbot.waitSignal(board_state.view_changed, timeout=1000) as blocker:
            board_state.set_fen(custom_fen)
            
        assert board_state.fen == custom_fen
        assert board_state.is_start_pos is True # It is the "start pos" of this new tree
        
        # Verify the emitted signal payload was the newly created root node
        emitted_node = blocker.args[0]
        assert isinstance(emitted_node, MoveNode)

    def test_is_valid_fen(self, board_state):
        """Verify FEN validation catches both structural and contextual errors."""
        assert board_state.is_valid_fen(chess.STARTING_FEN) is True
        
        # Invalid structural FEN
        assert board_state.is_valid_fen("invalid_garbage_string") is False
        
        # Invalid contextual FEN (e.g. Kings are missing)
        assert board_state.is_valid_fen("8/8/8/8/8/8/8/8 w - - 0 1") is False

    # --- Game Loop (Move, Undo, Reset) Tests ---

    def test_move_emits_signal(self, board_state, qtbot):
        """Verify that pushing a move appends a ChildMoveNode and emits view_changed."""
        move = chess.Move.from_uci("e2e4")
        
        with qtbot.waitSignal(board_state.view_changed, timeout=1000) as blocker:
            board_state.move(move)
            
        assert board_state.is_start_pos is False
        assert board_state.move_stack[-1] == move
        assert board_state.can_undo() is True
        
        # Verify the emitted payload was the new child node
        emitted_node = blocker.args[0]
        assert isinstance(emitted_node, ChildMoveNode)
        assert emitted_node.move == move

    def test_undo_move_emits_signal(self, board_state, qtbot):
        """Verify that undoing a move shifts the view backward and emits view_changed."""
        move = chess.Move.from_uci("e2e4")
        board_state.move(move)
        
        assert board_state.can_undo() is True

        with qtbot.waitSignal(board_state.view_changed, timeout=1000) as blocker:
            undone_move = board_state.undo()
            
        assert undone_move == move
        assert board_state.is_start_pos is True
        assert board_state.can_undo() is False
        
        # Verify the emitted payload is back to the root node
        emitted_node = blocker.args[0]
        assert isinstance(emitted_node, MoveNode)

    def test_undo_empty_raises_error(self, board_state):
        """Verify that trying to undo from the starting position raises an IndexError."""
        assert board_state.can_undo() is False
        
        with pytest.raises(IndexError, match="No moves to undo"):
            board_state.undo()

    def test_reset_emits_signal(self, board_state, qtbot):
        """Verify that resetting clears the tree, restores the starting FEN, and emits view_changed."""
        board_state.move(chess.Move.from_uci("e2e4"))
        assert board_state.is_start_pos is False
        
        with qtbot.waitSignal(board_state.view_changed, timeout=1000):
            board_state.reset()
            
        assert board_state.is_start_pos is True
        assert board_state.fen == chess.STARTING_FEN
        assert len(board_state.move_stack) == 0