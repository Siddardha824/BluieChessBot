from __future__ import annotations
import json
import chess.pgn
from typing import TYPE_CHECKING
from gui.utils import get_logger

if TYPE_CHECKING:
    from gui.app.board.services.move_node import MoveNode

logger = get_logger(__name__)

class GameSaver:
    @staticmethod
    def save_pgn(filepath: str, root_node: MoveNode, engine_info: dict) -> bool:
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