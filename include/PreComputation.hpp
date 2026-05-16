#pragma once

#include "Types.hpp"

extern Bitboard pawnAttacks[2][64];
extern Bitboard knightAttacks[64];

void computePawnAttacks();
void computeKnightAttacks();