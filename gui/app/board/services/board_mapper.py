"""Provide board mapping helpers for coordinate conversions.

This module provides the BoardMapper class for converting chess square indices and
algebraic coordinate notations between engine standards and python-chess representations.
"""

import chess


class BoardMapper:
    """Provide conversions between UCI engine board indices and python-chess square coordinates."""

    @staticmethod
    def index_to_square(index: int) -> int:
        """Return the python-chess square index for a given engine board index.

        Args:
            index: Engine board square index in the range 0..63.

        Returns:
            The corresponding python-chess square index.
        """
        return chess.parse_square(
            BoardMapper.index_to_coord(index)
        )

    @staticmethod
    def index_to_coord(index: int) -> str:
        """Return the board coordinate string for a given engine board index.

        Args:
            index: Engine board square index in the range 0..63.

        Returns:
            A coordinate string such as 'a1' through 'h8'.
        """
        file = index % 8
        rank = 7 - index // 8

        return f"{chr(ord('a') + file)}{rank + 1}"

    @staticmethod
    def coord_to_index(coord: str) -> int:
        """Return the engine board index for a given coordinate string.

        Args:
            coord: A coordinate string such as 'a1' through 'h8'.

        Returns:
            The corresponding engine board square index.
        """
        square = chess.parse_square(coord)

        file = chess.square_file(square)
        rank = chess.square_rank(square)

        return (7 - rank) * 8 + file
