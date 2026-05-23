#include "tools/MagicGenerator.hpp"
#include "attacks/MagicNumbers.hpp"
#include "attacks/SliderMasks.hpp"
#include "tools/AttacksOnTheFly.hpp"
#include "core/Bitboard.hpp"
#include "core/Types.hpp"
#include "tools/Random.hpp"
#include <cstddef>
#include <array>
#include <iostream>

namespace Bluie
{
namespace Tools
{

Bitboard setOccupancy(int index, int bitsInMask, Bitboard attackMask)
{
    Bitboard occupancy = 0ULL;

    for (int i = 0; i < bitsInMask; ++i)
    {
        int square = Bitboards::getLSBIndex(attackMask);
        Bitboards::clearBit(attackMask, static_cast<Square>(square));
        if (index & (1 << i))
        {
            occupancy |= (1ULL << square);
        }
    }

    return occupancy;
}

Bitboard findMagicNumber(Square square, int relevantBits, bool bishop)
{
    std::array<Bitboard, MAX_OCCUPANCIES> occupancies{};
    std::array<Bitboard, MAX_OCCUPANCIES> attacks{};
    std::array<Bitboard, MAX_OCCUPANCIES> usedAttacks{};

    // init attack mask for a current piece
    Bitboard attackMask = bishop ? Attacks::bishopOccupancyMasks[square] : Attacks::rookOccupancyMasks[square];

    // init occupancy indices
    int occupancyIndices = 1 << relevantBits;

    // loop over occupancy indices
    for (std::size_t index = 0; index < occupancyIndices; index++)
    {
        // init occupancies
        occupancies[index] = setOccupancy(index, relevantBits, attackMask);

        // init attacks
        attacks[index] = bishop ? bishopAttacksOnTheFly(square, occupancies[index])
                                : rookAttacksOnTheFly(square, occupancies[index]);
    }

    // test magic numbers loop
    for (int randomCount = 0; randomCount < MAGIC_TRIES; randomCount++)
    {
        // generate magic number candidate
        Bitboard magicNumber = generateMagicNumber();

        // skip inappropriate magic numbers
        if (Bitboards::countBits((attackMask * magicNumber) & 0xFF00000000000000) < 6)
            continue;

        // init used attacks
        usedAttacks.fill(0ULL);

        // init index & fail flag
        std::size_t index;
        bool fail;

        // test magic index loop
        for (index = 0, fail = false; !fail && index < occupancyIndices; index++)
        {
            // init magic index
            int magicIndex =
                static_cast<int>((occupancies[index] * magicNumber) >> (64 - relevantBits));

            // if magic index works
            if (usedAttacks[magicIndex] == 0ULL)
                // init used attacks
                usedAttacks[magicIndex] = attacks[index];

            // otherwise
            else if (usedAttacks[magicIndex] != attacks[index])
                // magic index doesn't work
                fail = true;
        }

        // if magic number works
        if (!fail)
        {
            // return it
            return magicNumber;
        }
    }

    // if magic number doesn't work
    std::cout << "  Magic number fails!" << std::endl;
    return 0ULL;
}

} // namespace Tools
} // namespace Bluie
