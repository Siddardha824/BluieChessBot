#include "Types.hpp"

Bitboard maskBishopAttacks(Square square);
Bitboard maskRookAttacks(Square square);

Bitboard bishopAttacksOnTheFly(Square square, Bitboard occupancy);
Bitboard rookAttacksOnTheFly(Square square, Bitboard occupancy);