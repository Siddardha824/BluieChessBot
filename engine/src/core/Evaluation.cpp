#include "core/Evaluation.hpp"
#include "core/Bitboard.hpp"

namespace Bluie
{

// 0 = a8, 63 = h1. 
// For white: rank 8 (top) is row 0, rank 1 (bottom) is row 7.
// White moves from rank 1 (indices 56-63) up towards rank 8 (indices 0-7).
const std::array<int, 64> Evaluation::PAWN_PST = {
      0,  0,  0,  0,  0,  0,  0,  0,
     50, 50, 50, 50, 50, 50, 50, 50,
     10, 10, 20, 30, 30, 20, 10, 10,
      5,  5, 10, 25, 25, 10,  5,  5,
      0,  0,  0, 20, 20,  0,  0,  0,
      5, -5,-10,  0,  0,-10, -5,  5,
      5, 10, 10,-20,-20, 10, 10,  5,
      0,  0,  0,  0,  0,  0,  0,  0
};

const std::array<int, 64> Evaluation::KNIGHT_PST = {
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
};

const std::array<int, 64> Evaluation::BISHOP_PST = {
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
};

const std::array<int, 64> Evaluation::ROOK_PST = {
      0,  0,  0,  0,  0,  0,  0,  0,
      5, 10, 10, 10, 10, 10, 10,  5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
      0,  0,  0,  5,  5,  0,  0,  0
};

const std::array<int, 64> Evaluation::QUEEN_PST = {
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  5,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
};

const std::array<int, 64> Evaluation::KING_PST = {
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
};

int Evaluation::evaluate(const Board& board)
{
    int score = 0;

    // --- WHITE PIECES ---
    // Pawns
    Bitboard wp = board.getPieceBitboard(Piece::P);
    while (wp)
    {
        int sq = Bitboards::getLSBIndex(wp);
        Bitboards::popLSB(wp);
        score += PAWN_VALUE + PAWN_PST[sq];
    }

    // Knights
    Bitboard wn = board.getPieceBitboard(Piece::N);
    while (wn)
    {
        int sq = Bitboards::getLSBIndex(wn);
        Bitboards::popLSB(wn);
        score += KNIGHT_VALUE + KNIGHT_PST[sq];
    }

    // Bishops
    Bitboard wb = board.getPieceBitboard(Piece::B);
    while (wb)
    {
        int sq = Bitboards::getLSBIndex(wb);
        Bitboards::popLSB(wb);
        score += BISHOP_VALUE + BISHOP_PST[sq];
    }

    // Rooks
    Bitboard wr = board.getPieceBitboard(Piece::R);
    while (wr)
    {
        int sq = Bitboards::getLSBIndex(wr);
        Bitboards::popLSB(wr);
        score += ROOK_VALUE + ROOK_PST[sq];
    }

    // Queens
    Bitboard wq = board.getPieceBitboard(Piece::Q);
    while (wq)
    {
        int sq = Bitboards::getLSBIndex(wq);
        Bitboards::popLSB(wq);
        score += QUEEN_VALUE + QUEEN_PST[sq];
    }

    // Kings
    Bitboard wk = board.getPieceBitboard(Piece::K);
    while (wk)
    {
        int sq = Bitboards::getLSBIndex(wk);
        Bitboards::popLSB(wk);
        score += KING_PST[sq]; // King material itself is typically ignored in static eval, or can be added.
    }


    // --- BLACK PIECES ---
    // For Black pieces, mirror PST vertically (square ^ 56) to maintain symmetry.
    // Pawns
    Bitboard bp = board.getPieceBitboard(Piece::p);
    while (bp)
    {
        int sq = Bitboards::getLSBIndex(bp);
        Bitboards::popLSB(bp);
        score -= (PAWN_VALUE + PAWN_PST[sq ^ 56]);
    }

    // Knights
    Bitboard bn = board.getPieceBitboard(Piece::n);
    while (bn)
    {
        int sq = Bitboards::getLSBIndex(bn);
        Bitboards::popLSB(bn);
        score -= (KNIGHT_VALUE + KNIGHT_PST[sq ^ 56]);
    }

    // Bishops
    Bitboard bb_b = board.getPieceBitboard(Piece::b);
    while (bb_b)
    {
        int sq = Bitboards::getLSBIndex(bb_b);
        Bitboards::popLSB(bb_b);
        score -= (BISHOP_VALUE + BISHOP_PST[sq ^ 56]);
    }

    // Rooks
    Bitboard br = board.getPieceBitboard(Piece::r);
    while (br)
    {
        int sq = Bitboards::getLSBIndex(br);
        Bitboards::popLSB(br);
        score -= (ROOK_VALUE + ROOK_PST[sq ^ 56]);
    }

    // Queens
    Bitboard bq = board.getPieceBitboard(Piece::q);
    while (bq)
    {
        int sq = Bitboards::getLSBIndex(bq);
        Bitboards::popLSB(bq);
        score -= (QUEEN_VALUE + QUEEN_PST[sq ^ 56]);
    }

    // Kings
    Bitboard bk = board.getPieceBitboard(Piece::k);
    while (bk)
    {
        int sq = Bitboards::getLSBIndex(bk);
        Bitboards::popLSB(bk);
        score -= KING_PST[sq ^ 56];
    }

    return score;
}

} // namespace Bluie
