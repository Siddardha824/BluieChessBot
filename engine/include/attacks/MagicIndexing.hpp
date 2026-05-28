#pragma once

#include "attacks/AttackTables.hpp"
#include "attacks/MagicNumbers.hpp"
#include "attacks/SliderMasks.hpp"
#include "core/Types.hpp"
#include <cstddef>

namespace Bluie
{
namespace Attacks
{

/**
 * @brief Maps a bishop square and board occupancy to its precomputed table index using hashing.
 *
 * @param square The square the bishop is standing on.
 * @param occupancy The current combined occupancy mask of all pieces on the board.
 * @return The mapped magic index for bishop lookup.
 */
constexpr std::size_t getBishopMagicIndex(Square square, Bitboard occupancy)
{
    occupancy &= bishopOccupancyMasks[toIndex(square)];

    return (occupancy * bishopMagicNumbers[toIndex(square)]) >>
           (64 - bishopRelevantBits[toIndex(square)]);
}

/**
 * @brief Maps a rook square and board occupancy to its precomputed table index using hashing.
 *
 * @param square The square the rook is standing on.
 * @param occupancy The current combined occupancy mask of all pieces on the board.
 * @return The mapped magic index for rook lookup.
 */
constexpr std::size_t getRookMagicIndex(Square square, Bitboard occupancy)
{
    occupancy &= rookOccupancyMasks[toIndex(square)];

    return (occupancy * rookMagicNumbers[toIndex(square)]) >>
           (64 - rookRelevantBits[toIndex(square)]);
}

/**
 * @brief Combines bishop and rook table lookups to get queen attacks.
 *
 * @param square The square the queen is standing on.
 * @param occupancy The current combined occupancy mask of all pieces on the board.
 * @return Bitboard of all squares attacked by the queen.
 */
constexpr Bitboard getQueenAttack(Square square, Bitboard occupancy)
{
    return bishopAttacks[toIndex(square)][getBishopMagicIndex(square, occupancy)] |
           rookAttacks[toIndex(square)][getRookMagicIndex(square, occupancy)];
}

} // namespace Attacks
} // namespace Bluie
