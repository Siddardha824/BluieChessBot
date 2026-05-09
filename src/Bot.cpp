
#include "Bitboard.hpp"




// Move Generation Logic

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

