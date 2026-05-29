#include "core/Search.hpp"
#include "core/Evaluation.hpp"
#include "core/MoveGen.hpp"
#include "core/Bitboard.hpp"
#include "attacks/AttacksAPI.hpp"

namespace Bluie
{

SearchResult Search::findBestMove(Board& board, int depth)
{
    SearchResult result;
    int nodesChecked = 0;

    MoveGen moveGen;
    MoveList legals = moveGen.getLegalMoves(board);

    if (legals.count == 0)
    {
        result.bestMove = Move::NO_MOVE;
        result.score = 0;
        result.nodes = 0;
        return result;
    }

    // Default to first move in case scores are identical
    Move bestMove = legals.moves[0];
    int bestScore = -999999;

    // Standard brute-force Negamax root loop
    for (int i = 0; i < legals.count; ++i)
    {
        Move m = legals.moves[i];
        Board tempBoard = board;
        tempBoard.makeMove(m);
        nodesChecked++;

        // Search deeper recursively (root ply is 0, so next ply is 1)
        int score = -negamax(tempBoard, depth - 1, 1, nodesChecked);

        if (score > bestScore)
        {
            bestScore = score;
            bestMove = m;
        }
    }

    result.bestMove = bestMove;
    result.score = bestScore;
    result.nodes = nodesChecked;

    return result;
}

int Search::negamax(Board& board, int depth, int ply, int& nodesChecked)
{
    // 1. Draw Detection (50-move rule limit)
    if (ply > 0 && board.getHalfmoveClock() >= 100)
    {
        return 0; // standard draw score
    }

    // 2. Base Case: Target Depth Reached
    if (depth <= 0)
    {
        int perspective = (board.getTurn() == Side::WHITE) ? 1 : -1;
        return perspective * Evaluation::evaluate(board);
    }

    // 3. Generate Legal Moves
    MoveGen moveGen;
    MoveList legals = moveGen.getLegalMoves(board);

    // 4. Checkmate & Stalemate Detection
    if (legals.count == 0)
    {
        Piece friendlyKing = (board.getTurn() == Side::WHITE) ? Piece::K : Piece::k;
        Bitboard kingBB = board.getPieceBitboard(friendlyKing);
        Square kingSq = static_cast<Square>(Bitboards::getLSBIndex(kingBB));
        Side opponent = (board.getTurn() == Side::WHITE) ? Side::BLACK : Side::WHITE;
        
        bool inCheck = Attacks::isSquareAttacked(board, kingSq, opponent);

        if (inCheck)
        {
            // Return mate score adjusted by distance from root (ply).
            // A smaller ply (closer to root) gives a more negative loss score,
            // which encourages the engine to delay checkmate as long as possible.
            return -30000 + ply;
        }
        else
        {
            return 0; // Stalemate draw
        }
    }

    // 5. Brute-Force Negamax Loop
    int bestScore = -999999;
    for (int i = 0; i < legals.count; ++i)
    {
        Board tempBoard = board;
        tempBoard.makeMove(legals.moves[i]);
        nodesChecked++;

        int score = -negamax(tempBoard, depth - 1, ply + 1, nodesChecked);
        if (score > bestScore)
        {
            bestScore = score;
        }
    }

    return bestScore;
}

} // namespace Bluie
