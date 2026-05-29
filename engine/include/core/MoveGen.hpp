#pragma once

#include "board/Board.hpp"
#include "core/Types.hpp"

namespace Bluie
{

/**
 * @class MoveGen
 * @brief High-performance chess move generation system.
 *
 * Implements standard bitboard-based move generation. Generates all possible
 * pseudo-legal moves (sliding, leaper, pawns) and filters them into strictly
 * legal moves by verifying king safety after a hypothetical move simulation.
 */

class MoveGen
{
  public:
    MoveList getPseudoLegalMoves(const Board& board);
    MoveList getLegalMoves(const Board& board);
};

} // namespace Bluie