#include "Attacks.hpp"
#include "AttackTables.hpp"
#include "Debug.hpp"
#include "MagicNumbers.hpp"
#include "PreComputation.hpp"
#include "Types.hpp"

#include <fstream>
#include <iomanip>
#include <iostream>

void testMagicAttacks()
{
    for (int square = 0; square < 64; ++square)
    {
        Square sq = static_cast<Square>(square);

        // =========================
        // ROOK TEST
        // =========================

        Bitboard rookOccupancyMask = rookOccupancyMasks[square];

        int rookOccupancyIndices = 1 << rookRelevantBits[square];

        for (int index = 0; index < rookOccupancyIndices; ++index)
        {
            Bitboard occupancy = setOccupancy(index, rookRelevantBits[square], rookOccupancyMask);

            Bitboard expected = rookAttacksOnTheFly(sq, occupancy);

            std::size_t magicIndex = getRookMagicIndex(sq, occupancy);

            Bitboard actual = rookAttacks[square][magicIndex];

            if (expected != actual)
            {
                std::cout << "Rook attack mismatch!\n";
                std::cout << "Square: " << square << '\n';
                std::cout << "Index : " << index << '\n';

                std::cout << "\nExpected:\n";
                printBitboard(expected);

                std::cout << "\nActual:\n";
                printBitboard(actual);

                return;
            }
        }

        // =========================
        // BISHOP TEST
        // =========================

        Bitboard bishopOccupancyMask = bishopOccupancyMasks[square];

        int bishopOccupancyIndices = 1 << bishopRelevantBits[square];

        for (int index = 0; index < bishopOccupancyIndices; ++index)
        {
            Bitboard occupancy =
                setOccupancy(index, bishopRelevantBits[square], bishopOccupancyMask);

            Bitboard expected = bishopAttacksOnTheFly(sq, occupancy);

            std::size_t magicIndex = getBishopMagicIndex(sq, occupancy);

            Bitboard actual = bishopAttacks[square][magicIndex];

            if (expected != actual)
            {
                std::cout << "Bishop attack mismatch!\n";
                std::cout << "Square: " << square << '\n';
                std::cout << "Index : " << index << '\n';

                std::cout << "\nExpected:\n";
                printBitboard(expected);

                std::cout << "\nActual:\n";
                printBitboard(actual);

                return;
            }
        }
    }

    std::cout << "Magic attack tables are correct!\n";
}

void writeRookAttackTablesToFile()
{
    std::ofstream file("RookAttackTables.txt");

    if (!file)
    {
        return;
    }

    file << "inline constexpr std::array<std::array<Bitboard, 4096>, 64> rookAttacks = {\n";
    file << "{\n";

    for (int square = 0; square < 64; ++square)
    {
        file << "{\n";

        int occupancyIndices = 1 << rookRelevantBits[square];

        for (int index = 0; index < occupancyIndices; ++index)
        {
            Bitboard occupancy =
                setOccupancy(index, rookRelevantBits[square], rookOccupancyMasks[square]);

            std::size_t magicIndex = getRookMagicIndex(static_cast<Square>(square), occupancy);

            Bitboard attacks = rookAttacksOnTheFly(static_cast<Square>(square), occupancy);

            file << "0x" << std::hex << std::setw(16) << std::setfill('0') << attacks << "ULL,";

            if ((index + 1) % 4 == 0)
            {
                file << '\n';
            }
        }

        file << "},\n";
    }

    file << "}};\n";

    file.close();
}

void writeBishopAttackTablesToFile()
{
    std::ofstream file("BishopAttackTables.txt");

    if (!file)
    {
        return;
    }

    file << "inline constexpr std::array<std::array<Bitboard, 512>, 64> bishopAttacks = {\n";
    file << "{\n";

    for (int square = 0; square < 64; ++square)
    {
        file << "{\n";

        int occupancyIndices = 1 << bishopRelevantBits[square];

        for (int index = 0; index < occupancyIndices; ++index)
        {
            Bitboard occupancy =
                setOccupancy(index, bishopRelevantBits[square], bishopOccupancyMasks[square]);

            std::size_t magicIndex = getBishopMagicIndex(static_cast<Square>(square), occupancy);

            Bitboard attacks = bishopAttacksOnTheFly(static_cast<Square>(square), occupancy);

            file << "0x" << std::hex << std::setw(16) << std::setfill('0') << attacks << "ULL,";

            if ((index + 1) % 4 == 0)
            {
                file << '\n';
            }
        }

        file << "},\n";
    }

    file << "}};\n";

    file.close();
}
