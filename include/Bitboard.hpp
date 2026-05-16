#pragma once

#include "Types.hpp"

// Mask constants for file and rank operations
namespace Masks
{
constexpr Bitboard FILE_MASK[8] = {
    0x0101010101010101ULL, // File A (Index 0)
    0x0202020202020202ULL, // File B (Index 1)
    0x0404040404040404ULL, // File C (Index 2)
    0x0808080808080808ULL, // File D (Index 3)
    0x1010101010101010ULL, // File E (Index 4)
    0x2020202020202020ULL, // File F (Index 5)
    0x4040404040404040ULL, // File G (Index 6)
    0x8080808080808080ULL  // File H (Index 7)
};

constexpr Bitboard RANK_MASK[8] = {
    0x00000000000000FFULL, // Rank 1 (Index 0)
    0x000000000000FF00ULL, // Rank 2 (Index 1)
    0x0000000000FF0000ULL, // Rank 3 (Index 2)
    0x00000000FF000000ULL, // Rank 4 (Index 3)
    0x000000FF00000000ULL, // Rank 5 (Index 4)
    0x0000FF0000000000ULL, // Rank 6 (Index 5)
    0x00FF000000000000ULL, // Rank 7 (Index 6)
    0xFF00000000000000ULL  // Rank 8 (Index 7)
};

const Bitboard NOT_A_FILE = 0xFEFEFEFEFEFEFEFEULL; // ~A_FILE
const Bitboard NOT_H_FILE = 0x7F7F7F7F7F7F7F7FULL; // ~H_FILE

const Bitboard NOT_AB_FILE = 0xFCFCFCFCFCFCFCFCULL; // ~(A_FILE | B_FILE)
const Bitboard NOT_GH_FILE = 0x3F3F3F3F3F3F3F3FULL; // ~(G_FILE | H_FILE)

// const Bitboard A_FILE = 0x0101010101010101ULL;
// const Bitboard B_FILE = 0x0202020202020202ULL;
// const Bitboard C_FILE = 0x0404040404040404ULL;
// const Bitboard D_FILE = 0x0808080808080808ULL;
// const Bitboard E_FILE = 0x1010101010101010ULL;
// const Bitboard F_FILE = 0x2020202020202020ULL;
// const Bitboard G_FILE = 0x4040404040404040ULL;
// const Bitboard H_FILE = 0x8080808080808080ULL;

// const Bitboard RANK_1 = 0x00000000000000FFULL;
const Bitboard RANK_2 = 0x000000000000FF00ULL;
// const Bitboard RANK_3 = 0x0000000000FF0000ULL;
// const Bitboard RANK_4 = 0x00000000FF000000ULL;
// const Bitboard RANK_5 = 0x000000FF00000000ULL;
// const Bitboard RANK_6 = 0x0000FF0000000000ULL;
const Bitboard RANK_7 = 0x00FF000000000000ULL;
// const Bitboard RANK_8 = 0xFF00000000000000ULL;

} // namespace Masks

// --- Core Bit Manipulation Functions ---

// Set a piece on a specific square (0 to 63)
inline void setBit(Bitboard& b, int square)
{
    b |= (1ULL << square);
}

// Remove a piece from a specific square
inline void clearBit(Bitboard& b, int square)
{
    b &= ~(1ULL << square);
}

// Check if a square is occupied in this bitboard
inline bool getBit(Bitboard b, int square)
{
    return (b & (1ULL << square)) != 0;
}

// Move a piece from one square to another using a branchless XOR operation
inline void movePiece(Bitboard& b, int from_square, int to_square)
{
    b ^= ((1ULL << from_square) | (1ULL << to_square));
}