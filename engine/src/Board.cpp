#include "Types.hpp"
#include <array>
#include <cstdint>

class Board
{
    std::array<Bitboard, 12> pieceBitboards;
    std::array<Bitboard, 3> occupancy;

    Side turn;
    Square enPassant;
    uint8_t casstle;

};