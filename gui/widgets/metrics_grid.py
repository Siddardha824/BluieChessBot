# gui/widgets/metrics_grid.py

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel
from gui.views.analysis.styles.analysis_styles import get_grid_lbl_style, get_grid_val_style
from .themed_widget import ThemedWidget

class MetricsGrid(ThemedWidget):
    def __init__(self, theme, initial_hash="Not Available", initial_threads="Not Available", parent=None):
        self.initial_hash = initial_hash
        self.initial_threads = initial_threads
        super().__init__(theme, parent)

    def setup_ui(self):
        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setVerticalSpacing(10)
        
        # Grid Labels
        lbl_nodes = QLabel("Nodes")
        lbl_nps = QLabel("NPS")
        lbl_hash = QLabel("Hash")
        lbl_threads = QLabel("Threads")
        
        for lbl in [lbl_nodes, lbl_nps, lbl_hash, lbl_threads]:
            lbl.setStyleSheet(get_grid_lbl_style(self.theme))
            
        # Grid Value holders
        self.val_nodes = QLabel("-")
        self.val_nps = QLabel("-")
        
        init_hash_str = f"{self.initial_hash} MB" if isinstance(self.initial_hash, int) else str(self.initial_hash)
        self.val_hash = QLabel(init_hash_str)
        self.val_threads = QLabel(str(self.initial_threads))
        
        for val in [self.val_nodes, self.val_nps, self.val_hash, self.val_threads]:
            val.setStyleSheet(get_grid_val_style(self.theme))
            
        grid_layout.addWidget(lbl_nodes, 0, 0)
        grid_layout.addWidget(self.val_nodes, 1, 0)
        grid_layout.addWidget(lbl_nps, 0, 1)
        grid_layout.addWidget(self.val_nps, 1, 1)
        grid_layout.addWidget(lbl_hash, 0, 2)
        grid_layout.addWidget(self.val_hash, 1, 2)
        grid_layout.addWidget(lbl_threads, 0, 3)
        grid_layout.addWidget(self.val_threads, 1, 3)

    def set_config(self, hash_size, threads) -> None:
        """Sets persistent config parameters like Hash size and Threads count."""
        if hash_size == "Not Available" or hash_size is None:
            self.val_hash.setText("Not Available")
        else:
            self.val_hash.setText(f"{hash_size} MB")
            
        if threads == "Not Available" or threads is None:
            self.val_threads.setText("Not Available")
        else:
            self.val_threads.setText(str(threads))

    def set_search_metrics(self, nodes: int, nps: float) -> None:
        """Sets real-time search metrics."""
        self.val_nodes.setText(f"{nodes:,}" if nodes > 0 else "-")
        self.val_nps.setText(f"{nps / 1000000.0:.2f} Mn/s" if nps > 0 else "-")

    def clear(self) -> None:
        self.val_nodes.setText("-")
        self.val_nps.setText("-")

    def apply_theme(self) -> None:
        for lbl in self.findChildren(QLabel):
            if lbl.text() in ["Nodes", "NPS", "Hash", "Threads"]:
                lbl.setStyleSheet(get_grid_lbl_style(self.theme))
            elif lbl in [self.val_nodes, self.val_nps, self.val_hash, self.val_threads]:
                lbl.setStyleSheet(get_grid_val_style(self.theme))
