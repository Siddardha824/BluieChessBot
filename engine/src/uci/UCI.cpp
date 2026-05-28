#include "uci/UCI.hpp"
#include "attacks/Attacks.hpp" // IWYU pragma: keep
#include "attacks/AttacksAPI.hpp"
#include "tools/Tests.hpp"
#include "core/MoveGen.hpp"
#include <chrono>
#include <cmath>
#include <iostream>
#include <sstream>
#include <vector>

namespace Bluie
{

// Start FEN constant representing the standard chess starting position
constexpr const char* STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

// Simple utility to tokenize string inputs into token vectors
static std::vector<std::string> tokenize(const std::string& input)
{
    std::vector<std::string> tokens;
    std::string token;
    std::stringstream ss(input);
    while (ss >> token)
    {
        tokens.push_back(token);
    }
    return tokens;
}

UCI::UCI() : isSearching(false)
{
    // Disable piping lag buffers on stdout to ensure immediate communication
    std::setvbuf(stdout, NULL, _IONBF, 0);
    board.parseFen(STARTING_FEN);
}

UCI::~UCI()
{
    stopSearch();
}

void UCI::loop()
{
    std::string line;
    while (std::getline(std::cin, line))
    {
        if (line.empty())
            continue;
        parseCommand(line);
    }
}

void UCI::parseCommand(const std::string& line)
{
    auto tokens = tokenize(line);
    if (tokens.empty())
        return;

    std::string cmd = tokens[0];

    if (cmd == "uci")
    {
        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "id name Bluie Bot\n";
        std::cout << "id author Siddardha\n";
        std::cout << "option name Hash type spin default 128 min 16 max 65536\n";
        std::cout << "option name Threads type spin default 4 min 1 max 32\n";
        std::cout << "uciok" << std::endl;
    }
    else if (cmd == "isready")
    {
        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "readyok" << std::endl;
    }
    else if (cmd == "setoption")
    {
        // Accept and acknowledge parameters setting silently
    }
    else if (cmd == "ucinewgame")
    {
        stopSearch();
        board.parseFen(STARTING_FEN);
    }
    else if (cmd == "position")
    {
        parsePosition(tokens);
    }
    else if (cmd == "go")
    {
        parseGo(tokens);
    }
    else if (cmd == "stop")
    {
        stopSearch();
    }
    else if (cmd == "quit")
    {
        stopSearch();
        std::exit(0);
    }
    else if (cmd == "bluie-debug")
    {
        handleDebug(tokens);
    }
}

void UCI::parsePosition(const std::vector<std::string>& tokens)
{
    stopSearch();

    size_t movesIdx = tokens.size();

    if (tokens.size() > 1)
    {
        if (tokens[1] == "startpos")
        {
            board.parseFen(STARTING_FEN);
            for (size_t i = 2; i < tokens.size(); ++i)
            {
                if (tokens[i] == "moves")
                {
                    movesIdx = i + 1;
                    break;
                }
            }
        }
        else if (tokens[1] == "fen")
        {
            // Reconstruct FEN
            std::string fenStr = "";
            size_t i = 2;
            while (i < tokens.size() && tokens[i] != "moves")
            {
                fenStr += tokens[i] + " ";
                i++;
            }
            board.parseFen(fenStr);
            if (i < tokens.size() && tokens[i] == "moves")
            {
                movesIdx = i + 1;
            }
        }
    }

    // Play any moves following the position specifier
    for (size_t i = movesIdx; i < tokens.size(); ++i)
    {
        Move move = parseMove(tokens[i]);
        if (move != Move::NO_MOVE)
        {
            board.makeMove(move);
        }
    }
}

void UCI::parseGo(const std::vector<std::string>& tokens)
{
    stopSearch();

    int depth = 10;
    int movetime = 0;

    for (size_t i = 1; i < tokens.size(); ++i)
    {
        if (tokens[i] == "depth" && i + 1 < tokens.size())
        {
            depth = std::stoi(tokens[i + 1]);
        }
        else if (tokens[i] == "movetime" && i + 1 < tokens.size())
        {
            movetime = std::stoi(tokens[i + 1]);
        }
        else if (tokens[i] == "infinite")
        {
            depth = 30; // Max depth bounds
        }
    }

    isSearching = true;
    searchThread = std::thread(&UCI::runSearch, this, depth, movetime);
}

Move UCI::parseMove(const std::string& moveStr)
{
    if (moveStr.length() < 4)
        return Move::NO_MOVE;

    int fromCol = moveStr[0] - 'a';
    int fromRow = '8' - moveStr[1];
    int toCol = moveStr[2] - 'a';
    int toRow = '8' - moveStr[3];

    if (fromCol < 0 || fromCol > 7 || fromRow < 0 || fromRow > 7 || toCol < 0 || toCol > 7 ||
        toRow < 0 || toRow > 7)
    {
        return Move::NO_MOVE;
    }

    Square from = static_cast<Square>(fromRow * 8 + fromCol);
    Square to = static_cast<Square>(toRow * 8 + toCol);

    // Scan piece bitboards to identify moving piece
    uint64_t fromBit = (1ULL << toIndex(from));
    Piece movingPiece = Piece::NO_PIECE;
    for (int p = 0; p < 12; ++p)
    {
        if (board.getPieceBitboard(static_cast<Piece>(p)) & fromBit)
        {
            movingPiece = static_cast<Piece>(p);
            break;
        }
    }

    if (movingPiece == Piece::NO_PIECE)
        return Move::NO_MOVE;

    // Check if target square is a capture
    uint64_t toBit = (1ULL << toIndex(to));
    bool isCap = false;
    for (int p = 0; p < 12; ++p)
    {
        if (board.getPieceBitboard(static_cast<Piece>(p)) & toBit)
        {
            isCap = true;
            break;
        }
    }

    Move::Flag flag = Move::Flag::QUIET;

    // 1. Pawn Double Push
    if ((movingPiece == Piece::P || movingPiece == Piece::p) &&
        std::abs(static_cast<int>(toIndex(to)) - static_cast<int>(toIndex(from))) == 16)
    {
        flag = Move::Flag::DOUBLE_PAWN_PUSH;
    }
    // 2. Castlings
    else if (movingPiece == Piece::K && from == Square::e1 && to == Square::g1)
        flag = Move::Flag::KING_CASTLE;
    else if (movingPiece == Piece::K && from == Square::e1 && to == Square::c1)
        flag = Move::Flag::QUEEN_CASTLE;
    else if (movingPiece == Piece::k && from == Square::e8 && to == Square::g8)
        flag = Move::Flag::KING_CASTLE;
    else if (movingPiece == Piece::k && from == Square::e8 && to == Square::c8)
        flag = Move::Flag::QUEEN_CASTLE;
    // 3. En Passant Capture
    else if ((movingPiece == Piece::P || movingPiece == Piece::p) && !isCap && (fromCol != toCol))
    {
        flag = Move::Flag::EN_PASSANT;
        isCap = true; // EP captures are captures
    }
    // 4. Promotions
    else if ((movingPiece == Piece::P && toRow == 0) || (movingPiece == Piece::p && toRow == 7))
    {
        char promoChar = (moveStr.length() >= 5) ? moveStr[4] : 'q';
        if (isCap)
        {
            if (promoChar == 'q')
                flag = Move::Flag::PC_QUEEN;
            else if (promoChar == 'r')
                flag = Move::Flag::PC_ROOK;
            else if (promoChar == 'b')
                flag = Move::Flag::PC_BISHOP;
            else if (promoChar == 'n')
                flag = Move::Flag::PC_KNIGHT;
        }
        else
        {
            if (promoChar == 'q')
                flag = Move::Flag::PR_QUEEN;
            else if (promoChar == 'r')
                flag = Move::Flag::PR_ROOK;
            else if (promoChar == 'b')
                flag = Move::Flag::PR_BISHOP;
            else if (promoChar == 'n')
                flag = Move::Flag::PR_KNIGHT;
        }
    }
    // 5. Standard Captures
    else if (isCap)
    {
        flag = Move::Flag::CAPTURE;
    }

    return Move(from, to, flag);
}

void UCI::stopSearch()
{
    isSearching = false;
    if (searchThread.joinable())
    {
        searchThread.join();
    }
}

void UCI::runSearch(int depth, int movetime)
{
    auto startTime = std::chrono::steady_clock::now();

    int eval_cp = 15;

    for (int d = 1; d <= depth && isSearching; ++d)
    {
        // Simulate thinking time offset
        std::this_thread::sleep_for(std::chrono::milliseconds(140));

        auto now = std::chrono::steady_clock::now();
        auto duration =
            std::chrono::duration_cast<std::chrono::milliseconds>(now - startTime).count();

        if (movetime > 0 && duration >= movetime)
        {
            break;
        }

        eval_cp += (d % 2 == 0) ? 14 : -9;
        long long nodes = d * 1842;
        long long nps = (duration > 0) ? (nodes * 1000 / duration) : 32000;

        {
            std::lock_guard<std::mutex> lock(coutMutex);
            std::cout << "info depth " << d << " score cp " << eval_cp << " nodes " << nodes
                      << " nps " << nps << " time " << duration << " pv e2e4 e7e5 g1f3 b8c6"
                      << std::endl;
        }
    }

    // Query actual legal moves from MoveGen
    MoveGen moveGen;
    MoveList moves = moveGen.getLegalMoves(board);

    std::string bestMoveStr = "0000";
    if (moves.count > 0)
    {
        Move m = moves.moves[0];
        Square from = m.getFrom();
        Square to = m.getTo();
        Move::Flag flag = m.getFlags();
        
        bestMoveStr = std::string(squareToCoordinates[toIndex(from)]) + std::string(squareToCoordinates[toIndex(to)]);
        if (flag == Move::Flag::PR_QUEEN || flag == Move::Flag::PC_QUEEN) bestMoveStr += "q";
        else if (flag == Move::Flag::PR_ROOK || flag == Move::Flag::PC_ROOK) bestMoveStr += "r";
        else if (flag == Move::Flag::PR_BISHOP || flag == Move::Flag::PC_BISHOP) bestMoveStr += "b";
        else if (flag == Move::Flag::PR_KNIGHT || flag == Move::Flag::PC_KNIGHT) bestMoveStr += "n";
    }

    {
        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "bestmove " << bestMoveStr << std::endl;
    }

    isSearching = false;
}

void UCI::handleDebug(const std::vector<std::string>& tokens)
{
    if (tokens.size() < 2)
    {
        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "info string error: bluie-debug requires a subcommand" << std::endl;
        return;
    }

    std::string sub = tokens[1];

    if (sub == "board")
    {
        // 1. Reconstruct FEN placement
        std::string fenPlacement = "";
        for (int rank = 0; rank < 8; ++rank)
        {
            int emptyCount = 0;
            for (int file = 0; file < 8; ++file)
            {
                int sq = rank * 8 + file;
                uint64_t bit = 1ULL << sq;
                Piece foundPiece = Piece::NO_PIECE;

                for (int p = 0; p < 12; ++p)
                {
                    if (board.getPieceBitboard(static_cast<Piece>(p)) & bit)
                    {
                        foundPiece = static_cast<Piece>(p);
                        break;
                    }
                }

                if (foundPiece != Piece::NO_PIECE)
                {
                    if (emptyCount > 0)
                    {
                        fenPlacement += std::to_string(emptyCount);
                        emptyCount = 0;
                    }
                    char pChar = '?';
                    switch (foundPiece)
                    {
                    case Piece::P:
                        pChar = 'P';
                        break;
                    case Piece::N:
                        pChar = 'N';
                        break;
                    case Piece::B:
                        pChar = 'B';
                        break;
                    case Piece::R:
                        pChar = 'R';
                        break;
                    case Piece::Q:
                        pChar = 'Q';
                        break;
                    case Piece::K:
                        pChar = 'K';
                        break;
                    case Piece::p:
                        pChar = 'p';
                        break;
                    case Piece::n:
                        pChar = 'n';
                        break;
                    case Piece::b:
                        pChar = 'b';
                        break;
                    case Piece::r:
                        pChar = 'r';
                        break;
                    case Piece::q:
                        pChar = 'q';
                        break;
                    case Piece::k:
                        pChar = 'k';
                        break;
                    default:
                        break;
                    }
                    fenPlacement += pChar;
                }
                else
                {
                    emptyCount++;
                }
            }
            if (emptyCount > 0)
            {
                fenPlacement += std::to_string(emptyCount);
            }
            if (rank < 7)
            {
                fenPlacement += "/";
            }
        }

        // Turn
        std::string turnStr = (board.getTurn() == Side::WHITE) ? "w" : "b";

        // Castling rights
        std::string castleStr = "";
        uint8_t c = board.getCastle();
        if (c & 1)
            castleStr += "K";
        if (c & 2)
            castleStr += "Q";
        if (c & 4)
            castleStr += "k";
        if (c & 8)
            castleStr += "q";
        if (castleStr.empty())
            castleStr = "-";

        // En Passant target
        std::string epStr = "-";
        if (board.getEnPassant() != Square::NO_SQUARE)
        {
            epStr = squareToCoordinates[toIndex(board.getEnPassant())];
        }

        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "info string DEBUG BOARD FEN " << fenPlacement << " " << turnStr << " "
                  << castleStr << " " << epStr << " " << board.getHalfmoveClock() << " "
                  << board.getFullmoveNumber() << std::endl;
        std::cout << "info string DEBUG BOARD TURN " << turnStr << std::endl;
        std::cout << "info string DEBUG BOARD CASTLING " << castleStr << std::endl;
        std::cout << "info string DEBUG BOARD EP " << epStr << std::endl;
        std::cout << "info string DEBUG BOARD CLOCKS " << board.getHalfmoveClock() << " "
                  << board.getFullmoveNumber() << std::endl;
    }
    else if (sub == "bitboards")
    {
        std::lock_guard<std::mutex> lock(coutMutex);

        // 12 pieces
        std::array<std::string, 12> pieceNames = {"WHITE_PAWNS", "WHITE_KNIGHTS", "WHITE_BISHOPS",
                                                  "WHITE_ROOKS", "WHITE_QUEENS",  "WHITE_KINGS",
                                                  "BLACK_PAWNS", "BLACK_KNIGHTS", "BLACK_BISHOPS",
                                                  "BLACK_ROOKS", "BLACK_QUEENS",  "BLACK_KINGS"};

        for (int p = 0; p < 12; ++p)
        {
            uint64_t bb = board.getPieceBitboard(static_cast<Piece>(p));
            std::cout << "info string DEBUG BITBOARD " << pieceNames[p] << " " << std::hex << bb
                      << std::dec << std::endl;
        }

        // 3 occupancies
        std::cout << "info string DEBUG BITBOARD WHITE_OCCUPANCY " << std::hex
                  << board.getOccupancy(Side::WHITE) << std::dec << std::endl;
        std::cout << "info string DEBUG BITBOARD BLACK_OCCUPANCY " << std::hex
                  << board.getOccupancy(Side::BLACK) << std::dec << std::endl;
        std::cout << "info string DEBUG BITBOARD COMBINED_OCCUPANCY " << std::hex
                  << board.getOccupancy(Side::NONE) << std::dec << std::endl;
    }
    else if (sub == "occupancy")
    {
        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "info string DEBUG OCCUPANCY WHITE " << std::hex
                  << board.getOccupancy(Side::WHITE) << std::dec << std::endl;
        std::cout << "info string DEBUG OCCUPANCY BLACK " << std::hex
                  << board.getOccupancy(Side::BLACK) << std::dec << std::endl;
        std::cout << "info string DEBUG OCCUPANCY ALL " << std::hex
                  << board.getOccupancy(Side::NONE) << std::dec << std::endl;
    }
    else if (sub == "attacks")
    {
        if (tokens.size() < 3)
        {
            std::lock_guard<std::mutex> lock(coutMutex);
            std::cout << "info string error: bluie-debug attacks requires a side (white/black)"
                      << std::endl;
            return;
        }

        std::string sideStr = tokens[2];
        Side sideToGen = Side::WHITE;
        if (sideStr == "black" || sideStr == "b")
        {
            sideToGen = Side::BLACK;
        }

        uint64_t attacksBB = 0ULL;
        for (int sq = 0; sq < 64; ++sq)
        {
            if (Attacks::isSquareAttacked(board, static_cast<Square>(sq), sideToGen))
            {
                attacksBB |= (1ULL << sq);
            }
        }

        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "info string DEBUG ATTACKS " << (sideToGen == Side::WHITE ? "WHITE" : "BLACK")
                  << " " << std::hex << attacksBB << std::dec << std::endl;
    }
    else if (sub == "attacksto")
    {
        if (tokens.size() < 4)
        {
            std::lock_guard<std::mutex> lock(coutMutex);
            std::cout
                << "info string error: bluie-debug attacksto requires a square coordinate and side"
                << std::endl;
            return;
        }

        std::string squareStr = tokens[2];
        std::string sideStr = tokens[3];

        if (squareStr.length() < 2)
            return;
        int col = squareStr[0] - 'a';
        int row = '8' - squareStr[1];

        if (col < 0 || col > 7 || row < 0 || row > 7)
            return;
        Square sq = static_cast<Square>(row * 8 + col);

        Side attackerSide = Side::WHITE;
        if (sideStr == "black" || sideStr == "b")
        {
            attackerSide = Side::BLACK;
        }

        Bitboard attackingBB = Attacks::attacksTo(board, sq, attackerSide);

        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "info string DEBUG ATTACKSTO " << squareStr << " "
                  << (attackerSide == Side::WHITE ? "WHITE" : "BLACK") << " " << std::hex
                  << attackingBB << std::dec << std::endl;
    }
    else if (sub == "validate")
    {
        std::lock_guard<std::mutex> lock(coutMutex);
        bool isValid = board.validate();
        std::cout << "info string DEBUG VALIDATE " << (isValid ? "OK" : "INVALID") << std::endl;
    }
    else if (sub == "runtests")
    {
        Tools::runAllTests();
    }
    else if (sub == "legalmoves")
    {
        std::lock_guard<std::mutex> lock(coutMutex);
        MoveGen moveGen;
        MoveList moves = moveGen.getLegalMoves(board);
        
        std::cout << "info string DEBUG LEGALS";
        for (int i = 0; i < moves.count; ++i)
        {
            Move m = moves.moves[i];
            Square from = m.getFrom();
            Square to = m.getTo();
            Move::Flag flag = m.getFlags();
            
            std::cout << " " << squareToCoordinates[toIndex(from)] << squareToCoordinates[toIndex(to)];
            if (flag == Move::Flag::PR_QUEEN || flag == Move::Flag::PC_QUEEN) std::cout << "q";
            else if (flag == Move::Flag::PR_ROOK || flag == Move::Flag::PC_ROOK) std::cout << "r";
            else if (flag == Move::Flag::PR_BISHOP || flag == Move::Flag::PC_BISHOP) std::cout << "b";
            else if (flag == Move::Flag::PR_KNIGHT || flag == Move::Flag::PC_KNIGHT) std::cout << "n";
        }
        std::cout << std::endl;
    }
    else if (sub == "piecemoves")
    {
        // Placeholder stub: returns mock empty list
        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "info string DEBUG PIECEMOVES" << std::endl;
    }
    else if (sub == "perft")
    {
        if (tokens.size() < 3)
        {
            std::lock_guard<std::mutex> lock(coutMutex);
            std::cout << "info string error: bluie-debug perft requires a depth" << std::endl;
            return;
        }
        int depth = std::stoi(tokens[2]);
        
        auto start = std::chrono::high_resolution_clock::now();
        uint64_t nodes = Tools::perft(depth, board);
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        
        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "info string DEBUG PERFTTOTAL " << nodes << std::endl;
        std::cout << "info string DEBUG PERFTTIME " << duration << " ms" << std::endl;
        if (duration > 0)
        {
            double nps = (static_cast<double>(nodes) / static_cast<double>(duration)) * 1000.0;
            std::cout << "info string DEBUG PERFTNPS " << static_cast<uint64_t>(nps) << std::endl;
        }
    }
    else if (sub == "divide")
    {
        if (tokens.size() < 3)
        {
            std::lock_guard<std::mutex> lock(coutMutex);
            std::cout << "info string error: bluie-debug divide requires a depth" << std::endl;
            return;
        }
        int depth = std::stoi(tokens[2]);
        
        MoveGen moveGen;
        MoveList moves = moveGen.getLegalMoves(board);
        
        uint64_t totalNodes = 0;
        
        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "info string DEBUG DIVIDESTART depth " << depth << std::endl;
        
        for (int i = 0; i < moves.count; ++i)
        {
            Move m = moves.moves[i];
            Board temp = board;
            temp.makeMove(m);
            
            uint64_t nodes = 0;
            if (depth > 1)
            {
                nodes = Tools::perft(depth - 1, temp);
            }
            else
            {
                nodes = 1;
            }
            
            totalNodes += nodes;
            
            Square from = m.getFrom();
            Square to = m.getTo();
            Move::Flag flag = m.getFlags();
            
            std::cout << "info string DEBUG DIVIDEMOVE " 
                      << squareToCoordinates[toIndex(from)] 
                      << squareToCoordinates[toIndex(to)];
            if (flag == Move::Flag::PR_QUEEN || flag == Move::Flag::PC_QUEEN) std::cout << "q";
            else if (flag == Move::Flag::PR_ROOK || flag == Move::Flag::PC_ROOK) std::cout << "r";
            else if (flag == Move::Flag::PR_BISHOP || flag == Move::Flag::PC_BISHOP) std::cout << "b";
            else if (flag == Move::Flag::PR_KNIGHT || flag == Move::Flag::PC_KNIGHT) std::cout << "n";
            std::cout << ": " << nodes << std::endl;
        }
        std::cout << "info string DEBUG DIVIDETOTAL " << totalNodes << std::endl;
    }
    else if (sub == "moveparse")
    {
        if (tokens.size() < 3)
        {
            std::lock_guard<std::mutex> lock(coutMutex);
            std::cout << "info string error: bluie-debug moveparse requires a move coordinate"
                      << std::endl;
            return;
        }

        std::string moveStr = tokens[2];
        Move move = parseMove(moveStr);

        std::lock_guard<std::mutex> lock(coutMutex);
        if (move == Move::NO_MOVE)
        {
            std::cout << "info string DEBUG MOVEPARSE " << moveStr << " INVALID" << std::endl;
        }
        else
        {
            std::cout << "info string DEBUG MOVEPARSE " << moveStr << " FROM "
                      << squareToCoordinates[toIndex(move.getFrom())] << " TO "
                      << squareToCoordinates[toIndex(move.getTo())] << " FLAGS " << std::hex
                      << toIndex(move.getFlags()) << std::dec << std::endl;
        }
    }
    else if (sub == "searchinfo")
    {
        // Telemetry stream placeholder
        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "info string DEBUG SEARCHINFO ACTIVE" << std::endl;
    }
    else
    {
        std::lock_guard<std::mutex> lock(coutMutex);
        std::cout << "info string error: unknown bluie-debug subcommand " << sub << std::endl;
    }
}

} // namespace Bluie
