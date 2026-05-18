#include "Bitboard.hpp"
#include "Types.hpp"
#include <array>

/*-----------------------------------------------*\
           Leaper pieces Attack Tables
\*-----------------------------------------------*/

constexpr Bitboard generate_pawn_attack(Side side, Square square)
{
    // Create a empty board and place the pawn at the square
    Bitboard piece = 0ULL;
    set_bit(piece, square);

    Bitboard attacks = 0ULL;
    if (side == Side::white)
    {
        // Calculate the pawn attacks if the pawn is white.
        // File masks are used to prevent wrap around at the edge of the board
        attacks |= (piece >> 7) & Masks::NOT_A_FILE;
        attacks |= (piece >> 9) & Masks::NOT_H_FILE;
    }
    else
    {
        // Calculate the pawn attacks if the pawn is black.
        attacks |= (piece << 7) & Masks::NOT_H_FILE;
        attacks |= (piece << 9) & Masks::NOT_A_FILE;
    }
    return attacks;
}

constexpr Bitboard generate_knight_attack(Square square)
{
    // Create a empty board and place the pawn at the square
    Bitboard piece = 0ULL;
    set_bit(piece, square);

    Bitboard attacks = 0ULL;

    // Calculate the knight attacks in 8 directions
    /*
        8  . . . . . . . .
        7  . . 2 . 3 . . .
        6  . 1 . . . 4 . .
        5  . . . N . . . .
        4  . 8 . . . 5 . .
        3  . . 7 . 6 . . .
        2  . . . . . . . .
        1  . . . . . . . .
           a b c d e f g h
    */

    attacks |= (piece >> 10) & Masks::NOT_GH_FILE; // Direction 1
    attacks |= (piece >> 17) & Masks::NOT_H_FILE;  // Direction 2
    attacks |= (piece >> 15) & Masks::NOT_A_FILE;  // Direction 3
    attacks |= (piece >> 6) & Masks::NOT_AB_FILE;  // Direction 4
    attacks |= (piece << 10) & Masks::NOT_AB_FILE; // Direction 5
    attacks |= (piece << 17) & Masks::NOT_A_FILE;  // Direction 6
    attacks |= (piece << 15) & Masks::NOT_H_FILE;  // Direction 7
    attacks |= (piece << 6) & Masks::NOT_GH_FILE;  // Direction 8

    return attacks;
}

constexpr Bitboard generate_king_attack(Square square)
{
    // Create a empty board and place the pawn at the square
    Bitboard piece = 0ULL;
    set_bit(piece, square);

    Bitboard attacks = 0ULL;

    // Calculate the king attacks in 8 directions
    /*
        8  . . . . . . . .
        7  . . . . . . . .
        6  . . 1 2 3 . . .
        5  . . 8 K 4 . . .
        4  . . 7 6 5 . . .
        3  . . . . . . . .
        2  . . . . . . . .
        1  . . . . . . . .
           a b c d e f g h
    */

    attacks |= (piece >> 9) & Masks::NOT_H_FILE; // Direction 1
    attacks |= (piece >> 8);                     // Direction 2
    attacks |= (piece >> 7) & Masks::NOT_A_FILE; // Direction 3
    attacks |= (piece << 1) & Masks::NOT_A_FILE; // Direction 4
    attacks |= (piece << 9) & Masks::NOT_A_FILE; // Direction 5
    attacks |= (piece << 8);                     // Direction 6
    attacks |= (piece << 7) & Masks::NOT_H_FILE; // Direction 7
    attacks |= (piece >> 1) & Masks::NOT_H_FILE; // Direction 8

    return attacks;
}

constexpr auto generate_pawn_attacks()
{
    std::array<std::array<Bitboard, 64>, 2> table{};
    // Iterate for both sides
    for (int side = 0; side < 2; ++side)
    {
        // Iterate through all the squares
        for (int square = 0; square < 64; square++)
        {
            table[side][square] =
                generate_pawn_attack(static_cast<Side>(side), static_cast<Square>(square));
        }
    }
    return table;
}


constexpr auto generate_knight_attacks()
{
    std::array<Bitboard, 64> table = {};
    
    // Iterate through all the squares
    for (int square = 0; square < 64; square++)
    {
        table[square] = generate_knight_attack(static_cast<Square>(square));
    }
    return table;
}


constexpr auto generate_king_attacks()
{
    std::array<Bitboard, 64> table = {};
    
    // Iterate through all the squares
    for (int square = 0; square < 64; square++)
    {
        table[square] = generate_king_attack(static_cast<Square>(square));
    }
    return table;
}

inline constexpr auto pawn_attacks = generate_pawn_attacks();
inline constexpr auto knight_attacks = generate_knight_attacks();
inline constexpr auto king_attacks = generate_king_attacks();
