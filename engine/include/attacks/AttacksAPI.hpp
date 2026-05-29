#pragma once

#include "board/Board.hpp"
#include "core/Types.hpp"

namespace Bluie
{
namespace Attacks
{

/**
 * @brief Identifies all active pieces of attackerSide threatening a given square.
 * 
 * Aggregates threat vectors by checking opposing piece positions from the target square:
 * - Opponent pawns using opposite-side pawn attack tables.
 * - Opponent knights and kings using knight and king attack tables.
 * - Opponent sliding pieces (bishops, rooks, queens) utilizing precomputed magic bitboard lookups.
 * 
 * @param board The active position board.
 * @param sq The target square index.
 * @param attackerSide The side of the attacking pieces.
 * @return Bitboard with bits set at the squares of all attacking pieces.
 */
Bitboard attacksTo(const Board& board, Square sq, Side attackerSide);

/**
 * @brief Checks if a square is currently attacked/threatened by any piece of attackerSide.
 * 
 * Used for:
 * - Filtering pseudo-legal moves (checking if friendly king is exposed).
 * - Determining castling rights validity (checking intermediate and start squares).
 * 
 * @param board The active position board.
 * @param sq The target square index.
 * @param attackerSide The side of the attacking pieces.
 * @return True if square is attacked, False otherwise.
 */
bool isSquareAttacked(const Board& board, Square sq, Side attackerSide);

} // namespace Attacks
} // namespace Bluie
