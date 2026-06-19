import math
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
import chess

from gui.app.ui.templates import StyledWidget
from gui.app.game.models.game_state import GameModes
from gui.utils import get_logger

from .evaluation_bar import EvaluationBar
from .telemetry_view import TelemetryView

logger = get_logger(__name__)

class EvaluationPanel(StyledWidget):
    """
    Main panel displaying evaluation bar and engine telemetry.
    """
    def __init__(self, app_manager, parent=None):
        super().__init__("evaluationPanel", parent)
        self._manager = app_manager
        self._game_manager = self._manager.game
        
        self._connected_main = False
        self._connected_white = False
        self._connected_black = False
        
        self.setMinimumHeight(220)
        self.setup_ui()
        self._connect_signals()
        self._update_layout_for_mode(self._game_manager.state.mode)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 1. Header Title
        self.lbl_title = QLabel("ENGINE ANALYSIS", self)
        self.lbl_title.setObjectName("panelTitle")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.lbl_title.font()
        font.setBold(True)
        font.setPointSize(12)
        self.lbl_title.setFont(font)
        main_layout.addWidget(self.lbl_title)

        # 2. Evaluation dashboard
        self.eval_container = QWidget(self)
        self.eval_container.setObjectName("evalContainer")
        eval_layout = QVBoxLayout(self.eval_container)
        eval_layout.setContentsMargins(0, 0, 0, 0)
        eval_layout.setSpacing(6)

        header_layout = QHBoxLayout()
        self.lbl_score = QLabel("+0.00", self)
        self.lbl_score.setObjectName("largeScoreLabel")
        font_score = self.lbl_score.font()
        font_score.setBold(True)
        font_score.setPointSize(20)
        self.lbl_score.setFont(font_score)
        
        self.lbl_active_side = QLabel("Idle", self)
        self.lbl_active_side.setObjectName("activeSideLabel")
        self.lbl_active_side.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        header_layout.addWidget(self.lbl_score)
        header_layout.addWidget(self.lbl_active_side, 1)
        eval_layout.addLayout(header_layout)

        self.eval_bar = EvaluationBar(self)
        eval_layout.addWidget(self.eval_bar)
        main_layout.addWidget(self.eval_container)

        # Divider
        divider = QFrame(self)
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setObjectName("evalPanelDivider")
        main_layout.addWidget(divider)

        # 3. Telemetry and PV stacked view
        self.telemetry_view = TelemetryView(self)
        main_layout.addWidget(self.telemetry_view)

    def _connect_signals(self):
        self._game_manager.state.game_mode_changed.connect(self._on_mode_changed)
        self._manager.board.position_changed.connect(self._on_position_changed)
        self._connect_engine_sessions()

    def _on_mode_changed(self, mode: GameModes):
        self._update_layout_for_mode(mode)
        self._connect_engine_sessions()
        self._reset_ui()

    def _on_position_changed(self, fen: str):
        board_session = self._manager.board.session
        if board_session and not board_session.move_stack:
            for sid in ["main", "white_engine", "black_engine"]:
                sess = self._manager.engine.get_session(sid)
                if sess:
                    sess.analysis_state.reset()
            self._reset_ui()
        else:
            self._update_all_displays()

    def _update_layout_for_mode(self, mode: GameModes):
        if mode == GameModes.ENGINE_VS_ENGINE:
            self.setMinimumHeight(380)
            self.telemetry_view.show_mode(True)
        else:
            self.setMinimumHeight(220)
            self.telemetry_view.show_mode(False)

    def _connect_engine_sessions(self):
        self._disconnect_engine_sessions()
        
        for sid in ["main", "white_engine", "black_engine"]:
            if not self._manager.engine.has_session(sid):
                self._manager.engine.create_session(sid)
        
        main_sess = self._manager.engine.get_session("main")
        if main_sess:
            main_sess.analysis_state.updated.connect(self._on_main_updated)
            self._connected_main = True
            
        white_sess = self._manager.engine.get_session("white_engine")
        if white_sess:
            white_sess.analysis_state.updated.connect(self._on_white_updated)
            self._connected_white = True
            
        black_sess = self._manager.engine.get_session("black_engine")
        if black_sess:
            black_sess.analysis_state.updated.connect(self._on_black_updated)
            self._connected_black = True

    def _disconnect_engine_sessions(self):
        if self._connected_main:
            try:
                self._manager.engine.get_session("main").analysis_state.updated.disconnect(self._on_main_updated)
            except Exception as e:
                logger.debug("Failed to disconnect main engine session analysis updates: %s", e)
            self._connected_main = False

        if self._connected_white:
            try:
                self._manager.engine.get_session("white_engine").analysis_state.updated.disconnect(self._on_white_updated)
            except Exception as e:
                logger.debug("Failed to disconnect white engine session analysis updates: %s", e)
            self._connected_white = False

        if self._connected_black:
            try:
                self._manager.engine.get_session("black_engine").analysis_state.updated.disconnect(self._on_black_updated)
            except Exception as e:
                logger.debug("Failed to disconnect black engine session analysis updates: %s", e)
            self._connected_black = False

    def _reset_ui(self):
        self.lbl_score.setText("+0.00")
        self.lbl_active_side.setText("Idle")
        self.eval_bar.set_win_chance(0.5)
        self.telemetry_view.reset_displays()

    # ---- FORMATTING HELPERS ----
    def _format_nps(self, nps: int) -> str:
        if nps >= 1_000_000:
            return f"{nps / 1_000_000:.2f} M"
        if nps >= 1_000:
            return f"{nps / 1_000:.1f} k"
        return str(nps)

    def _format_time(self, ms: int) -> str:
        if ms >= 1000:
            return f"{ms / 1000:.2f}s"
        return f"{ms}ms"

    def _format_score(self, score: float, is_mate: bool, mate_in: int | None) -> str:
        if is_mate:
            if mate_in is not None:
                return f"+M{mate_in}" if mate_in > 0 else f"-M{abs(mate_in)}"
            return "Mate"
        if abs(score) < 0.005:
            score = 0.0
        return f"+{score:.2f}" if score >= 0 else f"{score:.2f}"

    def _get_win_chance(self, score: float, is_mate: bool, mate_in: int | None) -> float:
        if is_mate:
            return 0.99 if (mate_in or 0) > 0 else 0.01
        return 1.0 / (1.0 + math.exp(-0.4 * score))



    # ---- RE-EVALUATE AND UPDATE DISPLAYS ----
    def _update_all_displays(self):
        mode = self._game_manager.state.mode
        if mode == GameModes.ENGINE_VS_ENGINE:
            self._update_dual_displays()
        else:
            self._update_single_displays()

    def _update_single_displays(self):
        sess = self._manager.engine.get_session("main")
        if not sess:
            return
        
        state = sess.analysis_state
        board = self._manager.board.session.view_board
        is_white_turn = (board.turn == chess.WHITE)
        
        score_val = state.score if is_white_turn else -state.score
        mate_val = state.mate_in
        if state.is_mate and mate_val is not None:
            mate_val = mate_val if is_white_turn else -mate_val
            
        score_text = self._format_score(score_val, state.is_mate, mate_val)
        self.lbl_score.setText(score_text)
        
        win_chance = self._get_win_chance(score_val, state.is_mate, mate_val)
        self.eval_bar.set_win_chance(win_chance)
        
        status = sess.engine_info.status
        self.lbl_active_side.setText(f"Main Engine ({status})")
        
        view = self.telemetry_view
        view.lbl_depth.setText(f"{state.depth}")
        view.lbl_nodes.setText(f"{state.nodes:,}")
        view.lbl_nps.setText(self._format_nps(state.nps))
        view.lbl_time.setText(self._format_time(state.time_ms))
        # Only show PV line if the engine is actively searching
        if status == "Searching" and state.pv:
            view.txt_pv.setText(self._manager.board.format_uci_sequence(state.pv))
        else:
            view.txt_pv.clear()

    def _update_dual_displays(self):
        white_sess = self._manager.engine.get_session("white_engine")
        black_sess = self._manager.engine.get_session("black_engine")
        if not white_sess or not black_sess:
            return
            
        board = self._manager.board.session.view_board
        is_white_turn = (board.turn == chess.WHITE)
        
        w_state = white_sess.analysis_state
        view = self.telemetry_view
        view.lbl_depth_w.setText(f"{w_state.depth}")
        view.lbl_nodes_w.setText(f"{w_state.nodes:,}")
        view.lbl_nps_w.setText(self._format_nps(w_state.nps))
        view.lbl_time_w.setText(self._format_time(w_state.time_ms))
        w_score_text = self._format_score(w_state.score, w_state.is_mate, w_state.mate_in)
        view.lbl_score_w.setText(w_score_text)
        
        w_status = white_sess.engine_info.status
        if w_status == "Searching" and w_state.pv:
            view.txt_pv_w.setText(self._manager.board.format_uci_sequence(w_state.pv))
        else:
            view.txt_pv_w.clear()

        b_state = black_sess.analysis_state
        b_score_val = -b_state.score
        b_mate_val = b_state.mate_in
        if b_state.is_mate and b_mate_val is not None:
            b_mate_val = -b_mate_val
            
        view.lbl_depth_b.setText(f"{b_state.depth}")
        view.lbl_nodes_b.setText(f"{b_state.nodes:,}")
        view.lbl_nps_b.setText(self._format_nps(b_state.nps))
        view.lbl_time_b.setText(self._format_time(b_state.time_ms))
        b_score_text = self._format_score(b_score_val, b_state.is_mate, b_mate_val)
        view.lbl_score_b.setText(b_score_text)
        
        b_status = black_sess.engine_info.status
        if b_status == "Searching" and b_state.pv:
            view.txt_pv_b.setText(self._manager.board.format_uci_sequence(b_state.pv))
        else:
            view.txt_pv_b.clear()

        active_sess = white_sess if is_white_turn else black_sess
        active_state = active_sess.analysis_state
        
        score_val = active_state.score if is_white_turn else -active_state.score
        mate_val = active_state.mate_in
        if active_state.is_mate and mate_val is not None:
            mate_val = mate_val if is_white_turn else -mate_val
            
        score_text = self._format_score(score_val, active_state.is_mate, mate_val)
        self.lbl_score.setText(score_text)
        
        win_chance = self._get_win_chance(score_val, active_state.is_mate, mate_val)
        self.eval_bar.set_win_chance(win_chance)
        
        active_label = "White's turn" if is_white_turn else "Black's turn"
        status = active_sess.engine_info.status
        self.lbl_active_side.setText(f"{active_label} ({status})")

    # ---- SLOTS ----
    @Slot()
    def _on_main_updated(self):
        if self._game_manager.state.mode != GameModes.ENGINE_VS_ENGINE:
            self._update_single_displays()

    @Slot()
    def _on_white_updated(self):
        if self._game_manager.state.mode == GameModes.ENGINE_VS_ENGINE:
            self._update_dual_displays()

    @Slot()
    def _on_black_updated(self):
        if self._game_manager.state.mode == GameModes.ENGINE_VS_ENGINE:
            self._update_dual_displays()

    def closeEvent(self, event):
        self._disconnect_engine_sessions()
        super().closeEvent(event)
