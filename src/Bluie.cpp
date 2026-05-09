#include <iostream>

#include "Bluie.hpp"
#include "Precomputed.hpp"

// Print the bitboard in a human-readable format (for debugging)
void printBitboard(Bitboard b) {
  for (int rank = 7; rank >= 0; --rank) {
    for (int file = 0; file < 8; ++file) {
      int square = rank * 8 + file;
      std::cout << (getBit(b, square) ? "1 " : ". ");
    }
    std::cout << std::endl;
  }
  std::cout << std::endl;
}

int main() {
  calculateWhitePawnMoves();
  for (int i = 0; i < 64; i++) {
    printBitboard(whitePawnMoves[i]);
  }
  return 0;
}
