#pragma once

#include <cstdint>

using Bitboard = uint64_t;

constexpr int MAX_MOVES = 256;

struct Move {
  int from_square;
  int to_square;

  Move(int from, int to) : from_square(from), to_square(to) {}
};

struct MoveList {
  Move moves[MAX_MOVES];
  int count = 0;

  inline void add(Move m) { moves[count++] = m; }
};