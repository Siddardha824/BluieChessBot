#include <iostream>

#include "Bluie.hpp"

int main()
{
    // Initializing all the precomputed attacks tables
    initPrecompute();

    Bitboard board = 0ULL;
    setBit(board, e4);
    setBit(board, a2);
    setBit(board, g6);
    printBitboard(board);
    std::cout << countBits(board) << std::endl;
    std::cout << squareToCoordinates[getLSBIndex(board)] << std::endl;
}
