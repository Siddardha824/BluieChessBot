#pragma once

#include "core/Types.hpp"

namespace Bluie
{
namespace Tools
{

/**
 * @brief Computes bishop attack bitboard on-the-fly using ray casting.
 *
 * Used only for testing and magic number verification.
 *
 * @param square The square the bishop is standing on.
 * @param occupancy The board's current piece occupancy mask.
 * @return Bitboard of all squares attacked by the bishop.
 */
Bluie::Bitboard bishopAttacksOnTheFly(Square square, Bluie::Bitboard occupancy);

/**
 * @brief Computes rook attack bitboard on-the-fly using ray casting.
 *
 * Used only for testing and magic number verification.
 *
 * @param square The square the rook is standing on.
 * @param occupancy The board's current piece occupancy mask.
 * @return Bitboard of all squares attacked by the rook.
 */
Bluie::Bitboard rookAttacksOnTheFly(Square square, Bluie::Bitboard occupancy);

} // namespace Tools
} // namespace Bluie
