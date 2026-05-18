#include "Types.hpp"

Bitboard mask_bishop_attacks(Square square);
Bitboard mask_rook_attacks(Square square);

Bitboard bishop_attacks_on_the_fly(Square square, Bitboard occupancy);
Bitboard rook_attacks_on_the_fly(Square square, Bitboard occupancy);