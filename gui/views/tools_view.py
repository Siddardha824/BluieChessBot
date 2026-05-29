# gui/views/tools_view.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QLineEdit, QGridLayout, QApplication)
from PySide6.QtCore import Qt, QRectF, QSize, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QMouseEvent
from gui.themes.theme_manager import theme_manager
from gui.core.config import SPRITE_SHEET
from gui.utils.logger import get_logger

logger = get_logger(__name__)

class PiecePalette(QWidget):
    """
    A tray containing all available chess pieces (White and Black) plus an Eraser.
    Users click a tool to make it the 'active' tool for painting on the board.
    """
    tool_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = theme_manager.get_theme()
        
        # Load spritesheet
        self.pieces = {}
        self._load_sprites()
        
        self.active_tool = 'P' # Default to White Pawn
        self.piece_order = [
            'K', 'Q', 'R', 'B', 'N', 'P',
            'k', 'q', 'r', 'b', 'n', 'p',
            'ERASER'
        ]
        
        self.setFixedSize(140, 400)
        self.setMouseTracking(True)
        self.hover_idx = -1

    def _load_sprites(self):
        if not SPRITE_SHEET.exists():
            logger.error("Sprite sheet missing!")
            return
            
        sheet = QPixmap(str(SPRITE_SHEET))
        pw = sheet.width() // 6
        ph = sheet.height() // 2
        
        order = ('K', 'Q', 'B', 'N', 'R', 'P', 'k', 'q', 'b', 'n', 'r', 'p')
        idx = 0
        for row in range(2):
            for col in range(6):
                self.pieces[order[idx]] = sheet.copy(col * pw, row * ph, pw, ph).scaled(
                    48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
                idx += 1

    def mouseMoveEvent(self, event: QMouseEvent):
        y = event.position().y()
        idx = int(y // 50)
        if 0 <= idx < len(self.piece_order):
            if self.hover_idx != idx:
                self.hover_idx = idx
                self.update()
        else:
            if self.hover_idx != -1:
                self.hover_idx = -1
                self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            y = event.position().y()
            idx = int(y // 50)
            if 0 <= idx < len(self.piece_order):
                self.active_tool = self.piece_order[idx]
                self.tool_selected.emit(self.active_tool)
                self.update()

    def leaveEvent(self, event):
        self.hover_idx = -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for i, tool in enumerate(self.piece_order):
            rect = QRectF(10, i * 50, 120, 46)
            
            # Background
            if tool == self.active_tool:
                painter.fillRect(rect, QColor(0, 229, 255, 60))
                painter.setPen(QPen(QColor(0, 229, 255), 2))
                painter.drawRect(rect)
            elif i == self.hover_idx:
                painter.fillRect(rect, QColor(255, 255, 255, 15))
                painter.setPen(Qt.PenStyle.NoPen)
            else:
                painter.fillRect(rect, QColor(22, 17, 38, 100))
                painter.setPen(QPen(QColor(255, 255, 255, 20), 1))
                painter.drawRect(rect)
            
            # Icon
            if tool == 'ERASER':
                painter.setPen(QColor(255, 64, 129))
                painter.setFont(theme_manager.get_font("Outfit", 12, weight=700))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Clear Sq")
            else:
                pixmap = self.pieces.get(tool)
                if pixmap:
                    # Draw piece centered
                    px = rect.x() + (rect.width() - 32) / 2
                    py = rect.y() + (rect.height() - 32) / 2
                    painter.drawPixmap(int(px), int(py), 32, 32, pixmap)


class BoardEditorCanvas(QWidget):
    """
    An 8x8 interactive grid for placing chess pieces.
    """
    board_changed = Signal(str) # Emits the new FEN

    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = theme_manager.get_theme()
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.active_tool = 'P'
        self.pieces = {}
        self.square_size = 50
        self.setFixedSize(400, 400)
        
        self.load_starting_position()

    def set_pieces_cache(self, pieces_dict):
        self.pieces = pieces_dict
        self.update()

    def set_active_tool(self, tool):
        self.active_tool = tool

    def clear_board(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self._emit_fen()
        self.update()

    def load_starting_position(self):
        start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        self.load_from_fen(start_fen)

    def load_from_fen(self, fen: str):
        placement = fen.strip().split()[0]
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        rows = placement.split('/')
        for r_idx, row in enumerate(rows):
            if r_idx >= 8: break
            c_idx = 0
            for char in row:
                if c_idx >= 8: break
                if char.isdigit():
                    c_idx += int(char)
                else:
                    self.grid[r_idx][c_idx] = char
                    c_idx += 1
        self._emit_fen()
        self.update()

    def _emit_fen(self):
        rows = []
        for row in self.grid:
            empty_count = 0
            row_str = ""
            for cell in row:
                if cell is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += cell
            if empty_count > 0:
                row_str += str(empty_count)
            rows.append(row_str)
        fen_placement = "/".join(rows)
        # Default suffix for standard chess board analysis
        full_fen = f"{fen_placement} w - - 0 1"
        self.board_changed.emit(full_fen)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._apply_tool(event.position())

    def mouseMoveEvent(self, event: QMouseEvent):
        # Allow painting by dragging
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._apply_tool(event.position())

    def _apply_tool(self, pos):
        c = int(pos.x() // self.square_size)
        r = int(pos.y() // self.square_size)
        
        if 0 <= r < 8 and 0 <= c < 8:
            target_val = None if self.active_tool == 'ERASER' else self.active_tool
            if self.grid[r][c] != target_val:
                self.grid[r][c] = target_val
                self._emit_fen()
                self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        self.square_size = w / 8.0

        for r in range(8):
            for c in range(8):
                is_light = (r + c) % 2 == 0
                color = QColor(216, 210, 236) if is_light else QColor(43, 29, 97) # Lavender/Indigo
                rect = QRectF(c * self.square_size, r * self.square_size, self.square_size, self.square_size)
                painter.fillRect(rect, color)
                
                piece = self.grid[r][c]
                if piece and piece in self.pieces:
                    pixmap = self.pieces[piece]
                    # Scale to fit nicely in square
                    px = rect.x() + (self.square_size - 40) / 2
                    py = rect.y() + (self.square_size - 40) / 2
                    painter.drawPixmap(int(px), int(py), 40, 40, pixmap)
        
        # Draw border
        painter.setPen(QPen(QColor(0, 229, 255), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(0, 0, w, h)


class ToolsView(QWidget):
    def __init__(self, engine_manager=None, parent=None):
        super().__init__(parent)
        self.engine_manager = engine_manager
        self.theme = theme_manager.get_theme()
        
        self.current_fen = ""
        self.validation_pending = False
        
        self._init_ui()
        self._connect_signals()
        
        # Trigger initial sync
        self.canvas.load_starting_position()

    def _init_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Left: Palette and Board
        left_panel = QWidget()
        left_layout = QHBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.palette = PiecePalette()
        self.canvas = BoardEditorCanvas()
        self.canvas.set_pieces_cache(self.palette.pieces)
        
        self.palette.tool_selected.connect(self.canvas.set_active_tool)
        self.canvas.board_changed.connect(self.on_fen_changed)
        
        left_layout.addWidget(self.palette)
        left_layout.addWidget(self.canvas)
        left_layout.addStretch()
        
        layout.addWidget(left_panel, stretch=2)

        # Right: FEN Export, Import, and Validation
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: rgba(22, 17, 38, 0.70); border: 1px solid rgba(0, 229, 255, 0.12); border-radius: 12px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(15)

        title = QLabel("Board Setup Editor")
        title.setStyleSheet(f"font-family: 'Outfit'; font-size: 18px; font-weight: bold; color: {self.theme.console_in.name()}; border: none;")
        right_layout.addWidget(title)

        desc = QLabel("Visually place pieces to construct custom positions. The FEN code is generated in real-time and validated by the engine.")
        desc.setStyleSheet("font-family: 'Outfit'; font-size: 12px; color: #B0BEC5; border: none;")
        desc.setWordWrap(True)
        right_layout.addWidget(desc)

        # FEN display field
        right_layout.addWidget(QLabel("Current FEN Code:"))
        self.fen_input = QLineEdit()
        self.fen_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 0, 0, 0.3);
                color: #FFFFFF;
                padding: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                font-family: 'Consolas', monospace;
            }
        """)
        right_layout.addWidget(self.fen_input)

        # Action Buttons
        btn_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("Apply FEN")
        self.apply_btn.clicked.connect(lambda: self.canvas.load_from_fen(self.fen_input.text()))
        
        self.copy_btn = QPushButton("Copy FEN")
        self.copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.fen_input.text()))
        
        for btn in (self.apply_btn, self.copy_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.05);
                    color: #E0F7FA;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover { background-color: rgba(0, 229, 255, 0.2); border-color: #00E5FF; }
            """)
            btn_layout.addWidget(btn)
        
        right_layout.addLayout(btn_layout)

        # Board Actions
        board_btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Board")
        self.clear_btn.clicked.connect(self.canvas.clear_board)
        
        self.start_btn = QPushButton("Starting Position")
        self.start_btn.clicked.connect(self.canvas.load_starting_position)
        
        for btn in (self.clear_btn, self.start_btn):
            btn.setStyleSheet(self.apply_btn.styleSheet())
            board_btn_layout.addWidget(btn)
            
        right_layout.addLayout(board_btn_layout)

        # Validation Status
        right_layout.addStretch()
        self.val_label = QLabel("Validation Status: Pending...")
        self.val_label.setStyleSheet("font-family: 'Outfit'; font-size: 14px; font-weight: bold; color: #B0BEC5; border: none;")
        self.val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.val_label)

        layout.addWidget(right_panel, stretch=1)

    def _connect_signals(self) -> None:
        if self.engine_manager:
            self.engine_manager.validate_received.connect(self.on_validation_result)

    def set_engine_manager(self, mgr) -> None:
        self.engine_manager = mgr
        self._connect_signals()
        self.validate_current_fen()

    def on_fen_changed(self, fen: str):
        self.current_fen = fen
        self.fen_input.setText(fen)
        self.validate_current_fen()

    def validate_current_fen(self):
        if self.engine_manager:
            self.val_label.setText("Validation Status: Checking...")
            self.val_label.setStyleSheet("font-family: 'Outfit'; font-size: 14px; font-weight: bold; color: #FFEB3B; border: none;")
            self.engine_manager.send_position(self.current_fen)
            self.engine_manager.send_command("bluie-debug validate")

    def on_validation_result(self, is_valid: bool):
        if is_valid:
            self.val_label.setText("Validation Status: Valid Setup")
            self.val_label.setStyleSheet("font-family: 'Outfit'; font-size: 14px; font-weight: bold; color: #00E676; border: none;")
        else:
            self.val_label.setText("Validation Status: Invalid Setup")
            self.val_label.setStyleSheet("font-family: 'Outfit'; font-size: 14px; font-weight: bold; color: #FF1744; border: none;")

    def update_theme(self) -> None:
        self.theme = theme_manager.get_theme()
        self.setStyleSheet(f"background-color: {self.theme.panel_background.name()}; color: {self.theme.panel_text.name()};")
        self.update()
