#include "tools/Tests.hpp"
#include "attacks/AttackTables.hpp"
#include "attacks/Attacks.hpp" // IWYU pragma: keep
#include "attacks/AttacksAPI.hpp"
#include "board/Board.hpp"
#include "core/Debug.hpp"
#include "core/Types.hpp"
#include "tools/AttacksOnTheFly.hpp"
#include "tools/MagicGenerator.hpp"

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
            Bitboard occupancy =
                setOccupancy(index, Attacks::rookRelevantBits[square], rookOccupancyMask);

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
            Bitboard occupancy = setOccupancy(index, Attacks::bishopRelevantBits[square],
                                              Attacks::bishopOccupancyMasks[square]);
            std::size_t magicIndex =
                Attacks::getBishopMagicIndex(static_cast<Square>(square), occupancy);
            Bitboard attacks = bishopAttacksOnTheFly(static_cast<Square>(square), occupancy);
            table[magicIndex] = attacks;
        }

        for (int index = 0; index < occupancyIndices; ++index)
        {
            file << "        0x" << std::hex << std::setw(16) << std::setfill('0') << table[index]
                 << "ULL,";
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
            Bitboard occupancy = setOccupancy(index, Attacks::rookRelevantBits[square],
                                              Attacks::rookOccupancyMasks[square]);
            std::size_t magicIndex =
                Attacks::getRookMagicIndex(static_cast<Square>(square), occupancy);
            Bitboard attacks = rookAttacksOnTheFly(static_cast<Square>(square), occupancy);
            table[magicIndex] = attacks;
        }

        for (int index = 0; index < occupancyIndices; ++index)
        {
            file << "        0x" << std::hex << std::setw(16) << std::setfill('0') << table[index]
                 << "ULL,";
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

void testSquareAttacked()
{
    std::cout << "Running testSquareAttacked unit tests...\n";

    // Test 1: Knight check threat detection
    {
        Board board;
        // Knight on d3 (index 43), White King on e1 (index 60)
        bool ok = board.parseFen("8/8/8/8/8/3n4/8/4K3 w - - 0 1");
        assert(ok);
        (void)ok; // silence unused var warnings

        // e1 should be attacked by Black (knight on d3)
        if (!Attacks::isSquareAttacked(board, Square::e1, Side::BLACK))
        {
            std::cout << "FAIL: Square e1 should be attacked by Black knight on d3\n";
            return;
        }

        // e1 should not be attacked by White
        if (Attacks::isSquareAttacked(board, Square::e1, Side::WHITE))
        {
            std::cout << "FAIL: Square e1 should not be attacked by White\n";
            return;
        }

        // attacksTo(board, Square::e1, Side::BLACK) should contain exactly the knight on d3
        Bitboard att = Attacks::attacksTo(board, Square::e1, Side::BLACK);
        Bitboard expected = 1ULL << static_cast<int>(Square::d3);
        if (att != expected)
        {
            std::cout << "FAIL: attacksTo(e1, BLACK) mismatch. Expected: " << std::hex << expected << ", Got: " << att << std::dec << "\n";
            return;
        }
    }

    // Test 2: Rook X-ray / Pin / Blocking
    {
        Board board;
        // Black Rook on e8 (index 4), White Pawn on e3 (index 44), White King on e1 (index 60)
        bool ok = board.parseFen("4r3/8/8/8/8/4P3/8/4K3 w - - 0 1");
        assert(ok);
        (void)ok;

        // e1 should not be attacked by Black because the Pawn on e3 blocks the rook.
        if (Attacks::isSquareAttacked(board, Square::e1, Side::BLACK))
        {
            std::cout << "FAIL: Square e1 should not be attacked due to blocking pawn on e3\n";
            return;
        }

        // e3 should be attacked by Black
        if (!Attacks::isSquareAttacked(board, Square::e3, Side::BLACK))
        {
            std::cout << "FAIL: Square e3 should be attacked by Black rook on e8\n";
            return;
        }

        // Now remove the blocking pawn:
        // Black Rook on e8, White King on e1
        ok = board.parseFen("4r3/8/8/8/8/8/8/4K3 w - - 0 1");
        assert(ok);
        (void)ok;

        // e1 should now be attacked by Black!
        if (!Attacks::isSquareAttacked(board, Square::e1, Side::BLACK))
        {
            std::cout << "FAIL: Square e1 should be attacked after block is removed\n";
            return;
        }
    }

    // Test 3: Bishop X-ray
    {
        Board board;
        // Black Bishop on a8 (index 0), White Pawn on d5 (index 27), White King on g2 (index 54)
        // a8 diagonal goes: b7, c6, d5, e4, f3, g2.
        bool ok = board.parseFen("b7/8/8/3P4/8/8/6K1/8 w - - 0 1");
        assert(ok);
        (void)ok;

        // g2 should not be attacked because d5 blocks it
        if (Attacks::isSquareAttacked(board, Square::g2, Side::BLACK))
        {
            std::cout << "FAIL: Square g2 should not be attacked due to blocking pawn on d5\n";
            return;
        }

        // Now remove the blocker
        ok = board.parseFen("b7/8/8/8/8/8/6K1/8 w - - 0 1");
        assert(ok);
        (void)ok;

        // g2 should be attacked now
        if (!Attacks::isSquareAttacked(board, Square::g2, Side::BLACK))
        {
            std::cout << "FAIL: Square g2 should be attacked by bishop on a8 without blocker\n";
            return;
        }
    }

    // Test 4: Castling safety / passage checks
    {
        Board board;
        // Standard starting-like castling setup but empty middle
        bool ok = board.parseFen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1");
        assert(ok);
        (void)ok;

        // f1 should not be attacked by Black
        if (Attacks::isSquareAttacked(board, Square::f1, Side::BLACK))
        {
            std::cout << "FAIL: Square f1 should be safe for castling\n";
            return;
        }

        // Now place a Black Queen controlling f1: Black Queen on f3 (index 45)
        ok = board.parseFen("r3k2r/8/8/8/8/5q2/8/R3K2R w KQkq - 0 1");
        assert(ok);
        (void)ok;

        // f1 should be attacked by Black Queen
        if (!Attacks::isSquareAttacked(board, Square::f1, Side::BLACK))
        {
            std::cout << "FAIL: Square f1 should be attacked by Black Queen on f3\n";
            return;
        }
    }

    std::cout << "All testSquareAttacked unit tests passed successfully!\n";
}

void runAllTests()
{
    testMagicAttacks();
    testSquareAttacked();
}

} // namespace Tools
} // namespace Bluie
