#pragma once

#include "Types.hpp"

// Mask constants for file and rank operations
namespace Masks
{
inline constexpr Bitboard NOT_A_FILE = 0xFEFEFEFEFEFEFEFEULL; // ~A_FILE
inline constexpr Bitboard NOT_H_FILE = 0x7F7F7F7F7F7F7F7FULL; // ~H_FILE

inline constexpr Bitboard NOT_AB_FILE = 0xFCFCFCFCFCFCFCFCULL; // ~(A_FILE | B_FILE)
inline constexpr Bitboard NOT_GH_FILE = 0x3F3F3F3F3F3F3F3FULL; // ~(G_FILE | H_FILE)

} // namespace Masks

/*-----------------------------------------------*\
    Bit manipulation functions for bitboards
\*-----------------------------------------------*/

// Return a Bitboard with the bit at the given square set to 1
constexpr Bitboard squareToBitboard(Square square)
{
    return 1ULL << square;
}

// Set a piece on a specific square (0 to 63)
constexpr void setBit(Bitboard& b, Square square)
{
    b |= (1ULL << square);
}

// Remove a piece from a specific square
constexpr void clearBit(Bitboard& b, Square square)
{
    b &= ~(1ULL << square);
}

// Check if a square is occupied in this bitboard
constexpr bool getBit(Bitboard b, Square square)
{
    return (b & (1ULL << square)) != 0;
}

// Move a piece from one square to another using a branchless XOR operation
constexpr void movePiece(Bitboard& b, Square fromSquare, Square toSquare)
{
    b ^= ((1ULL << fromSquare) | (1ULL << toSquare));
}

// Count the number of set bits in a bitboard using Brian Kernighan's algorithm
constexpr int countBits(Bitboard bitboard)
{
    // Counter for bits
    int count = 0;

    while (bitboard)
    {
        // Increment counter
        count++;

        // Reset the LSB
        bitboard &= bitboard - 1;
    }

    return count;
}

// Get the index of the least significant bit (LSB) in a bitboard, or -1 if the bitboard is empty
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

// Reset the least significant bit (LSB) in a bitboard
constexpr void popLSB(Bitboard& bitboard)
{
    bitboard &= bitboard - 1;
}