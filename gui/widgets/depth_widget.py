# gui/widgets/depth_widget.py

from PySide6.QtWidgets import QVBoxLayout, QLabel, QProgressBar

from .themed_widget import ThemedWidget
from gui.views.analysis.styles.analysis_styles import get_depth_title_style, get_depth_progress_style

class DepthWidget(ThemedWidget):

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        
        self.lbl_depth_title = QLabel("Depth 0/0")
        self.lbl_depth_title.setStyleSheet(get_depth_title_style(self.theme))
        
        self.depth_progress = QProgressBar()
        self.depth_progress.setRange(0, 30)
        self.depth_progress.setValue(0)
        self.depth_progress.setTextVisible(False)
        self.depth_progress.setFixedHeight(6)
        self.depth_progress.setStyleSheet(get_depth_progress_style(self.theme))
        
        layout.addWidget(self.lbl_depth_title)
        layout.addWidget(self.depth_progress)

    def set_depth(self, depth: int) -> None:
        self.lbl_depth_title.setText(f"Depth {depth}/{depth + 14}")
        self.depth_progress.setValue(min(depth, 30))

    def clear(self) -> None:
        self.lbl_depth_title.setText("Depth 0/0")
        self.depth_progress.setValue(0)

    def apply_theme(self) -> None:
        self.lbl_depth_title.setStyleSheet(get_depth_title_style(self.theme))
        self.depth_progress.setStyleSheet(get_depth_progress_style(self.theme))
