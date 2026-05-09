#pragma once

#include <cstdint>

using Bitboard = uint64_t;

constexpr int MAX_MOVES = 256;

struct Move {
  int fromSquare;
  int toSquare;

  Move(int from, int to) : fromSquare(from), toSquare(to) {}
};

struct MoveList {
  Move moves[MAX_MOVES];
  int count = 0;

  inline void add(Move m) { moves[count++] = m; }
};