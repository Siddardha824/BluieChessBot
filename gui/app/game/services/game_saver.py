"""Game serialization and export services.

This module provides the GameSaver utility class, which serializes and writes
chess game records and engine state metadata into PGN formats on disk.
"""

from __future__ import annotations
import json
import chess.pgn
from typing import TYPE_CHECKING
from gui.utils import get_logger

if TYPE_CHECKING:
    from gui.app.board.services.move_node import MoveNode

logger = get_logger(__name__)


class GameSaver:
    """Provide static utility methods for serializing and exporting chess games.

    This class handles formatting the game state history (represented by a MoveNode)
    and writing it out into PGN files, incorporating active chess engine metadata.
    """

    @staticmethod
    def save_pgn(filepath: str, root_node: MoveNode, engine_info: dict) -> bool:
        """Export the chess game history and engine metadata to a PGN file.

        Args:
            filepath: The target system path where the PGN file will be written.
            root_node: The root move node of the game tree.
            engine_info: A dictionary containing active engine profiles and statuses.

        Returns:
            True if the file was written successfully, False otherwise.
        """
        try:
            if engine_info:
                root_node.headers["Engine"] = json.dumps(engine_info)

            with open(filepath, 'w', encoding='utf-8') as f:
                expoter = chess.pgn.FileExporter(f)

                root_node.accept(expoter)

            logger.info(f"Game saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save game as PGN: {e}")
            return False