"""
Unit tests for the standalone move-history panel.

This module verifies the panel's rendering, state-update slots, and emitted
navigation intents without connecting it to the application coordinator.
"""

from PySide6.QtCore import Qt

from gui.ui.panels.move_history_panel import MoveHistoryPanel


class TestMoveHistoryPanel:
    """Test suite for move rendering and navigation intents."""

    def test_initialization_shows_a_clear_empty_state(self, qtbot):
        """Verify a new panel presents its empty state and disabled navigation."""
        panel = MoveHistoryPanel(parent=None)
        qtbot.addWidget(panel)

        assert panel.objectName() == "moveHistoryPanel"
        assert panel.empty_label.text() == "No moves yet"
        assert panel.empty_label.isHidden() is False
        assert panel.move_table.isHidden() is True
        assert panel.first_button.isEnabled() is False
        assert panel.next_button.isEnabled() is False

    def test_set_moves_groups_san_moves_by_full_move_and_selects_current_ply(self, qtbot):
        """Verify SAN moves render in white/black columns with a selected ply."""
        panel = MoveHistoryPanel(parent=None)
        qtbot.addWidget(panel)

        panel.set_moves(["e4", "e5", "Nf3"], current_ply=1)

        assert panel.empty_label.isHidden() is True
        assert panel.move_table.rowCount() == 2
        assert panel.move_table.item(0, 0).text() == "1."
        assert panel.move_table.item(0, 1).text() == "e4"
        assert panel.move_table.item(0, 2).text() == "e5"
        assert panel.move_table.item(1, 1).text() == "Nf3"
        assert panel.move_table.currentItem().data(Qt.ItemDataRole.UserRole) == 1
        assert panel.previous_button.isEnabled() is True
        assert panel.next_button.isEnabled() is True

    def test_clicking_a_move_emits_its_zero_based_ply(self, qtbot):
        """Verify a user move selection emits the matching chronological ply index."""
        panel = MoveHistoryPanel(parent=None)
        qtbot.addWidget(panel)
        panel.set_moves(["e4", "e5", "Nf3"])

        item = panel.move_table.item(1, 1)
        with qtbot.waitSignal(panel.move_selected, timeout=1000) as blocker:
            panel.move_table.itemClicked.emit(item)

        assert blocker.args == [2]

    def test_navigation_buttons_emit_view_navigation_intents(self, qtbot):
        """Verify navigation buttons emit decoupled coordinator intents."""
        panel = MoveHistoryPanel(parent=None)
        qtbot.addWidget(panel)
        panel.set_moves(["e4", "e5"], current_ply=0)

        with qtbot.waitSignal(panel.last_move_requested, timeout=1000):
            qtbot.mouseClick(panel.last_button, Qt.MouseButton.LeftButton)

        panel.set_current_ply(1)
        with qtbot.waitSignal(panel.previous_move_requested, timeout=1000):
            qtbot.mouseClick(panel.previous_button, Qt.MouseButton.LeftButton)
