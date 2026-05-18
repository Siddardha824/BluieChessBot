#include "Bitboard.hpp"
#include "Types.hpp"
#include "MagicNumbers.hpp"

Bitboard setOccupancy(int index, int bitsInMask, Bitboard attackMask)
{
    Bitboard occupancy = 0ULL;

    for (int i = 0; i < bitsInMask; ++i)
    {
        int square = getLSBIndex(attackMask);
        clearBit(attackMask, static_cast<Square>(square));
        if (index & (1 << i))
        {
            occupancy |= (1ULL << square);
        }
    }

    return occupancy;
}

