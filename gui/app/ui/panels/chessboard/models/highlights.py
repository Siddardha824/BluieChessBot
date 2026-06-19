from typing import List, Optional

class HighlightManager:
    def __init__(self):
        """
        Initializes the HighlightManager.
        Stores all coordinate-highlight state, isolated from active drawing logic.
        """
        self.selected_square: Optional[int] = None
        self.legal_moves: List[int] = []
        
        self.last_move_from: Optional[int] = None
        self.last_move_to: Optional[int] = None
        
        self.check_square: Optional[int] = None
        
        self.game_over_result: Optional[str] = None
        self.game_over_reason: Optional[str] = None
        
        self.debug_overlay_squares: List[int] = []
        self.debug_overlay_mode: str = "NONE"

    def select_square(self, square_idx: Optional[int], legal_destinations: List[int] | None = None) -> None:
        """
        Selects a square and caches its legal move destinations.
        """
        self.selected_square = square_idx
        self.legal_moves = legal_destinations if legal_destinations is not None else []

    def set_last_move(self, from_idx: Optional[int], to_idx: Optional[int]) -> None:
        """
        Records the last played move's source and destination indices.
        """
        self.last_move_from = from_idx
        self.last_move_to = to_idx

    def set_check_square(self, king_idx: Optional[int]) -> None:
        """
        Records the square index of a king currently in check.
        """
        self.check_square = king_idx

    def clear_selection(self) -> None:
        """
        Clears the selection and legal moves highlights.
        """
        self.selected_square = None
        self.legal_moves = []

    def reset(self) -> None:
        """
        Full reset of all highlight states.
        """
        self.clear_selection()
        self.last_move_from = None
        self.last_move_to = None
        self.check_square = None
        self.game_over_result = None
        self.game_over_reason = None
        self.debug_overlay_squares = []
        self.debug_overlay_mode = "NONE"
