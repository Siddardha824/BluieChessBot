#pragma once

#include "core/Types.hpp"

/**
 * @brief Mask constants for board file and rank boundary operations.
 */
namespace Masks
{
inline constexpr Bitboard NOT_A_FILE = 0xFEFEFEFEFEFEFEFEULL; ///< Everything except the A-file
inline constexpr Bitboard NOT_H_FILE = 0x7F7F7F7F7F7F7F7FULL; ///< Everything except the H-file

inline constexpr Bitboard NOT_AB_FILE = 0xFCFCFCFCFCFCFCFCULL; ///< Everything except A and B files
inline constexpr Bitboard NOT_GH_FILE = 0x3F3F3F3F3F3F3F3FULL; ///< Everything except G and H files

} // namespace Masks

/*-----------------------------------------------*\
    Bit manipulation functions for bitboards
\*-----------------------------------------------*/

/**
 * @brief Get a bitboard with only the bit at the specified square set to 1.
 * @param square The square index (0-63).
 * @return Bitboard with a single set bit.
 */
constexpr Bitboard squareToBitboard(Square square)
{
    return 1ULL << square;
}

/**
 * @brief Set the bit of a specific square to 1.
 * @param b The bitboard reference to modify.
 * @param square The square index (0-63).
 */
constexpr void setBit(Bitboard& b, Square square)
{
    b |= (1ULL << square);
}

/**
 * @brief Clear the bit of a specific square (set to 0).
 * @param b The bitboard reference to modify.
 * @param square The square index (0-63).
 */
constexpr void clearBit(Bitboard& b, Square square)
{
    b &= ~(1ULL << square);
}

/**
 * @brief Check if a specific square bit is set (occupied).
 * @param b The bitboard to check.
 * @param square The square index (0-63).
 * @return True if the square is occupied, false otherwise.
 */
constexpr bool getBit(Bitboard b, Square square)
{
    return (b & (1ULL << square)) != 0;
}

/**
 * @brief Move a piece from one square to another using a branchless XOR.
 * @param b The bitboard reference to modify.
 * @param fromSquare The square the piece is leaving.
 * @param toSquare The square the piece is entering.
 */
constexpr void movePiece(Bitboard& b, Square fromSquare, Square toSquare)
{
    b ^= ((1ULL << fromSquare) | (1ULL << toSquare));
}

/**
 * @brief Count the number of active bits (set to 1) using Brian Kernighan's algorithm.
 * @param bitboard The bitboard to count.
 * @return Count of active bits.
 */
constexpr int countBits(Bitboard bitboard)
{
    int count = 0;
    while (bitboard)
    {
        count++;
        bitboard &= bitboard - 1; // Resets the least significant set bit
    }
    return count;
}

/**
 * @brief Get the square index of the Least Significant set Bit (LSB).
 * @param bitboard The bitboard to scan.
 * @return Index of the LSB (0-63), or -1 if the bitboard is empty.
 */
constexpr int getLSBIndex(Bitboard bitboard)
{
    if (bitboard)
    {
        return countBits((bitboard & -bitboard) - 1);
    }
    else
    {
        return -1;
    }
}

/**
 * @brief Reset (pop/clear) the Least Significant set Bit (LSB) in a bitboard.
 * @param bitboard The bitboard reference to modify.
 */
constexpr void popLSB(Bitboard& bitboard)
{
    bitboard &= bitboard - 1;
}