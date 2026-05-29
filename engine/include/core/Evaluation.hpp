#pragma once

#include "board/Board.hpp"
#include "core/Types.hpp"
#include <array>

namespace Bluie
{

/**
 * @class Evaluation
 * @brief Handles material and positional chess board evaluation.
 *
 * Implements standard piece values and Piece-Square Tables (PSTs).
 * Evaluates the board state and returns a positional score in centipawns
 * from White's perspective (positive is good for White, negative for Black).
 */
class Evaluation
{
  public:
    // Standard Piece Values in centipawns (Pawns=100, Knights=320, Bishops=330, Rooks=500, Queens=900)
    static constexpr int PAWN_VALUE = 100;
    static constexpr int KNIGHT_VALUE = 320;
    static constexpr int BISHOP_VALUE = 330;
    static constexpr int ROOK_VALUE = 500;
    static constexpr int QUEEN_VALUE = 900;
    static constexpr int KING_VALUE = 20000;

    // Piece-Square Tables (PST) arrays for each piece type
    static const std::array<int, 64> PAWN_PST;
    static const std::array<int, 64> KNIGHT_PST;
    static const std::array<int, 64> BISHOP_PST;
    static const std::array<int, 64> ROOK_PST;
    static const std::array<int, 64> QUEEN_PST;
    static const std::array<int, 64> KING_PST;

    /**
     * @brief Computes static evaluation score of a given board position.
     * @param board The chess board state.
     * @return Centipawn score from White's perspective (positive = White leads, negative = Black leads).
     */
    static int evaluate(const Board& board);
};

} // namespace Bluie
