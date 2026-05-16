#include <iostream>
#include <iomanip>
#include "Bluie.hpp"
#include "PreComputation.hpp"
#include "Types.hpp"

// Print the bitboard in a human-readable format (for debugging)
void printBitboard(Bitboard b)
{
    for (int rank = 0; rank < 8; ++rank)
    {
        std::cout << 8 - rank << "  ";
        for (int file = 0; file < 8; ++file)
        {
            int square = rank * 8 + file;
            std::cout << (getBit(b, square) ? "1 " : ". ");
        }
        std::cout << std::endl;
    }
    std::cout << "   a b c d e f g h" << std::endl << std::endl;
    std::cout << "Bitboard: " << std::hex << std::setfill('0') << std::setw(16) <<  b << std::endl << std::endl;
}

int main()
{
    // Initializing all the precomputed attacks tables
    initPrecompute();

    for (int square = 0; square < 64; ++square) {
        printBitboard(kingAttacks[square]);
    }
}
