#include "tools/Tests.hpp"
#include "attacks/Attacks.hpp"
#include "attacks/AttackTables.hpp"
#include "core/Debug.hpp"
#include "attacks/MagicNumbers.hpp"
#include "tools/MagicGenerator.hpp"
#include "tools/AttacksOnTheFly.hpp"
#include "core/Types.hpp"

#include <fstream>
#include <iomanip>
#include <iostream>

namespace Bluie
{
namespace Tools
{

void testMagicAttacks()
{
    for (int square = 0; square < 64; ++square)
    {
        Square sq = static_cast<Square>(square);

        // =========================
        // ROOK TEST
        // =========================

        Bitboard rookOccupancyMask = Attacks::rookOccupancyMasks[square];

        int rookOccupancyIndices = 1 << Attacks::rookRelevantBits[square];

        for (int index = 0; index < rookOccupancyIndices; ++index)
        {
            Bitboard occupancy = setOccupancy(index, Attacks::rookRelevantBits[square], rookOccupancyMask);

            Bitboard expected = rookAttacksOnTheFly(sq, occupancy);

            std::size_t magicIndex = Attacks::getRookMagicIndex(sq, occupancy);

            Bitboard actual = Attacks::rookAttacks[square][magicIndex];

            if (expected != actual)
            {
                std::cout << "Rook attack mismatch!\n";
                std::cout << "Square: " << square << '\n';
                std::cout << "Index : " << index << '\n';

                std::cout << "\nExpected:\n";
                Debug::printBitboard(expected);

                std::cout << "\nActual:\n";
                Debug::printBitboard(actual);

                return;
            }
        }

        // =========================
        // BISHOP TEST
        // =========================

        Bitboard bishopOccupancyMask = Attacks::bishopOccupancyMasks[square];

        int bishopOccupancyIndices = 1 << Attacks::bishopRelevantBits[square];

        for (int index = 0; index < bishopOccupancyIndices; ++index)
        {
            Bitboard occupancy =
                setOccupancy(index, Attacks::bishopRelevantBits[square], bishopOccupancyMask);

            Bitboard expected = bishopAttacksOnTheFly(sq, occupancy);

            std::size_t magicIndex = Attacks::getBishopMagicIndex(sq, occupancy);

            Bitboard actual = Attacks::bishopAttacks[square][magicIndex];

            if (expected != actual)
            {
                std::cout << "Bishop attack mismatch!\n";
                std::cout << "Square: " << square << '\n';
                std::cout << "Index : " << index << '\n';

                std::cout << "\nExpected:\n";
                Debug::printBitboard(expected);

                std::cout << "\nActual:\n";
                Debug::printBitboard(actual);

                return;
            }
        }
    }

    std::cout << "Magic attack tables are correct!\n";
}

void writeAttackTablesHeaderFile()
{
    std::ofstream file("engine/include/attacks/AttackTables.hpp");
    if (!file)
    {
        std::cout << "Failed to open AttackTables.hpp for writing!\n";
        return;
    }

    file << "#pragma once\n\n";
    file << "#include \"core/Types.hpp\"\n\n";
    file << "namespace Bluie\n{\nnamespace Attacks\n{\n\n";

    // Bishop Attacks
    file << "inline constexpr std::array<std::array<Bitboard, 512>, 64> bishopAttacks = {{\n";
    for (int square = 0; square < 64; ++square)
    {
        file << "    {\n";
        int occupancyIndices = 1 << Attacks::bishopRelevantBits[square];
        std::array<Bitboard, 512> table{};

        for (int index = 0; index < occupancyIndices; ++index)
        {
            Bitboard occupancy =
                setOccupancy(index, Attacks::bishopRelevantBits[square], Attacks::bishopOccupancyMasks[square]);
            std::size_t magicIndex = Attacks::getBishopMagicIndex(static_cast<Square>(square), occupancy);
            Bitboard attacks = bishopAttacksOnTheFly(static_cast<Square>(square), occupancy);
            table[magicIndex] = attacks;
        }

        for (int index = 0; index < occupancyIndices; ++index)
        {
            file << "        0x" << std::hex << std::setw(16) << std::setfill('0') << table[index] << "ULL,";
            if ((index + 1) % 4 == 0)
                file << '\n';
        }
        file << "    },\n";
    }
    file << "}};\n\n";

    // Rook Attacks
    file << "inline constexpr std::array<std::array<Bitboard, 4096>, 64> rookAttacks = {{\n";
    for (int square = 0; square < 64; ++square)
    {
        file << "    {\n";
        int occupancyIndices = 1 << Attacks::rookRelevantBits[square];
        std::array<Bitboard, 4096> table{};

        for (int index = 0; index < occupancyIndices; ++index)
        {
            Bitboard occupancy =
                setOccupancy(index, Attacks::rookRelevantBits[square], Attacks::rookOccupancyMasks[square]);
            std::size_t magicIndex = Attacks::getRookMagicIndex(static_cast<Square>(square), occupancy);
            Bitboard attacks = rookAttacksOnTheFly(static_cast<Square>(square), occupancy);
            table[magicIndex] = attacks;
        }

        for (int index = 0; index < occupancyIndices; ++index)
        {
            file << "        0x" << std::hex << std::setw(16) << std::setfill('0') << table[index] << "ULL,";
            if ((index + 1) % 4 == 0)
                file << '\n';
        }
        file << "    },\n";
    }
    file << "}};\n\n";

    file << "} // namespace Attacks\n} // namespace Bluie\n";
    file.close();
    std::cout << "Successfully regenerated AttackTables.hpp!\n";
}

} // namespace Tools
} // namespace Bluie
