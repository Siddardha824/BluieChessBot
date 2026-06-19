import io
import chess.pgn
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QInputDialog, QFrame
)
from gui.app.ui.templates import StyledWidget
from gui.utils import get_logger
from .move_list_widget import MoveListWidget

logger = get_logger(__name__)

class MoveHistoryPanel(StyledWidget):
    """
    Panel that shows the SAN move history table, undo/redo navigation, and save/load options.
    """
    def __init__(self, app_manager, parent=None):
        super().__init__("moveHistoryPanel", parent)
        self._manager = app_manager
        self._board_state = self._manager.board.getSession

        self.setup_ui()
        self._connect_signals()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 8, 6, 8)
        main_layout.setSpacing(6)

        # 1. Header Title
        self.lbl_title = QLabel("MOVE HISTORY", self)
        self.lbl_title.setObjectName("panelTitle")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.lbl_title.font()
        font.setBold(True)
        font.setPointSize(12)
        self.lbl_title.setFont(font)
        main_layout.addWidget(self.lbl_title)

        # 2. Move List Table
        self.move_list = MoveListWidget(self._manager, self)
        main_layout.addWidget(self.move_list, 1)

        # Divider
        divider1 = QFrame(self)
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(divider1)

        # 3. Navigation Controls
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(6)

        self.btn_first = QPushButton("<<", self)
        self.btn_first.setObjectName("navButton")
        self.btn_first.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_first.setMinimumWidth(30)
        self.btn_first.setMaximumWidth(50)

        self.btn_prev = QPushButton("<", self)
        self.btn_prev.setObjectName("navButton")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setMinimumWidth(30)
        self.btn_prev.setMaximumWidth(50)

        self.btn_next = QPushButton(">", self)
        self.btn_next.setObjectName("navButton")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setMinimumWidth(30)
        self.btn_next.setMaximumWidth(50)

        self.btn_last = QPushButton(">>", self)
        self.btn_last.setObjectName("navButton")
        self.btn_last.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_last.setMinimumWidth(30)
        self.btn_last.setMaximumWidth(50)

        nav_layout.addWidget(self.btn_first)
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        nav_layout.addWidget(self.btn_last)
        main_layout.addLayout(nav_layout)

        # Divider
        divider2 = QFrame(self)
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(divider2)

        # 4. Save/Load Action Controls
        action_layout = QVBoxLayout()
        action_layout.setSpacing(6)

        self.btn_load = QPushButton("Load Game", self)
        self.btn_load.setObjectName("actionButton")
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_save = QPushButton("Save Game", self)
        self.btn_save.setObjectName("actionButton")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)

        action_layout.addWidget(self.btn_load)
        action_layout.addWidget(self.btn_save)
        main_layout.addLayout(action_layout)

    def _connect_signals(self):
        # Table Selection
        self.move_list.move_selected.connect(self._on_move_selected)

        # Navigation Buttons
        self.btn_first.clicked.connect(self._on_nav_first)
        self.btn_prev.clicked.connect(self._on_nav_prev)
        self.btn_next.clicked.connect(self._on_nav_next)
        self.btn_last.clicked.connect(self._on_nav_last)

        # Save/Load Buttons
        self.btn_save.clicked.connect(self._on_save_game)
        self.btn_load.clicked.connect(self._on_load_game)

    def _on_move_selected(self, index: int):
        self._board_state.view_index = index

    def _on_nav_first(self):
        logger.info("Navigation: Jump to start.")
        self._board_state.view_index = 0

    def _on_nav_prev(self):
        logger.info("Navigation: Step back.")
        self._board_state.view_index -= 1

    def _on_nav_next(self):
        logger.info("Navigation: Step forward.")
        self._board_state.view_index += 1

    def _on_nav_last(self):
        logger.info("Navigation: Jump to end.")
        self._board_state.view_index = len(self._board_state.move_stack)

    def _on_save_game(self):
        logger.info("Save game clicked.")
        # Halt engine first
        self._manager.game.stop_game()

        # Build chess.pgn.Game object
        moves = self._board_state.move_stack
        game = chess.pgn.Game()
        
        # Load FEN starting position if not default
        starting_fen = self._board_state.starting_fen
        if starting_fen != chess.STARTING_FEN:
            game.setup(starting_fen)

        # Append all moves in the stack to the game node
        node = game
        for m in moves:
            node = node.add_main_variation(m)

        # Exporter PGN formatting
        pgn_data = str(game)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Chess Game (PGN)",
            "",
            "PGN Files (*.pgn);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(pgn_data)
                logger.info("Game saved to %s", file_path)
            except Exception as e:
                logger.error("Failed to save game to file: %s", e)

    def _on_load_game(self):
        logger.info("Load game clicked.")
        self._manager.game.stop_game()

        # Let user choose between Load FEN or Load PGN file
        options = ["Load FEN String", "Load PGN File"]
        choice, ok = QInputDialog.getItem(
            self,
            "Load Chess Game/Position",
            "Choose source type:",
            options,
            0,
            False
        )
        
        if not ok or not choice:
            return

        if choice == "Load FEN String":
            fen_str, ok = QInputDialog.getText(
                self,
                "Load FEN String",
                "Paste FEN string here:"
            )
            if ok and fen_str.strip():
                try:
                    self._manager.board.load_fen(fen_str.strip())
                    logger.info("FEN loaded successfully")
                except Exception as e:
                    logger.error("Invalid FEN: %s", e)
                    
        elif choice == "Load PGN File":
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Chess Game (PGN)",
                "",
                "PGN Files (*.pgn);;All Files (*)"
            )
            if file_path:
                try:
                    with open(file_path, "r") as f:
                        game = chess.pgn.read_game(f)
                    
                    if game:
                        moves = list(game.mainline_moves())
                        starting_fen = game.headers.get("FEN", chess.STARTING_FEN)
                        
                        # Reset board to game's start position, then play moves sequentially
                        self._manager.board.load_fen(starting_fen)
                        for m in moves:
                            self._manager.board.make_move(m.uci())
                        logger.info("PGN file loaded successfully with %s moves", len(moves))
                except Exception as e:
                    logger.error("Failed to load PGN file: %s", e)
