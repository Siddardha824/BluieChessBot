#pragma once

#include "core/Types.hpp"
#include <cstdint>

namespace Bluie
{
namespace Tools
{

/**
 * @brief Generates a pseudo-random 32-bit unsigned integer using XORShift.
 */
uint32_t getRandomU32Number();

/**
 * @brief Generates a pseudo-random 64-bit Chessboard occupancy bitboard.
 */
Bluie::Bitboard getRandomBitboardNumber();

/**
 * @brief Generates a magic number candidate through sparse bitwise intersection.
 */
Bluie::Bitboard generateMagicNumber();

} // namespace Tools
} // namespace Bluie