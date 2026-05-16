#pragma once

#include "Types.hpp"

extern Bitboard pawnAttacks[2][64];
extern Bitboard knightAttacks[64];
extern Bitboard kingAttacks[64];

void initPrecompute();
void computePawnAttacks();
void computeKnightAttacks();
void computeKingAttacks();