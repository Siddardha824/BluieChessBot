#include "attacks/AttacksAPI.hpp"
#include "attacks/Attacks.hpp"
#include "core/Bitboard.hpp"

namespace Bluie
{
namespace Attacks
{

Bitboard attacksTo(const Board& board, Square sq, Side attackerSide)
{
    Bitboard attacks = 0ULL;
    Bitboard occAll = board.getOccupancy(Side::NONE);

    // 1. Pawns: pawns of attackerSide attacking sq are on opposite-side pawn attack squares from sq
    Side oppositeSide = (attackerSide == Side::WHITE) ? Side::BLACK : Side::WHITE;
    Bitboard attackingPawns = pawnAttacks[toIndex(oppositeSide)][toIndex(sq)] & 
                              board.getPieceBitboard(attackerSide == Side::WHITE ? Piece::P : Piece::p);
    attacks |= attackingPawns;

    // 2. Knights: knights attacking sq are on knight attack squares from sq
    Bitboard attackingKnights = knightAttacks[toIndex(sq)] & 
                                board.getPieceBitboard(attackerSide == Side::WHITE ? Piece::N : Piece::n);
    attacks |= attackingKnights;

    // 3. Kings: kings attacking sq are on king attack squares from sq
    Bitboard attackingKings = kingAttacks[toIndex(sq)] & 
                              board.getPieceBitboard(attackerSide == Side::WHITE ? Piece::K : Piece::k);
    attacks |= attackingKings;

    // 4. Bishops & Queens: sliding diagonal attacks from sq matching bishop/queen bitboards
    Bitboard bAttacks = bishopAttacks[toIndex(sq)][getBishopMagicIndex(sq, occAll)];
    Bitboard attackingBishops = bAttacks & 
                                (board.getPieceBitboard(attackerSide == Side::WHITE ? Piece::B : Piece::b) |
                                 board.getPieceBitboard(attackerSide == Side::WHITE ? Piece::Q : Piece::q));
    attacks |= attackingBishops;

    // 5. Rooks & Queens: sliding orthogonal attacks from sq matching rook/queen bitboards
    Bitboard rAttacks = rookAttacks[toIndex(sq)][getRookMagicIndex(sq, occAll)];
    Bitboard attackingRooks = rAttacks & 
                              (board.getPieceBitboard(attackerSide == Side::WHITE ? Piece::R : Piece::r) |
                               board.getPieceBitboard(attackerSide == Side::WHITE ? Piece::Q : Piece::q));
    attacks |= attackingRooks;

    return attacks;
}

bool isSquareAttacked(const Board& board, Square sq, Side attackerSide)
{
    return attacksTo(board, sq, attackerSide) != 0ULL;
}

} // namespace Attacks
} // namespace Bluie
