#pragma once

#include "core/Types.hpp"

/**
 * @brief Maximum possible occupancies for sliding piece magic lookup array.
 */
constexpr int MAX_OCCUPANCIES = 4096;

/**
 * @brief Number of search trials before giving up on finding a magic number.
 */
constexpr int MAGIC_TRIES = 100000000;

/**
 * @brief Sets a piece occupancy state for a given index and attack mask.
 * 
 * Used during magic bitboard lookup table generation.
 * 
 * @param index Occupancy state index (0 to 2^bits - 1).
 * @param bitsInMask Number of set bits in the attack mask.
 * @param attackMask The base slider occupancy mask.
 * @return Bitboard representing chess board occupancy for this state.
 */
Bitboard setOccupancy(int index, int bitsInMask, Bitboard attackMask);

/**
 * @brief Finds a valid magic number candidate using XORShift hashing.
 * 
 * @param square The target square to find the magic number for.
 * @param relevantBits The number of relevant bits in the slider mask.
 * @param bishop True for bishop lookups, false for rook lookups.
 * @return The 64-bit magic number candidate, or 0ULL if search fails.
 */
Bitboard findMagicNumber(Square square, int relevantBits, bool bishop);
