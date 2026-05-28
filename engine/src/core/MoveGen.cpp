#include "core/MoveGen.hpp"
#include "attacks/Attacks.hpp" // IWYU pragma: keep
#include "attacks/AttacksAPI.hpp"
#include "core/Bitboard.hpp"
#include <cassert>

namespace Bluie
{

MoveList MoveGen::getPseudoLegalMoves(const Board& board)
{
    MoveList moveList;
    Side activeSide = board.getTurn();
    Side opponentSide = (activeSide == Side::WHITE) ? Side::BLACK : Side::WHITE;

    Bitboard friendlyOcc = board.getOccupancy(activeSide);
    Bitboard opponentOcc = board.getOccupancy(opponentSide);
    Bitboard allOcc = board.getOccupancy(Side::NONE);
    Bitboard emptyOcc = ~allOcc;

    // --- 1. PAWN MOVE GENERATION ---
    if (activeSide == Side::WHITE)
    {
        Bitboard pawns = board.getPieceBitboard(Piece::P);

        // White Pawn single push (up 1 rank / decrease index by 8)
        Bitboard singlePush = (pawns >> 8) & emptyOcc;
        Bitboard sp = singlePush;
        while (sp)
        {
            int toIdx = Bitboards::getLSBIndex(sp);
            int fromIdx = toIdx + 8;
            
            // Check for promotions (rank 8, i.e., index < 8)
            if (toIdx < 8)
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PR_QUEEN));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PR_ROOK));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PR_BISHOP));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PR_KNIGHT));
            }
            else
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::QUIET));
            }
            Bitboards::popLSB(sp);
        }

        // White Pawn double push (rank 2 to rank 4, i.e., index 48-55 to index 32-39)
        Bitboard doublePush = ((pawns & Bitboards::Masks::RANK_2) >> 8) & emptyOcc;
        doublePush = (doublePush >> 8) & emptyOcc;
        Bitboard dp = doublePush;
        while (dp)
        {
            int toIdx = Bitboards::getLSBIndex(dp);
            int fromIdx = toIdx + 16;
            moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::DOUBLE_PAWN_PUSH));
            Bitboards::popLSB(dp);
        }

        // White Pawn diagonal attacks (left: index - 9, right: index - 7)
        Bitboard leftAttacks = ((pawns & Bitboards::Masks::NOT_A_FILE) >> 9) & opponentOcc;
        Bitboard la = leftAttacks;
        while (la)
        {
            int toIdx = Bitboards::getLSBIndex(la);
            int fromIdx = toIdx + 9;
            if (toIdx < 8)
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_QUEEN));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_ROOK));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_BISHOP));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_KNIGHT));
            }
            else
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::CAPTURE));
            }
            Bitboards::popLSB(la);
        }

        Bitboard rightAttacks = ((pawns & Bitboards::Masks::NOT_H_FILE) >> 7) & opponentOcc;
        Bitboard ra = rightAttacks;
        while (ra)
        {
            int toIdx = Bitboards::getLSBIndex(ra);
            int fromIdx = toIdx + 7;
            if (toIdx < 8)
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_QUEEN));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_ROOK));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_BISHOP));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_KNIGHT));
            }
            else
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::CAPTURE));
            }
            Bitboards::popLSB(ra);
        }

        // White Pawn En Passant diagonal captures
        Square epSq = board.getEnPassant();
        if (epSq != Square::NO_SQUARE)
        {
            Bitboard candidatePawns = Attacks::pawnAttacks[toIndex(Side::BLACK)][toIndex(epSq)] & pawns;
            while (candidatePawns)
            {
                int fromIdx = Bitboards::getLSBIndex(candidatePawns);
                moveList.add(Move(static_cast<Square>(fromIdx), epSq, Move::Flag::EN_PASSANT));
                Bitboards::popLSB(candidatePawns);
            }
        }
    }
    else // BLACK TURN
    {
        Bitboard pawns = board.getPieceBitboard(Piece::p);

        // Black Pawn single push (down 1 rank / increase index by 8)
        Bitboard singlePush = (pawns << 8) & emptyOcc;
        Bitboard sp = singlePush;
        while (sp)
        {
            int toIdx = Bitboards::getLSBIndex(sp);
            int fromIdx = toIdx - 8;
            
            if (toIdx >= 56)
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PR_QUEEN));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PR_ROOK));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PR_BISHOP));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PR_KNIGHT));
            }
            else
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::QUIET));
            }
            Bitboards::popLSB(sp);
        }

        // Black Pawn double push (rank 7 to rank 5, i.e., index 8-15 to index 24-31)
        Bitboard doublePush = ((pawns & Bitboards::Masks::RANK_7) << 8) & emptyOcc;
        doublePush = (doublePush << 8) & emptyOcc;
        Bitboard dp = doublePush;
        while (dp)
        {
            int toIdx = Bitboards::getLSBIndex(dp);
            int fromIdx = toIdx - 16;
            moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::DOUBLE_PAWN_PUSH));
            Bitboards::popLSB(dp);
        }

        // Black Pawn diagonal attacks (left: index + 7, right: index + 9)
        Bitboard leftAttacks = ((pawns & Bitboards::Masks::NOT_A_FILE) << 7) & opponentOcc;
        Bitboard la = leftAttacks;
        while (la)
        {
            int toIdx = Bitboards::getLSBIndex(la);
            int fromIdx = toIdx - 7;
            if (toIdx >= 56)
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_QUEEN));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_ROOK));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_BISHOP));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_KNIGHT));
            }
            else
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::CAPTURE));
            }
            Bitboards::popLSB(la);
        }

        Bitboard rightAttacks = ((pawns & Bitboards::Masks::NOT_H_FILE) << 9) & opponentOcc;
        Bitboard ra = rightAttacks;
        while (ra)
        {
            int toIdx = Bitboards::getLSBIndex(ra);
            int fromIdx = toIdx - 9;
            if (toIdx >= 56)
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_QUEEN));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_ROOK));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_BISHOP));
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::PC_KNIGHT));
            }
            else
            {
                moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), Move::Flag::CAPTURE));
            }
            Bitboards::popLSB(ra);
        }

        // Black Pawn En Passant diagonal captures
        Square epSq = board.getEnPassant();
        if (epSq != Square::NO_SQUARE)
        {
            Bitboard candidatePawns = Attacks::pawnAttacks[toIndex(Side::WHITE)][toIndex(epSq)] & pawns;
            while (candidatePawns)
            {
                int fromIdx = Bitboards::getLSBIndex(candidatePawns);
                moveList.add(Move(static_cast<Square>(fromIdx), epSq, Move::Flag::EN_PASSANT));
                Bitboards::popLSB(candidatePawns);
            }
        }
    }

    // --- 2. KNIGHT MOVE GENERATION ---
    Piece activeKnight = (activeSide == Side::WHITE) ? Piece::N : Piece::n;
    Bitboard knights = board.getPieceBitboard(activeKnight);
    while (knights)
    {
        int fromIdx = Bitboards::getLSBIndex(knights);
        Bitboard attacks = Attacks::knightAttacks[fromIdx] & ~friendlyOcc;
        while (attacks)
        {
            int toIdx = Bitboards::getLSBIndex(attacks);
            bool isCapture = (opponentOcc & (1ULL << toIdx)) != 0;
            moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), 
                              isCapture ? Move::Flag::CAPTURE : Move::Flag::QUIET));
            Bitboards::popLSB(attacks);
        }
        Bitboards::popLSB(knights);
    }

    // --- 3. KING MOVE GENERATION & CASTLING ---
    Piece activeKing = (activeSide == Side::WHITE) ? Piece::K : Piece::k;
    Bitboard kings = board.getPieceBitboard(activeKing);
    if (kings)
    {
        int fromIdx = Bitboards::getLSBIndex(kings);
        Bitboard attacks = Attacks::kingAttacks[fromIdx] & ~friendlyOcc;
        while (attacks)
        {
            int toIdx = Bitboards::getLSBIndex(attacks);
            bool isCapture = (opponentOcc & (1ULL << toIdx)) != 0;
            moveList.add(Move(static_cast<Square>(fromIdx), static_cast<Square>(toIdx), 
                              isCapture ? Move::Flag::CAPTURE : Move::Flag::QUIET));
            Bitboards::popLSB(attacks);
        }

        // CASTLING (Pseudo-legal check: empty intermediate squares)
        uint8_t castlingRights = board.getCastle();
        if (activeSide == Side::WHITE)
        {
            // White Kingside castling
            if (castlingRights & 1)
            {
                if (!(allOcc & (1ULL << 61)) && !(allOcc & (1ULL << 62)))
                {
                    moveList.add(Move(Square::e1, Square::g1, Move::Flag::KING_CASTLE));
                }
            }
            // White Queenside castling
            if (castlingRights & 2)
            {
                if (!(allOcc & (1ULL << 59)) && !(allOcc & (1ULL << 58)) && !(allOcc & (1ULL << 57)))
                {
                    moveList.add(Move(Square::e1, Square::c1, Move::Flag::QUEEN_CASTLE));
                }
            }
        }
        else // BLACK
        {
            // Black Kingside castling
            if (castlingRights & 4)
            {
                if (!(allOcc & (1ULL << 5)) && !(allOcc & (1ULL << 6)))
                {
                    moveList.add(Move(Square::e8, Square::g8, Move::Flag::KING_CASTLE));
                }
            }
            // Black Queenside castling
            if (castlingRights & 8)
            {
                if (!(allOcc & (1ULL << 3)) && !(allOcc & (1ULL << 2)) && !(allOcc & (1ULL << 1)))
                {
                    moveList.add(Move(Square::e8, Square::c8, Move::Flag::QUEEN_CASTLE));
                }
            }
        }
    }

    // --- 4. SLIDING BISHOP & QUEEN MOVE GENERATION ---
    Piece activeBishop = (activeSide == Side::WHITE) ? Piece::B : Piece::b;
    Piece activeQueen = (activeSide == Side::WHITE) ? Piece::Q : Piece::q;
    Bitboard diagonalSliders = board.getPieceBitboard(activeBishop) | board.getPieceBitboard(activeQueen);
    while (diagonalSliders)
    {
        int fromIdx = Bitboards::getLSBIndex(diagonalSliders);
        Square sq = static_cast<Square>(fromIdx);
        Bitboard attacks = Attacks::bishopAttacks[fromIdx][Attacks::getBishopMagicIndex(sq, allOcc)] & ~friendlyOcc;
        while (attacks)
        {
            int toIdx = Bitboards::getLSBIndex(attacks);
            bool isCapture = (opponentOcc & (1ULL << toIdx)) != 0;
            moveList.add(Move(sq, static_cast<Square>(toIdx), 
                              isCapture ? Move::Flag::CAPTURE : Move::Flag::QUIET));
            Bitboards::popLSB(attacks);
        }
        Bitboards::popLSB(diagonalSliders);
    }

    // --- 5. SLIDING ROOK & QUEEN MOVE GENERATION ---
    Piece activeRook = (activeSide == Side::WHITE) ? Piece::R : Piece::r;
    Bitboard straightSliders = board.getPieceBitboard(activeRook) | board.getPieceBitboard(activeQueen);
    while (straightSliders)
    {
        int fromIdx = Bitboards::getLSBIndex(straightSliders);
        Square sq = static_cast<Square>(fromIdx);
        Bitboard attacks = Attacks::rookAttacks[fromIdx][Attacks::getRookMagicIndex(sq, allOcc)] & ~friendlyOcc;
        while (attacks)
        {
            int toIdx = Bitboards::getLSBIndex(attacks);
            bool isCapture = (opponentOcc & (1ULL << toIdx)) != 0;
            moveList.add(Move(sq, static_cast<Square>(toIdx), 
                              isCapture ? Move::Flag::CAPTURE : Move::Flag::QUIET));
            Bitboards::popLSB(attacks);
        }
        Bitboards::popLSB(straightSliders);
    }

    return moveList;
}

MoveList MoveGen::getLegalMoves(const Board& board)
{
    MoveList pseudoMoves = getPseudoLegalMoves(board);
    MoveList legalMoves;
    Side activeSide = board.getTurn();
    Side opponentSide = (activeSide == Side::WHITE) ? Side::BLACK : Side::WHITE;

    for (int i = 0; i < pseudoMoves.count; ++i)
    {
        Move m = pseudoMoves.moves[i];
        
        // 1. Specialized Castling Check Constraints
        if (m.getFlags() == Move::Flag::KING_CASTLE || m.getFlags() == Move::Flag::QUEEN_CASTLE)
        {
            Square kingStart = (activeSide == Side::WHITE) ? Square::e1 : Square::e8;
            // King cannot castle out of check
            if (Attacks::isSquareAttacked(board, kingStart, opponentSide)) continue;

            Square stepSquare = Square::NO_SQUARE;
            if (m.getFlags() == Move::Flag::KING_CASTLE)
            {
                stepSquare = (activeSide == Side::WHITE) ? Square::f1 : Square::f8;
            }
            else
            {
                stepSquare = (activeSide == Side::WHITE) ? Square::d1 : Square::d8;
            }
            // King cannot pass through attacked squares
            if (Attacks::isSquareAttacked(board, stepSquare, opponentSide)) continue;
        }

        // 2. Standard Move Legality: copy board, play move, assert King safety
        Board temp = board;
        temp.makeMove(m);

        // Find the King square of activeSide on the updated position
        Piece activeKing = (activeSide == Side::WHITE) ? Piece::K : Piece::k;
        Bitboard kingBB = temp.getPieceBitboard(activeKing);
        if (!kingBB) continue; // Safety guard
        Square kingSq = static_cast<Square>(Bitboards::getLSBIndex(kingBB));

        // If the King is not attacked on the new board, the move is fully legal!
        if (!Attacks::isSquareAttacked(temp, kingSq, opponentSide))
        {
            legalMoves.add(m);
        }
    }
    return legalMoves;
}

} // namespace Bluie
