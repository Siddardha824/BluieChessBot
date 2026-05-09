#include "Precomputed.hpp"
#include "Types.hpp"
#include "Bitboard.hpp"

Bitboard whitePawnMoves[64];

void calculateWhitePawnMoves() {
  for (int square = 0; square < 64; square++) {
    Bitboard pawn = 0ULL;
    // Place a pawn on the square
    setBit(pawn, square);
    whitePawnMoves[square] = pawn << 8;
  }
}