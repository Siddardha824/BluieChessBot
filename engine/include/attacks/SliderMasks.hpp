#pragma once

#include "core/Bitboard.hpp"
#include "core/Types.hpp"
#include <array>

namespace Bluie
{
namespace Attacks
{

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
    for (r = rank + 1, f = file + 1; r <= 6 && f <= 6; ++r, ++f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 2: Down-Right
    for (r = rank - 1, f = file + 1; r >= 1 && f <= 6; --r, ++f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 3: Down-Left
    for (r = rank - 1, f = file - 1; r >= 1 && f >= 1; --r, --f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 4: Up-Left
    for (r = rank + 1, f = file - 1; r <= 6 && f >= 1; ++r, --f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    return attacks;
}

constexpr Bitboard maskRookAttacks(Square square)
{
    // Resulting bitboard to store the rook attacks
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
    for (r = rank + 1, f = file; r <= 6; ++r)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 2: Right
    for (r = rank, f = file + 1; f <= 6; ++f)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 3: Down
    for (r = rank - 1, f = file; r >= 1; --r)
    {
        attacks |= (1ULL << (r * 8 + f));
    }

    // Direction 4: Left
    for (r = rank, f = file - 1; f >= 1; --f)
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

} // namespace Attacks
} // namespace Bluie
