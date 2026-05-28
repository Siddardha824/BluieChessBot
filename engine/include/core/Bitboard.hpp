#pragma once

#include "core/Types.hpp"
#include <bit>

namespace Bluie
{
namespace Bitboards
{

/**
 * @brief Mask constants for board file and rank boundary operations.
 */
namespace Masks
{
inline constexpr Bluie::Bitboard NOT_A_FILE =
    0xFEFEFEFEFEFEFEFEULL; ///< Everything except the A-file
inline constexpr Bluie::Bitboard NOT_H_FILE =
    0x7F7F7F7F7F7F7F7FULL; ///< Everything except the H-file

inline constexpr Bluie::Bitboard NOT_AB_FILE =
    0xFCFCFCFCFCFCFCFCULL; ///< Everything except A and B files
inline constexpr Bluie::Bitboard NOT_GH_FILE =
    0x3F3F3F3F3F3F3F3FULL; ///< Everything except G and H files

} // namespace Masks

/*-----------------------------------------------*\
    Bit manipulation functions for bitboards
\*-----------------------------------------------*/

/**
 * @brief Get a bitboard with only the bit at the specified square set to 1.
 * @param square The square index (0-63).
 * @return Bitboard with a single set bit.
 */
constexpr Bluie::Bitboard squareToBitboard(Square square)
{
    return 1ULL << toIndex(square);
}

/**
 * @brief Set the bit of a specific square to 1.
 * @param b The bitboard reference to modify.
 * @param square The square index (0-63).
 */
constexpr void setBit(Bluie::Bitboard& b, Square square)
{
    b |= (1ULL << toIndex(square));
}

/**
 * @brief Clear the bit of a specific square (set to 0).
 * @param b The bitboard reference to modify.
 * @param square The square index (0-63).
 */
constexpr void clearBit(Bluie::Bitboard& b, Square square)
{
    b &= ~(1ULL << toIndex(square));
}

/**
 * @brief Check if a specific square bit is set (occupied).
 * @param b The bitboard to check.
 * @param square The square index (0-63).
 * @return True if the square is occupied, false otherwise.
 */
constexpr bool getBit(Bluie::Bitboard b, Square square)
{
    return (b & (1ULL << toIndex(square))) != 0;
}

/**
 * @brief Move a piece from one square to another using a branchless XOR.
 * @param b The bitboard reference to modify.
 * @param fromSquare The square the piece is leaving.
 * @param toSquare The square the piece is entering.
 */
constexpr void movePiece(Bluie::Bitboard& b, Square fromSquare, Square toSquare)
{
    b ^= ((1ULL << toIndex(fromSquare)) | (1ULL << toIndex(toSquare)));
}

/**
 * @brief Count the number of active bits (set to 1) using C++20 std::popcount.
 * @param bitboard The bitboard to count.
 * @return Count of active bits.
 */
constexpr int countBits(Bluie::Bitboard bitboard)
{
    return static_cast<int>(std::popcount(bitboard));
}

/**
 * @brief Get the square index of the Least Significant set Bit (LSB) using C++20 std::countr_zero.
 * @param bitboard The bitboard to scan.
 * @return Index of the LSB (0-63), or -1 if the bitboard is empty.
 */
constexpr int getLSBIndex(Bluie::Bitboard bitboard)
{
    return bitboard ? static_cast<int>(std::countr_zero(bitboard)) : -1;
}

/**
 * @brief Reset (pop/clear) the Least Significant set Bit (LSB) in a bitboard.
 * @param bitboard The bitboard reference to modify.
 */
constexpr void popLSB(Bluie::Bitboard& bitboard)
{
    bitboard &= bitboard - 1;
}

} // namespace Bitboards
} // namespace Bluie