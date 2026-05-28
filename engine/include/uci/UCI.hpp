#pragma once

#include "board/Board.hpp"
#include <atomic>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

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
     * @brief Parses custom debug commands prefixed with 'bluie-debug'.
     */
    void handleDebug(const std::vector<std::string>& tokens);

    /**
     * @brief Executes multi-threaded search benchmark.
     */
    void handleBench(const std::vector<std::string>& tokens);

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

    Board board;                   ///< The active chess board position state
    std::atomic<bool> isSearching; ///< Atomic flag indicating active calculation state
    std::thread searchThread;      ///< Thread handle for asynchronous calculations
    std::mutex coutMutex;          ///< Mutex guarding standard output stream prints
    int hashSizeMB;                ///< Transposition table allocation size in megabytes
    int numThreads;                ///< Number of search calculation threads
};

} // namespace Bluie
