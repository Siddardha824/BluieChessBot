#include "Bitboard.hpp"
#include "Types.hpp"
#include "MagicNumbers.hpp"

Bitboard set_occupancy(int index, int bits_in_mask, Bitboard attack_mask)
{
    Bitboard occupancy = 0ULL;

    for (int i = 0; i < bits_in_mask; ++i)
    {
        int square = get_LSB_index(attack_mask);
        clear_bit(attack_mask, static_cast<Square>(square));
        if (index & (1 << i))
        {
            occupancy |= (1ULL << square);
        }
    }

    return occupancy;
}

