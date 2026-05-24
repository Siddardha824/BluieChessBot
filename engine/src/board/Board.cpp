#include "board/Board.hpp"
#include <sstream>
#include <iostream>

namespace Bluie
{

Board::Board()
{
    clear();
}

void Board::clear()
{
    pieceBitboards.fill(0ULL);
    occupancy.fill(0ULL);
    turn = WHITE;
    enPassant = NO_SQUARE;
    casstle = 0;
}

Bitboard Board::getPieceBitboard(Piece p) const
{
    if (p == NO_PIECE) return 0ULL;
    return pieceBitboards[static_cast<size_t>(p)];
}

void Board::setPieceBitboard(Piece p, Bitboard bb)
{
    if (p == NO_PIECE) return;
    pieceBitboards[static_cast<size_t>(p)] = bb;
}

Bitboard Board::getOccupancy(Side side) const
{
    if (side == NONE) return occupancy[2]; // Combined
    return occupancy[side == WHITE ? 1 : 0];
}

void Board::updateOccupancies()
{
    occupancy.fill(0ULL);
    
    // Combine White piece bitboards (P to K are indices 0 to 5)
    for (int p = 0; p < 6; ++p)
    {
        occupancy[1] |= pieceBitboards[p];
    }
    
    // Combine Black piece bitboards (p to k are indices 6 to 11)
    for (int p = 6; p < 12; ++p)
    {
        occupancy[0] |= pieceBitboards[p];
    }
    
    // Combined all occupancy
    occupancy[2] = occupancy[0] | occupancy[1];
}

bool Board::parseFen(const std::string& fen)
{
    clear();
    
    std::stringstream ss(fen);
    std::string placement, activeColor, castling, epSquare, halfmove, fullmove;
    
    if (!(ss >> placement)) return false;
    
    // 1. Piece Placement parsing
    int squareIdx = 0;
    for (char c : placement)
    {
        if (c == '/') continue;
        if (c >= '1' && c <= '8')
        {
            squareIdx += (c - '0');
        }
        else
        {
            Piece p = NO_PIECE;
            switch (c)
            {
                case 'P': p = P; break;
                case 'N': p = N; break;
                case 'B': p = B; break;
                case 'R': p = R; break;
                case 'Q': p = Q; break;
                case 'K': p = K; break;
                case 'p': p = p; break;
                case 'n': p = n; break;
                case 'b': p = b; break;
                case 'r': p = r; break;
                case 'q': p = q; break;
                case 'k': p = k; break;
                default: return false; // Invalid char
            }
            if (p != NO_PIECE && squareIdx < 64)
            {
                // Add the bit representing c to p's bitboard
                // Note: a8 is 0, h1 is 63. The square bit starts at MSB (square index 0)
                pieceBitboards[static_cast<size_t>(p)] |= (1ULL << (63 - squareIdx));
                squareIdx++;
            }
        }
    }
    
    // 2. Active color
    if (ss >> activeColor)
    {
        turn = (activeColor == "w") ? WHITE : BLACK;
    }
    
    // 3. Castling rights
    if (ss >> castling)
    {
        for (char c : castling)
        {
            if (c == 'K') casstle |= 1;  // WK
            else if (c == 'Q') casstle |= 2;  // WQ
            else if (c == 'k') casstle |= 4;  // BK
            else if (c == 'q') casstle |= 8;  // BQ
        }
    }
    
    // 4. En Passant Square
    if (ss >> epSquare && epSquare != "-")
    {
        if (epSquare.length() >= 2)
        {
            int col = epSquare[0] - 'a';
            int row = '8' - epSquare[1];
            if (col >= 0 && col < 8 && row >= 0 && row < 8)
            {
                enPassant = static_cast<Square>(row * 8 + col);
            }
        }
    }
    
    updateOccupancies();
    return true;
}

void Board::makeMove(Move move)
{
    Square from = move.getFrom();
    Square to = move.getTo();
    Move::Flag flag = move.getFlags();
    
    uint64_t fromBit = (1ULL << (63 - static_cast<int>(from)));
    uint64_t toBit = (1ULL << (63 - static_cast<int>(to)));
    
    // Find the piece that is moving
    Piece movingPiece = NO_PIECE;
    for (int p = 0; p < 12; ++p)
    {
        if (pieceBitboards[p] & fromBit)
        {
            movingPiece = static_cast<Piece>(p);
            break;
        }
    }
    
    if (movingPiece == NO_PIECE) return; // Illegal moving piece
    
    // 1. Handle capturing (if capture flag or standard capture)
    if (move.isCapture())
    {
        Square captureSq = to;
        
        // Handle En Passant capture target square (it captures the pawn behind the target square)
        if (flag == Move::EN_PASSANT)
        {
            captureSq = static_cast<Square>(static_cast<int>(to) + (movingPiece == P ? 8 : -8));
        }
        
        uint64_t capBit = (1ULL << (63 - static_cast<int>(captureSq)));
        
        // Remove the captured piece
        for (int p = 0; p < 12; ++p)
        {
            if (pieceBitboards[p] & capBit)
            {
                pieceBitboards[p] &= ~capBit;
                break;
            }
        }
    }
    
    // 2. Perform moving the piece
    pieceBitboards[static_cast<size_t>(movingPiece)] &= ~fromBit;
    
    if (move.isPromotion())
    {
        // Replace with promoted piece
        Piece promotedPiece = NO_PIECE;
        switch (flag)
        {
            case Move::PR_KNIGHT: case Move::PC_KNIGHT:
                promotedPiece = (movingPiece == P) ? N : n;
                break;
            case Move::PR_BISHOP: case Move::PC_BISHOP:
                promotedPiece = (movingPiece == P) ? B : b;
                break;
            case Move::PR_ROOK: case Move::PC_ROOK:
                promotedPiece = (movingPiece == P) ? R : r;
                break;
            case Move::PR_QUEEN: case Move::PC_QUEEN:
                promotedPiece = (movingPiece == P) ? Q : q;
                break;
            default:
                promotedPiece = (movingPiece == P) ? Q : q;
                break;
        }
        pieceBitboards[static_cast<size_t>(promotedPiece)] |= toBit;
    }
    else
    {
        pieceBitboards[static_cast<size_t>(movingPiece)] |= toBit;
    }
    
    // 3. Handle Castling rook movements
    if (flag == Move::KING_CASTLE)
    {
        if (movingPiece == K) // White Kingside
        {
            // Move rook from h1 (63) to f1 (61)
            pieceBitboards[static_cast<size_t>(R)] &= ~(1ULL << (63 - 63));
            pieceBitboards[static_cast<size_t>(R)] |= (1ULL << (63 - 61));
        }
        else if (movingPiece == k) // Black Kingside
        {
            // Move rook from h8 (7) to f8 (5)
            pieceBitboards[static_cast<size_t>(r)] &= ~(1ULL << (63 - 7));
            pieceBitboards[static_cast<size_t>(r)] |= (1ULL << (63 - 5));
        }
    }
    else if (flag == Move::QUEEN_CASTLE)
    {
        if (movingPiece == K) // White Queenside
        {
            // Move rook from a1 (56) to d1 (59)
            pieceBitboards[static_cast<size_t>(R)] &= ~(1ULL << (63 - 56));
            pieceBitboards[static_cast<size_t>(R)] |= (1ULL << (63 - 59));
        }
        else if (movingPiece == k) // Black Queenside
        {
            // Move rook from a8 (0) to d8 (3)
            pieceBitboards[static_cast<size_t>(r)] &= ~(1ULL << (63 - 0));
            pieceBitboards[static_cast<size_t>(r)] |= (1ULL << (63 - 3));
        }
    }
    
    // 4. Update Castling rights flags on king/rook movements
    if (movingPiece == K) casstle &= ~3; // Remove white castle rights
    else if (movingPiece == k) casstle &= ~12; // Remove black castle rights
    
    if (from == h1 || to == h1) casstle &= ~1; // WK
    if (from == a1 || to == a1) casstle &= ~2; // WQ
    if (from == h8 || to == h8) casstle &= ~4; // BK
    if (from == a8 || to == a8) casstle &= ~8; // BQ
    
    // 5. Update En Passant target squares
    if (flag == Move::DOUBLE_PAWN_PUSH)
    {
        enPassant = static_cast<Square>(static_cast<int>(to) + (movingPiece == P ? 8 : -8));
    }
    else
    {
        enPassant = NO_SQUARE;
    }
    
    // 6. Toggle active turn side
    turn = (turn == WHITE) ? BLACK : WHITE;
    
    updateOccupancies();
}

} // namespace Bluie