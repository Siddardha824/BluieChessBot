#include <iostream>
#include <cstdint>
#include <bitset>

// Define a Bitboard as a 64-bit unsigned integer
typedef uint64_t Bitboard;

// Mask constants for file and rank operations

namespace Masks {
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

    const Bitboard NOT_A_FILE = 0xFEFEFEFEFEFEFEFEULL; // ~A_FILE
    const Bitboard NOT_H_FILE = 0x7F7F7F7F7F7F7F7FULL; // ~H_FILE

    const Bitboard NOT_AB_FILE = 0xFCFCFCFCFCFCFCFCULL; // ~(A_FILE | B_FILE)
    const Bitboard NOT_GH_FILE = 0x3F3F3F3F3F3F3F3FULL; // ~(G_FILE | H_FILE)
}



// --- Core Bit Manipulation Functions ---

// Set a piece on a specific square (0 to 63)
inline void set_bit(Bitboard &b, int square)
{
    b |= (1ULL << square);
}

// Remove a piece from a specific square
inline void clear_bit(Bitboard &b, int square)
{
    b &= ~(1ULL << square);
}

// Check if a square is occupied in this bitboard
inline bool get_bit(Bitboard b, int square)
{
    return (b & (1ULL << square)) != 0;
}

// Move a piece from one square to another using a branchless XOR operation
inline void move_piece(Bitboard &b, int from_square, int to_square)
{
    b ^= ((1ULL << from_square) | (1ULL << to_square));
}

// Print the bitboard in a human-readable format (for debugging)
void print_bitboard(Bitboard b)
{
    for (int rank = 7; rank >= 0; --rank)
    {
        for (int file = 0; file < 8; ++file)
        {
            int square = rank * 8 + file;
            std::cout << (get_bit(b, square) ? "1 " : ". ");
        }
        std::cout << std::endl;
    }
    std::cout << std::endl;
}

// Move Generation Logic

// Simple Move representation (can be packed into a 16-bit int later)
struct Move
{
    int from_square;
    int to_square;

    Move(int from, int to) : from_square(from), to_square(to) {}
};

// A pre-allocated list to hold generated moves (max possible in chess is 218)
struct MoveList
{
    Move moves[218];
    int count = 0;

    void add(Move m)
    {
        moves[count++] = m;
    }
};

// Pawn Pushes for White Pawns
Bitboard generate_white_pawn_pushes(Bitboard white_pawns, Bitboard empty_squares)
{
    // Shift the pawns forward by 1 rank (8 squares) and ensure the destination is empty for single pushes
    Bitboard single_pushes_available = (white_pawns << 8) & empty_squares;
    // For double pushes, ensure the pawns are on the second rank and the squares in front are empty
    Bitboard double_pushes_available = ((white_pawns & Masks::RANK_2) << 16) & empty_squares & (empty_squares << 8);
    return single_pushes_available | double_pushes_available;
}

// Pawn Pushes for Black Pawns
Bitboard generate_black_pawn_pushes(Bitboard black_pawns, Bitboard empty_squares)
{
    // Shift the pawns backward by 1 rank (8 squares) and ensure the destination is empty for single pushes
    Bitboard single_pushes_available = (black_pawns >> 8) & empty_squares;
    Bitboard double_pushes_available = ((black_pawns & Masks::RANK_7) >> 16) & empty_squares & (empty_squares >> 8);
    return single_pushes_available | double_pushes_available;
}

Bitboard generate_white_pawn_captures(Bitboard white_pawns, Bitboard black_pieces)
{
    // Attack to the North-West (Shift by 7). Clear the H-file to prevent A-file wrapping.
    Bitboard left_attacks = (white_pawns << 7) & Masks::NOT_H_FILE;

    // Attack to the North-East (Shift by 9). Clear the A-file to prevent H-file wrapping.
    Bitboard right_attacks = (white_pawns << 9) & Masks::NOT_A_FILE;

    // A capture is only valid if it lands on a square occupied by an enemy piece
    return (left_attacks | right_attacks) & black_pieces;
}

Bitboard generate_black_pawn_captures(Bitboard black_pawns, Bitboard white_pieces)
{
    // Attack to the South-East (Shift by 7)
    Bitboard left_attacks = (black_pawns >> 7) & Masks::NOT_A_FILE;

    // Attack to the South-West (Shift by 9)
    Bitboard right_attacks = (black_pawns >> 9) & Masks::NOT_H_FILE;

    return (left_attacks | right_attacks) & white_pieces;
}

Bitboard generate_white_pawn_moves(Bitboard white_pawns, Bitboard black_pieces, Bitboard empty_squares)
{
    Bitboard pushes = generate_white_pawn_pushes(white_pawns, empty_squares);
    Bitboard captures = generate_white_pawn_captures(white_pawns, black_pieces);
    return pushes | captures;
}

Bitboard generate_black_pawn_moves(Bitboard black_pawns, Bitboard white_pieces, Bitboard empty_squares)
{
    Bitboard pushes = generate_black_pawn_pushes(black_pawns, empty_squares);
    Bitboard captures = generate_black_pawn_captures(black_pawns, white_pieces);
    return pushes | captures;
}

Bitboard precomputed_knight_moves[64];

void precompute_knight_moves()
{
    for (int square = 0; square < 64; ++square)
    {
        Bitboard knight = 1ULL << square;

        Bitboard moves = 0ULL;
        moves |= (knight << 6 ) & Masks::NOT_GH_FILE;
        moves |= (knight << 10) & Masks::NOT_AB_FILE;
        moves |= (knight << 15) & Masks::NOT_H_FILE;
        moves |= (knight << 17) & Masks::NOT_A_FILE;
        moves |= (knight >> 6 ) & Masks::NOT_AB_FILE;
        moves |= (knight >> 10) & Masks::NOT_GH_FILE;
        moves |= (knight >> 15) & Masks::NOT_A_FILE;
        moves |= (knight >> 17) & Masks::NOT_H_FILE;

        precomputed_knight_moves[square] = moves;
    }
}

// Bitboard get_knight_moves(Bitboard knight, Bitboard friendly_pieces)
// {
//     return 
// }

Bitboard precomputed_king_moves[64];

void precompute_king_moves()
{
    for (int square = 0; square < 64; ++square)
    {
        Bitboard king = 1ULL << square;

        Bitboard moves = 0ULL;
        moves |= (king << 9) & Masks::NOT_A_FILE;
        moves |= (king << 8);
        moves |= (king << 7) & Masks::NOT_H_FILE;
        moves |= (king << 1) & Masks::NOT_A_FILE;
        moves |= (king >> 9) & Masks::NOT_H_FILE;
        moves |= (king >> 8);
        moves |= (king >> 7) & Masks::NOT_A_FILE;
        moves |= (king >> 1) & Masks::NOT_H_FILE;

        precomputed_king_moves[square] = moves;
    }
}

int main()
{
    precompute_king_moves();
    for(Bitboard b : precomputed_king_moves)
        print_bitboard(b);

    return 0;
}