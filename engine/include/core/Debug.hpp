#pragma once

#include "core/Types.hpp"

namespace Bluie
{
namespace Debug
{

/**
 * @brief Print the bitboard in a human-readable 8x8 grid format to console.
 * @param b The 64-bit Chessboard occupancy bitboard to print.
 */
void printBitboard(Bluie::Bitboard b);

} // namespace Debug
} // namespace Bluie