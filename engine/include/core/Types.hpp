#pragma once

#include <array>
#include <cassert>
#include <cstdint>

namespace Bluie
{

/**
 * @brief Representation of a 64-bit chessboard occupancy map (Bitboard).
 */
using Bitboard = uint64_t;

/**
 * @brief Array of 64 Bitboards, typically mapping one bitboard per square.
 */
using BitboardArray = std::array<Bitboard, 64>;

/**
 * @brief Represents the active player or side to move.
 */
enum Side
{
    NONE,  ///< Empty/No Side
    BLACK, ///< Black Side (0)
    WHITE  ///< White Side (1)
};

// clang-format off
/**
 * @brief Mapping of the 64 board squares in standard C++ chess-engine orientation (a8 = 0, h1 = 63).
 */
enum Square
{
    a8, b8, c8, d8, e8, f8, g8, h8, 
    a7, b7, c7, d7, e7, f7, g7, h7, 
    a6, b6, c6, d6, e6, f6, g6, h6, 
    a5, b5, c5, d5, e5, f5, g5, h5, 
    a4, b4, c4, d4, e4, f4, g4, h4, 
    a3, b3, c3, d3, e3, f3, g3, h3, 
    a2, b2, c2, d2, e2, f2, g2, h2, 
    a1, b1, c1, d1, e1, f1, g1, h1
};

/**
 * @brief Represents standard chess pieces. Upper case are White, lower case are Black.
 */
enum Piece 
{
    NO_PIECE,
    P, N, B, R, Q, K, ///< White Pieces (Pawn, Knight, Bishop, Rook, Queen, King)
    p, n, b, r, q, k  ///< Black Pieces (Pawn, Knight, Bishop, Rook, Queen, King)
};

/**
 * @brief Lookup table to convert standard board square indices (0-63) to UCI algebraic strings.
 */
inline constexpr std::array<const char*, 64> squareToCoordinates = 
{
    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8",
    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7",
    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1"
};
// clang-format on

/**
 * @class Move
 * @brief High-performance packed 16-bit move representation.
 * 
 * Bit layout:
 * - Bits 0-5  : Source Square (0-63)
 * - Bits 6-11 : Target Square (0-63)
 * - Bits 12-15: Move Type Flags (Quiet, Double Push, Castles, Capture, Promotion, etc.)
 */
class Move
{
public:
    /**
     * @brief Move flags representing move category, captures, and promotions.
     */
    enum Flag : uint16_t
    {
        QUIET            = 0,  ///< Quiet Move
        DOUBLE_PAWN_PUSH = 1,  ///< Double Pawn Push (2 squares)
        KING_CASTLE      = 2,  ///< Kingside Castling
        QUEEN_CASTLE     = 3,  ///< Queenside Castling
        CAPTURE          = 4,  ///< Standard Piece Capture
        EN_PASSANT       = 5,  ///< En Passant Capture
        PR_KNIGHT        = 8,  ///< Promotion to Knight
        PR_BISHOP        = 9,  ///< Promotion to Bishop
        PR_ROOK          = 10, ///< Promotion to Rook
        PR_QUEEN         = 11, ///< Promotion to Queen
        PC_KNIGHT        = 12, ///< Promotion to Knight with Capture
        PC_BISHOP        = 13, ///< Promotion to Bishop with Capture
        PC_ROOK          = 14, ///< Promotion to Rook with Capture
        PC_QUEEN         = 15  ///< Promotion to Queen with Capture
    };

    /**
     * @brief Default constructor. Initializes as an illegal/null move.
     */
    inline constexpr Move() : data(0) {}

    /**
     * @brief Constructor from a raw 16-bit value.
     */
    inline constexpr explicit Move(uint16_t rawData) : data(rawData) {}

    /**
     * @brief Constructor from source square, target square, and move flags.
     */
    inline constexpr Move(Square from, Square to, Flag flag = QUIET)
        : data(static_cast<uint16_t>(from) | 
              (static_cast<uint16_t>(to) << 6) | 
              (static_cast<uint16_t>(flag) << 12)) {}

    /**
     * @brief Extract the source square of the move.
     */
    inline constexpr Square getFrom() const { return static_cast<Square>(data & 0x3F); }

    /**
     * @brief Extract the destination square of the move.
     */
    inline constexpr Square getTo() const { return static_cast<Square>((data >> 6) & 0x3F); }

    /**
     * @brief Extract the move flag.
     */
    inline constexpr Flag getFlags() const { return static_cast<Flag>((data >> 12) & 0x0F); }

    /**
     * @brief Get the raw 16-bit value of this move.
     */
    inline constexpr uint16_t getRaw() const { return data; }

    /**
     * @brief Check if the move is a piece capture.
     */
    inline constexpr bool isCapture() const { return (data & 0x4000) != 0; }

    /**
     * @brief Check if the move is a pawn promotion.
     */
    inline constexpr bool isPromotion() const { return (data & 0x8000) != 0; }

    /**
     * @brief Check if the move is an en passant capture.
     */
    inline constexpr bool isEnPassant() const { return getFlags() == EN_PASSANT; }

    /**
     * @brief Check if the move is castling.
     */
    inline constexpr bool isCastling() const { Flag f = getFlags(); return f == KING_CASTLE || f == QUEEN_CASTLE; }

    /**
     * @brief Check if the move is a double pawn push.
     */
    inline constexpr bool isDoublePush() const { return getFlags() == DOUBLE_PAWN_PUSH; }

    /**
     * @brief Sentinel representing a null, illegal, or empty move.
     */
    static const Move NO_MOVE;

    inline constexpr bool operator==(const Move& other) const { return data == other.data; }
    inline constexpr bool operator!=(const Move& other) const { return data != other.data; }

private:
    uint16_t data; ///< Encoded move data
};

inline constexpr Move Move::NO_MOVE = Move(0);

/**
 * @brief Maximum moves that can be generated in any valid chess position.
 */
constexpr int MAX_MOVES = 256;

/**
 * @struct MoveList
 * @brief Fixed-size array-based list of generated moves to avoid dynamic allocations.
 */
struct MoveList
{
    Move moves[MAX_MOVES]; ///< Statically allocated move array
    int count = 0;         ///< Number of valid moves currently stored

    /**
     * @brief Append a move to the list.
     * @param m The move to add.
     */
    inline void add(Move m)
    {
        assert(count < MAX_MOVES);
        moves[count++] = m;
    }
};

} // namespace Bluie