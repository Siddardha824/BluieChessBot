#pragma once

#include "board/Board.hpp"
#include "core/Types.hpp"

namespace Bluie
{

/**
 * @class MoveGen
 * @brief Generates all the possible pseudo legal moves and legal moves.
 *
 *
 *
 */

class MoveGen
{
  public:
    MoveList getPseudoLegalMoves(const Board& board);
    MoveList getLegalMoves(const Board& board);
};

} // namespace Bluie