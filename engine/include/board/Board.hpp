#pragma once

#include "core/Types.hpp"
#include <array>
#include <cstdint>
#include <string>

namespace Bluie
{

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
     * @brief Construct a new Board in the default state (empty).
     */
    Board();

    /**
     * @brief Clear the board state completely.
     */
    void clear();

    /**
     * @brief Parse a FEN chess format string and setup the board.
     * @param fen The FEN string.
     * @return True if parsing succeeded, False otherwise.
     */
    bool parseFen(const std::string& fen);

    /**
     * @brief Applies a move to the board, updating occupancies and states.
     * @param move The packed binary Move.
     */
    void makeMove(Move move);

    // Public getters and setters for UCI and telemetry integration
    Side getTurn() const { return turn; }
    void setTurn(Side side) { turn = side; }

    Square getEnPassant() const { return enPassant; }
    void setEnPassant(Square sq) { enPassant = sq; }

    uint8_t getCastle() const { return casstle; }
    void setCastle(uint8_t c) { casstle = c; }

    Bitboard getPieceBitboard(Piece p) const;
    void setPieceBitboard(Piece p, Bitboard bb);

    Bitboard getOccupancy(Side side) const;
    void updateOccupancies();

private:
    std::array<Bitboard, 12> pieceBitboards; ///< Bitboards for the 12 piece types (WK to bp)
    std::array<Bitboard, 3> occupancy;       ///< Combined occupancies: [0]=Black, [1]=White, [2]=All

    Side turn;        ///< Side whose turn it is to move (WHITE or BLACK)
    Square enPassant; ///< En passant target square (NO_SQUARE if none exists)
    uint8_t casstle;  ///< Castling rights bitmask (WKca)
};

} // namespace Bluie
