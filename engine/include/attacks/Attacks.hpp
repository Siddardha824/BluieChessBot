#pragma once

#include "core/Types.hpp"

/**
 * @brief Computes bishop attack bitboard on-the-fly using ray casting.
 * 
 * Used for magic bitboard generation and testing validation. Slow compared
 * to table lookups but 100% mathematically correct.
 * 
 * @param square The square the bishop is standing on.
 * @param occupancy The board's current piece occupancy mask.
 * @return Bitboard of all squares attacked by the bishop.
 */
Bitboard bishopAttacksOnTheFly(Square square, Bitboard occupancy);

/**
 * @brief Computes rook attack bitboard on-the-fly using ray casting.
 * 
 * Used for magic bitboard generation and testing validation. Slow compared
 * to table lookups but 100% mathematically correct.
 * 
 * @param square The square the rook is standing on.
 * @param occupancy The board's current piece occupancy mask.
 * @return Bitboard of all squares attacked by the rook.
 */
Bitboard rookAttacksOnTheFly(Square square, Bitboard occupancy);