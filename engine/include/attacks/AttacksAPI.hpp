#pragma once

#include "board/Board.hpp"
#include "core/Types.hpp"

namespace Bluie
{
namespace Attacks
{

/**
 * @brief Identifies all active pieces of attackerSide threatening a given square.
 * @param board The active position board.
 * @param sq The target square index.
 * @param attackerSide The side of the attacking pieces.
 * @return Bitboard with bits set at the squares of all attacking pieces.
 */
Bitboard attacksTo(const Board& board, Square sq, Side attackerSide);

/**
 * @brief Checks if a square is currently attacked/threatened by any piece of attackerSide.
 * @param board The active position board.
 * @param sq The target square index.
 * @param attackerSide The side of the attacking pieces.
 * @return True if square is attacked, False otherwise.
 */
bool isSquareAttacked(const Board& board, Square sq, Side attackerSide);

} // namespace Attacks
} // namespace Bluie
