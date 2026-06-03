import chess

class BoardMapper:

    @staticmethod
    def index_to_square(index: int) -> int:
        return chess.parse_square(
            BoardMapper.index_to_coord(index)
        )

    @staticmethod
    def index_to_coord(index: int) -> str:
        file = index % 8
        rank = 7 - index // 8

        return f"{chr(ord('a') + file)}{rank + 1}"

    @staticmethod
    def coord_to_index(coord: str) -> int:
        square = chess.parse_square(coord)

        file = chess.square_file(square)
        rank = chess.square_rank(square)

        return (7 - rank) * 8 + file