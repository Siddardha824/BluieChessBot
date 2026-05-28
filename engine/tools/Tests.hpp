#pragma once

namespace Bluie
{
namespace Tools
{

/**
 * @brief Run correctness tests for bishop and rook magic lookup tables.
 *
 * Compares precomputed magic bitboard lookups with slow on-the-fly
 * ray casting calculations across all 64 squares and occupancy states.
 */
void testMagicAttacks();

/**
 * @brief Regenerates and writes the correct AttackTables.hpp header file.
 *
 * Orders generated table elements directly by their mapped magicIndex
 * hash key to ensure 100% correct engine attack lookups.
 */
void writeAttackTablesHeaderFile();

} // namespace Tools
} // namespace Bluie
