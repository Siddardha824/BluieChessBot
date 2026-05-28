#include "board/Board.hpp"
#include "core/Bitboard.hpp"
#include <sstream>

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
    turn = Side::WHITE;
    enPassant = Square::NO_SQUARE;
    casstle = 0;
    halfmoveClock = 0;
    fullmoveNumber = 1;
    zobristHash = 0;
}

Bitboard Board::getPieceBitboard(Piece p) const
{
    if (p == Piece::NO_PIECE)
        return 0ULL;
    return pieceBitboards[toIndex(p)];
}

void Board::setPieceBitboard(Piece p, Bitboard bb)
{
    if (p == Piece::NO_PIECE)
        return;
    pieceBitboards[toIndex(p)] = bb;
}

Bitboard Board::getOccupancy(Side side) const
{
    if (side == Side::NONE)
        return occupancy[2]; // Combined
    return occupancy[side == Side::WHITE ? 1 : 0];
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

    if (!(ss >> placement))
        return false;

    // 1. Piece Placement parsing
    int squareIdx = 0;
    for (char c : placement)
    {
        if (c == '/')
            continue;
        if (c >= '1' && c <= '8')
        {
            squareIdx += (c - '0');
        }
        else
        {
            Piece pc = Piece::NO_PIECE;
            switch (c)
            {
            case 'P':
                pc = Piece::P;
                break;
            case 'N':
                pc = Piece::N;
                break;
            case 'B':
                pc = Piece::B;
                break;
            case 'R':
                pc = Piece::R;
                break;
            case 'Q':
                pc = Piece::Q;
                break;
            case 'K':
                pc = Piece::K;
                break;
            case 'p':
                pc = Piece::p;
                break;
            case 'n':
                pc = Piece::n;
                break;
            case 'b':
                pc = Piece::b;
                break;
            case 'r':
                pc = Piece::r;
                break;
            case 'q':
                pc = Piece::q;
                break;
            case 'k':
                pc = Piece::k;
                break;
            default:
                return false; // Invalid char
            }
            if (pc != Piece::NO_PIECE && squareIdx < 64)
            {
                // Add the bit representing pc to its bitboard
                // Note: a8 is 0, h1 is 63. The square bit starts at LSB (square index 0)
                pieceBitboards[toIndex(pc)] |= (1ULL << squareIdx);
                squareIdx++;
            }
        }
    }

    // 2. Active color
    if (ss >> activeColor)
    {
        turn = (activeColor == "w") ? Side::WHITE : Side::BLACK;
    }

    // 3. Castling rights
    if (ss >> castling)
    {
        for (char c : castling)
        {
            if (c == 'K')
                casstle |= 1; // WK
            else if (c == 'Q')
                casstle |= 2; // WQ
            else if (c == 'k')
                casstle |= 4; // BK
            else if (c == 'q')
                casstle |= 8; // BQ
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

    // 5. Halfmove clock
    if (ss >> halfmove)
    {
        halfmoveClock = std::stoi(halfmove);
    }

    // 6. Fullmove number
    if (ss >> fullmove)
    {
        fullmoveNumber = std::stoi(fullmove);
    }

    updateOccupancies();
    return true;
}

void Board::makeMove(Move move)
{
    Square from = move.getFrom();
    Square to = move.getTo();
    Move::Flag flag = move.getFlags();

    uint64_t fromBit = (1ULL << toIndex(from));
    uint64_t toBit = (1ULL << toIndex(to));

    // Find the piece that is moving
    Piece movingPiece = Piece::NO_PIECE;
    for (int p = 0; p < 12; ++p)
    {
        if (pieceBitboards[p] & fromBit)
        {
            movingPiece = static_cast<Piece>(p);
            break;
        }
    }

    if (movingPiece == Piece::NO_PIECE)
        return; // Illegal moving piece

    // 1. Handle capturing (if capture flag or standard capture)
    if (move.isCapture())
    {
        Square captureSq = to;

        // Handle En Passant capture target square (it captures the pawn behind the target square)
        if (flag == Move::Flag::EN_PASSANT)
        {
            captureSq = static_cast<Square>(toIndex(to) + (movingPiece == Piece::P ? 8 : -8));
        }

        uint64_t capBit = (1ULL << toIndex(captureSq));

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
    pieceBitboards[toIndex(movingPiece)] &= ~fromBit;

    if (move.isPromotion())
    {
        // Replace with promoted piece
        Piece promotedPiece = Piece::NO_PIECE;
        switch (flag)
        {
        case Move::Flag::PR_KNIGHT:
        case Move::Flag::PC_KNIGHT:
            promotedPiece = (movingPiece == Piece::P) ? Piece::N : Piece::n;
            break;
        case Move::Flag::PR_BISHOP:
        case Move::Flag::PC_BISHOP:
            promotedPiece = (movingPiece == Piece::P) ? Piece::B : Piece::b;
            break;
        case Move::Flag::PR_ROOK:
        case Move::Flag::PC_ROOK:
            promotedPiece = (movingPiece == Piece::P) ? Piece::R : Piece::r;
            break;
        case Move::Flag::PR_QUEEN:
        case Move::Flag::PC_QUEEN:
            promotedPiece = (movingPiece == Piece::P) ? Piece::Q : Piece::q;
            break;
        default:
            promotedPiece = (movingPiece == Piece::P) ? Piece::Q : Piece::q;
            break;
        }
        pieceBitboards[toIndex(promotedPiece)] |= toBit;
    }
    else
    {
        pieceBitboards[toIndex(movingPiece)] |= toBit;
    }

    // 3. Handle Castling rook movements
    if (flag == Move::Flag::KING_CASTLE)
    {
        if (movingPiece == Piece::K) // White Kingside
        {
            // Move rook from h1 (63) to f1 (61)
            pieceBitboards[toIndex(Piece::R)] &= ~(1ULL << 63);
            pieceBitboards[toIndex(Piece::R)] |= (1ULL << 61);
        }
        else if (movingPiece == Piece::k) // Black Kingside
        {
            // Move rook from h8 (7) to f8 (5)
            pieceBitboards[toIndex(Piece::r)] &= ~(1ULL << 7);
            pieceBitboards[toIndex(Piece::r)] |= (1ULL << 5);
        }
    }
    else if (flag == Move::Flag::QUEEN_CASTLE)
    {
        if (movingPiece == Piece::K) // White Queenside
        {
            // Move rook from a1 (56) to d1 (59)
            pieceBitboards[toIndex(Piece::R)] &= ~(1ULL << 56);
            pieceBitboards[toIndex(Piece::R)] |= (1ULL << 59);
        }
        else if (movingPiece == Piece::k) // Black Queenside
        {
            // Move rook from a8 (0) to d8 (3)
            pieceBitboards[toIndex(Piece::r)] &= ~(1ULL << 0);
            pieceBitboards[toIndex(Piece::r)] |= (1ULL << 3);
        }
    }

    // 4. Update Castling rights flags on king/rook movements
    if (movingPiece == Piece::K)
        casstle &= ~3; // Remove white castle rights
    else if (movingPiece == Piece::k)
        casstle &= ~12; // Remove black castle rights

    if (from == Square::h1 || to == Square::h1)
        casstle &= ~1; // WK
    if (from == Square::a1 || to == Square::a1)
        casstle &= ~2; // WQ
    if (from == Square::h8 || to == Square::h8)
        casstle &= ~4; // BK
    if (from == Square::a8 || to == Square::a8)
        casstle &= ~8; // BQ

    // 5. Update En Passant target squares
    if (flag == Move::Flag::DOUBLE_PAWN_PUSH)
    {
        enPassant = static_cast<Square>(toIndex(to) + (movingPiece == Piece::P ? 8 : -8));
    }
    else
    {
        enPassant = Square::NO_SQUARE;
    }

    // 6. Toggle active turn side
    turn = (turn == Side::WHITE) ? Side::BLACK : Side::WHITE;

    updateOccupancies();
}

bool Board::validate() const
{
    // 1. Exactly one White King and exactly one Black King
    if (Bitboards::countBits(pieceBitboards[toIndex(Piece::K)]) != 1)
        return false;
    if (Bitboards::countBits(pieceBitboards[toIndex(Piece::k)]) != 1)
        return false;

    // 2. Overlapping pieces
    Bitboard occupied = 0ULL;
    for (int p = 0; p < 12; ++p)
    {
        if (occupied & pieceBitboards[p])
            return false; // Overlap detected
        occupied |= pieceBitboards[p];
    }

    // 3. Occupancy consistency
    Bitboard whiteOcc = 0ULL;
    for (int p = 0; p < 6; ++p)
        whiteOcc |= pieceBitboards[p];
    Bitboard blackOcc = 0ULL;
    for (int p = 6; p < 12; ++p)
        blackOcc |= pieceBitboards[p];

    if (occupancy[1] != whiteOcc)
        return false;
    if (occupancy[0] != blackOcc)
        return false;
    if (occupancy[2] != (whiteOcc | blackOcc))
        return false;

    // 4. En Passant legality
    if (enPassant != Square::NO_SQUARE)
    {
        int epIdx = toIndex(enPassant);
        int rank = epIdx / 8;
        if (rank != 2 && rank != 5)
            return false;
    }

    // 5. Castling legality
    if (casstle & 1) // WK
    {
        if (!(pieceBitboards[toIndex(Piece::K)] & (1ULL << 60)))
            return false;
        if (!(pieceBitboards[toIndex(Piece::R)] & (1ULL << 63)))
            return false;
    }
    if (casstle & 2) // WQ
    {
        if (!(pieceBitboards[toIndex(Piece::K)] & (1ULL << 60)))
            return false;
        if (!(pieceBitboards[toIndex(Piece::R)] & (1ULL << 56)))
            return false;
    }
    if (casstle & 4) // BK
    {
        if (!(pieceBitboards[toIndex(Piece::k)] & (1ULL << 4)))
            return false;
        if (!(pieceBitboards[toIndex(Piece::r)] & (1ULL << 7)))
            return false;
    }
    if (casstle & 8) // BQ
    {
        if (!(pieceBitboards[toIndex(Piece::k)] & (1ULL << 4)))
            return false;
        if (!(pieceBitboards[toIndex(Piece::r)] & (1ULL << 0)))
            return false;
    }

    return true;
}

} // namespace Bluie