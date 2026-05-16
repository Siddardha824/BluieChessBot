#include "PreComputation.hpp"
#include "Bitboard.hpp"
#include "Types.hpp"

Bitboard pawnAttacks[2][64];
Bitboard knightAttacks[64];
Bitboard kingAttacks[64];

void initPrecompute()
{
    // Precompute the pawn attacks Table
    computePawnAttacks();

    // Precompute the knight attacks Table
    computeKnightAttacks();

    // Precompute the king attacks Table
    computeKingAttacks();
}

void computePawnAttacks()
{
    // Iterate through all the squares
    for (int square = 0; square < 64; square++)
    {
        // Create a empty board and place the pawn at the square
        Bitboard piece = 0ULL;
        setBit(piece, square);

        Bitboard attacks = 0ULL;
        // Calculate the pawn attacks if the pawn is white.
        // File masks are used to prevent wrap around at the edge of the board
        attacks |= (piece >> 7) & Masks::NOT_A_FILE;
        attacks |= (piece >> 9) & Masks::NOT_H_FILE;
        // Store it in an array for faster access during move generation
        pawnAttacks[Side::white][square] = attacks;

        attacks = 0ULL;
        // Calculate the pawn attacks if the pawn is black.
        attacks |= (piece << 7) & Masks::NOT_H_FILE;
        attacks |= (piece << 9) & Masks::NOT_A_FILE;

        pawnAttacks[Side::black][square] = attacks;
    }
}

void computeKnightAttacks()
{
    // Iterate through all the squares
    for (int square = 0; square < 64; square++)
    {
        // Create a empty board and place the pawn at the square
        Bitboard piece = 0ULL;
        setBit(piece, square);

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

        knightAttacks[square] = attacks;
    }
}

void computeKingAttacks()
{
    // Iterate through all the squares
    for (int square = 0; square < 64; square++)
    {
        // Create a empty board and place the pawn at the square
        Bitboard piece = 0ULL;
        setBit(piece, square);

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

        kingAttacks[square] = attacks;
    }
}