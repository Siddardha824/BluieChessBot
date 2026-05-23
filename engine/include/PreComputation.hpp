#pragma once

#include "AttackTables.hpp"
#include "Bitboard.hpp"
#include "MagicNumbers.hpp"
#include "Types.hpp"
#include <array>
#include <cstddef>

/*-----------------------------------------------*\
           Leaper pieces Attack Tables
\*-----------------------------------------------*/

constexpr Bitboard generatePawnAttack(Side side, Square square)
{
    // Create a empty board and place the pawn at the square
    Bitboard piece = 0ULL;
    setBit(piece, square);

    Bitboard attacks = 0ULL;
    if (side == Side::WHITE)
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

constexpr Bitboard generateKnightAttack(Square square)
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

    return attacks;
}

constexpr Bitboard generateKingAttack(Square square)
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

    return attacks;
}

constexpr auto generatePawnAttacks()
{
    std::array<BitboardArray, 2> table{};
    // Iterate for both sides
    for (int side = 0; side < 2; ++side)
    {
        // Iterate through all the squares
        for (int square = 0; square < 64; square++)
        {
            table[side][square] =
                generatePawnAttack(static_cast<Side>(side), static_cast<Square>(square));
        }
    }
    return table;
}

constexpr auto generateKnightAttacks()
{
    BitboardArray table = {};

    // Iterate through all the squares
    for (int square = 0; square < 64; square++)
    {
        table[square] = generateKnightAttack(static_cast<Square>(square));
    }
    return table;
}

constexpr auto generateKingAttacks()
{
    BitboardArray table = {};

    // Iterate through all the squares
    for (int square = 0; square < 64; square++)
    {
        table[square] = generateKingAttack(static_cast<Square>(square));
    }
    return table;
}

inline constexpr auto pawnAttacks = generatePawnAttacks();
inline constexpr auto knightAttacks = generateKnightAttacks();
inline constexpr auto kingAttacks = generateKingAttacks();

/*-----------------------------------------------*\
           Slider pieces Attack Tables
\*-----------------------------------------------*/

constexpr Bitboard maskBishopAttacks(Square square)
{
    // Resulting bitboard to store the bishop attacks
    Bitboard attacks = 0ULL;

    // Convert the square index to rank and file
    int rank = square / 8;
    int file = square % 8;

    // Calculate the bishop attacks in 4 diagonal directions
    /*
        8  . . . . . . . .
        7  . 4 . . . 1 . .
        6  . . 4 . 1 . . .
        5  . . . B . . . .
        4  . . 3 . 2 . . .
        3  . 3 . . . 2 . .
        2  . . . . . . 2 .
        1  . . . . . . . .
           a b c d e f g h
    */
    int r, f;
    // Direction 1: Up-Right
    for (int r = rank + 1, f = file + 1; r <= 6 && f <= 6; ++r, ++f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 2: Down-Right
    for (int r = rank - 1, f = file + 1; r >= 1 && f <= 6; --r, ++f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 3: Down-Left
    for (int r = rank - 1, f = file - 1; r >= 1 && f >= 1; --r, --f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 4: Up-Left
    for (int r = rank + 1, f = file - 1; r <= 6 && f >= 1; ++r, --f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    return attacks;
}

constexpr Bitboard maskRookAttacks(Square square)
{
    // Resulting bitboard to store the bishop attacks
    Bitboard attacks = 0ULL;

    // Convert the square index to rank and file
    int rank = square / 8;
    int file = square % 8;

    // Calculate the rook attacks in 4 directions
    /*
        8  . . . . . . . .
        7  . . . 1 . . . .
        6  . . . 1 . . . .
        5  . . . 1 . . . .
        4  . 4 4 R 2 2 2 .
        3  . . . 3 . . . .
        2  . . . 3 . . . .
        1  . . . . . . . .
           a b c d e f g h
    */
    int r, f;
    // Direction 1: Up
    for (int r = rank + 1, f = file; r <= 6; ++r)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 2: Right
    for (int r = rank, f = file + 1; f <= 6; ++f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 3: Down
    for (int r = rank - 1, f = file; r >= 1; --r)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 4: Left
    for (int r = rank, f = file - 1; f >= 1; --f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    return attacks;
}

constexpr auto generateBishopOccupancyMaskTables()
{
    BitboardArray table = {};

    // Iterate through all the squares
    for (int square = 0; square < 64; square++)
    {
        table[square] = maskBishopAttacks(static_cast<Square>(square));
    }
    return table;
}

constexpr auto generateRookOccupancyMaskTables()
{
    BitboardArray table = {};

    // Iterate through all the squares
    for (int square = 0; square < 64; square++)
    {
        table[square] = maskRookAttacks(static_cast<Square>(square));
    }
    return table;
}

inline constexpr BitboardArray bishopOccupancyMasks = generateBishopOccupancyMaskTables();
inline constexpr BitboardArray rookOccupancyMasks = generateRookOccupancyMaskTables();

constexpr std::size_t getBishopMagicIndex(Square square, Bitboard occupancy)
{
    occupancy &= bishopOccupancyMasks[square];

    return (occupancy * bishopMagicNumbers[square]) >> (64 - bishopRelevantBits[square]);
}

constexpr std::size_t getRookMagicIndex(Square square, Bitboard occupancy)
{
    occupancy &= rookOccupancyMasks[square];

    return (occupancy * rookMagicNumbers[square]) >> (64 - rookRelevantBits[square]);
}

constexpr Bitboard getQueneAttack(Square square, Bitboard occupancy)
{
    return bishopAttacks[square][getBishopMagicIndex(square, occupancy)] |
           rookAttacks[square][getRookMagicIndex(square, occupancy)];
}