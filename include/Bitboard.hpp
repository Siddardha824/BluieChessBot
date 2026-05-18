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
constexpr void set_bit(Bitboard& b, Square square)
{
    b |= (1ULL << square);
}

// Remove a piece from a specific square
constexpr void clear_bit(Bitboard& b, Square square)
{
    b &= ~(1ULL << square);
}

// Check if a square is occupied in this bitboard
constexpr bool get_bit(Bitboard b, Square square)
{
    return (b & (1ULL << square)) != 0;
}

// Move a piece from one square to another using a branchless XOR operation
constexpr void move_piece(Bitboard& b, Square from_square, Square to_square)
{
    b ^= ((1ULL << from_square) | (1ULL << to_square));
}

constexpr int count_bits(Bitboard bitboard)
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

constexpr int get_LSB_index(Bitboard bitboard)
{
    if (bitboard)
    {
        return count_bits((bitboard & -bitboard) - 1);
    }
    else
    {
        return -1;
    }
}