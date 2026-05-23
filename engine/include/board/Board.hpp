#pragma once

#include "core/Types.hpp"
#include <array>
#include <cstdint>

/**
 * @class Board
 * @brief Represents the full state of a chess position.
 * 
 * Manages piece bitboards, combined side occupancies, active player turn, 
 * en passant square, and castling rights.
 */
class Board
{
public:
    /**
     * @brief Construct a new Board in the default state.
     */
    Board() = default;

private:
    std::array<Bitboard, 12> pieceBitboards; ///< Bitboards for the 12 piece types (WK to bp)
    std::array<Bitboard, 3> occupancy;       ///< Combined occupancies: [0]=Black, [1]=White, [2]=All

    Side turn;        ///< Side whose turn it is to move (WHITE or BLACK)
    Square enPassant; ///< En passant target square (NONE if none exists)
    uint8_t casstle;  ///< Castling rights bitmask (WKca)
};
