#pragma once

#include "board/Board.hpp"
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <mutex>

namespace Bluie
{

/**
 * @class UCI
 * @brief Universal Chess Interface (UCI) protocol controller for the C++ engine.
 * 
 * Manages asynchronous standard stream parsing and routes communications
 * between standard input command queues and calculation threads.
 */
class UCI
{
public:
    /**
     * @brief Constructor. Initializes handshake state and atomic status.
     */
    UCI();

    /**
     * @brief Destructor. Aborts search threads safely before exit.
     */
    ~UCI();

    /**
     * @brief The infinite main command loop reading lines from standard input (cin).
     */
    void loop();

private:
    /**
     * @brief Decodes a single command line text.
     */
    void parseCommand(const std::string& line);

    /**
     * @brief Parses position strings (e.g. 'position startpos moves e2e4...').
     */
    void parsePosition(const std::vector<std::string>& tokens);

    /**
     * @brief Parses search bounds and spawns the calculation thread.
     */
    void parseGo(const std::vector<std::string>& tokens);

    /**
     * @brief Translates text coordinates (e.g. 'e2e4') into binary packed Move objects.
     */
    Move parseMove(const std::string& moveStr);

    /**
     * @brief Aborts active calculation thread search operations reactively.
     */
    void stopSearch();

    /**
     * @brief Search calculation runner loop executed in the background thread.
     */
    void runSearch(int depth, int movetime);

    Board board;                    ///< The active chess board position state
    std::atomic<bool> isSearching; ///< Atomic flag indicating active calculation state
    std::thread searchThread;       ///< Thread handle for asynchronous calculations
    std::mutex coutMutex;          ///< Mutex guarding standard output stream prints
};

} // namespace Bluie
