#include "tools/AttacksOnTheFly.hpp"

namespace Bluie
{
namespace Tools
{

Bitboard bishopAttacksOnTheFly(Square square, Bitboard occupancy)
{
    // Resulting bitboard to store the bishop attacks
    Bitboard attacks = 0ULL;

    // Convert the square index to rank and file
    int rank = static_cast<int>(toIndex(square)) / 8;
    int file = static_cast<int>(toIndex(square)) % 8;

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
    for (r = rank + 1, f = file + 1; r <= 7 && f <= 7; ++r, ++f)
    {
        attacks |= (1ULL << (r * 8 + f));
        if (occupancy & (1ULL << (r * 8 + f)))
            break;
    }

    // Direction 2: Down-Right
    for (r = rank - 1, f = file + 1; r >= 0 && f <= 7; --r, ++f)
    {
        attacks |= (1ULL << (r * 8 + f));
        if (occupancy & (1ULL << (r * 8 + f)))
            break;
    }

    // Direction 3: Down-Left
    for (r = rank - 1, f = file - 1; r >= 0 && f >= 0; --r, --f)
    {
        attacks |= (1ULL << (r * 8 + f));
        if (occupancy & (1ULL << (r * 8 + f)))
            break;
    }

    // Direction 4: Up-Left
    for (r = rank + 1, f = file - 1; r <= 7 && f >= 0; ++r, --f)
    {
        attacks |= (1ULL << (r * 8 + f));
        if (occupancy & (1ULL << (r * 8 + f)))
            break;
    }

    return attacks;
}

Bitboard rookAttacksOnTheFly(Square square, Bitboard occupancy)
{
    // Resulting bitboard to store the rook attacks
    Bitboard attacks = 0ULL;

    // Convert the square index to rank and file
    int rank = static_cast<int>(toIndex(square)) / 8;
    int file = static_cast<int>(toIndex(square)) % 8;

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
    for (r = rank + 1, f = file; r <= 7; ++r)
    {
        attacks |= (1ULL << (r * 8 + f));
        if (occupancy & (1ULL << (r * 8 + f)))
            break;
    }

    // Direction 2: Right
    for (r = rank, f = file + 1; f <= 7; ++f)
    {
        attacks |= (1ULL << (r * 8 + f));
        if (occupancy & (1ULL << (r * 8 + f)))
            break;
    }

    // Direction 3: Down
    for (r = rank - 1, f = file; r >= 0; --r)
    {
        attacks |= (1ULL << (r * 8 + f));
        if (occupancy & (1ULL << (r * 8 + f)))
            break;
    }

    // Direction 4: Left
    for (r = rank, f = file - 1; f >= 0; --f)
    {
        attacks |= (1ULL << (r * 8 + f));
        if (occupancy & (1ULL << (r * 8 + f)))
            break;
    }

    return attacks;
}

} // namespace Tools
} // namespace Bluie