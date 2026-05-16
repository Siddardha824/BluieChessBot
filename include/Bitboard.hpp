#pragma once

#include "Types.hpp"

// Mask constants for file and rank operations
namespace Masks
{
const Bitboard NOT_A_FILE = 0xFEFEFEFEFEFEFEFEULL; // ~A_FILE
const Bitboard NOT_H_FILE = 0x7F7F7F7F7F7F7F7FULL; // ~H_FILE

const Bitboard NOT_AB_FILE = 0xFCFCFCFCFCFCFCFCULL; // ~(A_FILE | B_FILE)
const Bitboard NOT_GH_FILE = 0x3F3F3F3F3F3F3F3FULL; // ~(G_FILE | H_FILE)

} // namespace Masks

/*-----------------------------------------------*\
           Slider pieces Attacks
\*-----------------------------------------------*/

// Set a piece on a specific square (0 to 63)
constexpr void setBit(Bitboard& b, int square)
{
    b |= (1ULL << square);
}

// Remove a piece from a specific square
constexpr void clearBit(Bitboard& b, int square)
{
    b &= ~(1ULL << square);
}

// Check if a square is occupied in this bitboard
constexpr bool getBit(Bitboard b, int square)
{
    return (b & (1ULL << square)) != 0;
}

// Move a piece from one square to another using a branchless XOR operation
constexpr void movePiece(Bitboard& b, Square from_square, Square to_square)
{
    b ^= ((1ULL << from_square) | (1ULL << to_square));
}

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