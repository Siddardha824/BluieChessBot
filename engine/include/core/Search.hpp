#pragma once

#include "board/Board.hpp"
#include "core/Types.hpp"

namespace Bluie
{

/**
 * @struct SearchResult
 * @brief Bundles search results including the selected move, evaluation score, and node count.
 */
struct SearchResult
{
    Move bestMove = Move::NO_MOVE; ///< The best move found by the search
    int score = 0;                 ///< The evaluation score of the position
    int nodes = 0;                 ///< Total number of nodes evaluated during the search
};

/**
 * @class Search
 * @brief Brute-force depth-bounded Negamax chess engine search system.
 *
 * Implements a pure brute-force Negamax search algorithm without alpha-beta pruning.
 * Safely handles checkmate, stalemate, and 50-move rule draw scenarios.
 */
class Search
{
  public:
    /**
     * @brief Searches the board to the specified depth and returns the best move.
     * @param board The active board position state.
     * @param depth The target search depth.
     * @return SearchResult struct with best move, score, and nodes checked.
     */
    static SearchResult findBestMove(Board& board, int depth);

    /**
     * @brief Recursive Negamax evaluation function.
     * @param board Copy of the board state.
     * @param depth Remaining search depth.
     * @param ply Distance from the search root.
     * @param nodesChecked Counter for tracking total searched nodes.
     * @return Evaluation score from the perspective of the side to move.
     */
    static int negamax(Board& board, int depth, int ply, int& nodesChecked);
};

} // namespace Bluie
