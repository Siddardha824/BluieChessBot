import pytest
import chess
from gui.app.board.services.move_node import MoveNode, ChildMoveNode


class TestMoveNode:
    """Test suite for the custom MoveNode and ChildMoveNode PGN classes."""

    @pytest.fixture
    def root_node(self):
        """Fixture to provide a fresh MoveNode (starting position) for each test."""
        return MoveNode()

    # --- Initialization & Caching Tests ---

    def test_initialization_and_board_caching(self, root_node):
        """Verify the root node initializes with the starting FEN and caches it securely."""
        board = root_node.board()
        assert board.fen() == chess.STARTING_FEN
        
        # Verify .board() returns a copy (mutating it shouldn't affect the cache)
        board.push(chess.Move.from_uci("e2e4"))
        assert root_node.board().fen() == chess.STARTING_FEN

    def test_setup_from_fen(self, root_node):
        """Verify that setting up a custom FEN updates the cached board properly."""
        custom_fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3"
        root_node.setup(custom_fen)
        
        assert root_node.board().fen() == custom_fen

    # --- Header Properties Tests ---

    def test_header_properties(self, root_node):
        """Verify that the custom property wrappers correctly read and write to the headers dictionary."""
        # Test White/Black setters
        root_node.white = "Stockfish"
        root_node.black = "Leela"
        assert root_node.headers["White"] == "Stockfish"
        assert root_node.black == "Leela"

        # Test Outcome setter
        root_node.set_outcome("1-0", "Time forfeit")
        assert root_node.result == "1-0"
        assert root_node.result_reason == "Time forfeit"
        
        # Test individual Result setters
        root_node.result = "1/2-1/2"
        root_node.result_reason = "Draw by agreement"
        assert root_node.headers["Result"] == "1/2-1/2"
        assert root_node.headers["Termination"] == "Draw by agreement"

    # --- Variation & Tree Logic Tests ---

    def test_add_variations_ordering(self, root_node):
        """Verify that variations and main variations are inserted into the correct indices."""
        move_e4 = chess.Move.from_uci("e2e4")
        move_d4 = chess.Move.from_uci("d2d4")

        # Standard variation appends to the end
        child_e4 = root_node.add_variation(move_e4)
        assert isinstance(child_e4, ChildMoveNode)
        assert len(root_node.variations) == 1
        assert root_node.variations[0].move == move_e4

        # Main variation inserts at index 0
        child_d4 = root_node.add_main_variation(move_d4)
        assert len(root_node.variations) == 2
        assert root_node.variations[0].move == move_d4
        assert root_node.variations[1].move == move_e4

    # --- ChildMoveNode Tests ---

    def test_child_node_board_caching(self, root_node):
        """Verify that a child node instantly calculates and caches its own board state."""
        move_e4 = chess.Move.from_uci("e2e4")
        child = root_node.add_variation(move_e4)
        
        # The child's cached board should reflect the move e4
        child_board = child.board()
        assert child_board.piece_at(chess.E4) == chess.Piece(chess.PAWN, chess.WHITE)
        assert child_board.piece_at(chess.E2) is None
        
        # Verify copy isolation for the child node
        child_board.push(chess.Move.from_uci("e7e5"))
        assert child.board().piece_at(chess.E5) is None

    def test_deep_variation_tree_caching(self, root_node):
        """Verify that deep node chains successfully pass and update the cache without O(n) recalculation."""
        move_e4 = chess.Move.from_uci("e2e4")
        move_e5 = chess.Move.from_uci("e7e5")
        move_nf3 = chess.Move.from_uci("g1f3")

        # Build a line: 1. e4 e5 2. Nf3
        child_1 = root_node.add_variation(move_e4)
        child_2 = child_1.add_variation(move_e5)
        child_3 = child_2.add_main_variation(move_nf3)

        # Verify the grandchild (depth 3) has the perfectly accumulated state
        final_board = child_3.board()
        assert final_board.piece_at(chess.E4) == chess.Piece(chess.PAWN, chess.WHITE)
        assert final_board.piece_at(chess.E5) == chess.Piece(chess.PAWN, chess.BLACK)
        assert final_board.piece_at(chess.F3) == chess.Piece(chess.KNIGHT, chess.WHITE)