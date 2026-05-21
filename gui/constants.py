# Constants and Configurations for C++ Chess Bot Debugger & UCI GUI

PIECE_CHARS = {
    'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟', # Black (viewed from standard perspective or engine side)
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R_white': '♖', 'N_white': '♘', 'B_white': '♗', 'Q_white': '♕', 'K_white': '♔', 'P_white': '♙',
}

DEFAULT_BOARD = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
]

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# Themes configuration for fully changing board & frame styles
BOARD_THEMES = {
    "Classic Emerald": {
        "light": "#F0D9B5", "dark": "#B58863", "select": "#BACA2B", "last_move": "#CD9A62",
        "bg_dark": "#0f172a", "bg_mid": "#1e293b", "fg": "#e2e8f0", "accent": "#3b82f6",
        "piece_white": "#f8fafc", "piece_black": "#1e293b"
    },
    "Deep Velvet": {
        "light": "#EAE8E8", "dark": "#6A5ACD", "select": "#FFD700", "last_move": "#BA55D3",
        "bg_dark": "#121214", "bg_mid": "#1D1D24", "fg": "#F5F5F7", "accent": "#8A2BE2",
        "piece_white": "#ffffff", "piece_black": "#110933"
    },
    "Nordic Ice": {
        "light": "#E5E9F0", "dark": "#4C566A", "select": "#A3BE8C", "last_move": "#81A1C1",
        "bg_dark": "#2E3440", "bg_mid": "#3B4252", "fg": "#D8DEE9", "accent": "#88C0D0",
        "piece_white": "#ECEFF4", "piece_black": "#2E3440"
    },
    "High Contrast Dark": {
        "light": "#ffffff", "dark": "#2a2d34", "select": "#FFEB3B", "last_move": "#76c7c0",
        "bg_dark": "#0B0C10", "bg_mid": "#1F2833", "fg": "#C5C6C7", "accent": "#66FCF1",
        "piece_white": "#00ff00", "piece_black": "#ff003c"
    },
    "Bluie Teal": {
        "light": "#B5E6E6", "dark": "#539797", "select": "#FCD34D", "last_move": "#A7F3D0",
        "bg_dark": "#0B132B", "bg_mid": "#1C2541", "fg": "#E2E8F0", "accent": "#48CAE4",
        "piece_white": "#FFFFFF", "piece_black": "#0B132B"
    }
}

CPP_TEMPLATE_CODE = """/**
 * C++ Chess Bot UCI Starter Template
 * ---------------------------------
 * A structured starter program for building a performance-oriented C++ chess bot.
 * Out-of-the-box handles standard I/O streams and asynchronous search termination tags.
 *
 * Compilation command:
 *   g++ -O3 -std=c++17 bot_template.cpp -o my_chess_bot
 */

#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <thread>
#include <atomic>
#include <mutex>

// State controls for search execution
std::atomic<bool> is_searching{false};
std::thread search_thread;
std::mutex cout_mutex;

// Dummy implementation of engine statistics
void run_search(int depth) {
    is_searching = true;
    
    // Simple iterative deepening evaluation dummy logic
    for (int d = 1; d <= depth && is_searching; ++d) {
        // Mock evaluation scores
        int eval_cp = 18 + d * 5; 
        long long nodes = d * 1824;
        long long nps = 36000;
        
        {
            std::lock_guard<std::mutex> lock(cout_mutex);
            // standard engine info search structure
            std::cout << "info depth " << d 
                      << " score cp " << eval_cp 
                      << " nodes " << nodes 
                      << " nps " << nps 
                      << " pv e2e4 e7e5 g1f3" << std::endl;
        }
        
        // Simulating search processing load
        std::this_thread::sleep_for(std::chrono::milliseconds(150));
    }

    if (is_searching) {
        std::lock_guard<std::mutex> lock(cout_mutex);
        std::cout << "bestmove e2e4" << std::endl;
    }
    is_searching = false;
}

// Splits strings into clean coordinate vectors
std::vector<std::string> tokenize(const std::string& input) {
    std::vector<std::string> tokens;
    std::string token;
    std::stringstream ss(input);
    while (ss >> token) {
        tokens.push_back(token);
    }
    return tokens;
}

int main() {
    // Explicit stdout buffer flushing alignment for pipe consistency
    std::setvbuf(stdout, NULL, _IONBF, 0);

    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;

        auto tokens = tokenize(line);
        if (tokens.empty()) continue;

        std::string cmd = tokens[0];

        if (cmd == "uci") {
            std::lock_guard<std::mutex> lock(cout_mutex);
            std::cout << "id name MyCppChessBot" << std::endl;
            std::cout << "id author Your Name" << std::endl;
            std::cout << "uciok" << std::endl;
        } 
        else if (cmd == "isready") {
            std::lock_guard<std::mutex> lock(cout_mutex);
            std::cout << "readyok" << std::endl;
        } 
        else if (cmd == "ucinewgame") {
            // Reset transpositions tables & engine internal arrays
            if (is_searching) {
                is_searching = false;
                if (search_thread.joinable()) search_thread.join();
            }
        } 
        else if (cmd == "position") {
            // Examples: 'position startpos' or 'position fen ...'
            // Parsers can extract the board positions and movements lists here.
            // tokens[1] tells if startpos or fen
        } 
        else if (cmd == "go") {
            int depth = 10;
            for (size_t i = 1; i < tokens.size(); ++i) {
                if (tokens[i] == "depth" && i + 1 < tokens.size()) {
                    depth = std::stoi(tokens[i + 1]);
                }
            }

            // Halt execution if engine is active before commencing a new search
            if (is_searching) {
                is_searching = false;
                if (search_thread.joinable()) search_thread.join();
            }

            // Run search asynchronously to preserve GUI command checks (like `stop`)
            search_thread = std::thread(run_search, depth);
        } 
        else if (cmd == "stop") {
            if (is_searching) {
                is_searching = false;
                if (search_thread.joinable()) search_thread.join();
            }
        } 
        else if (cmd == "quit") {
            is_searching = false;
            if (search_thread.joinable()) search_thread.join();
            break;
        }
    }
    return 0;
}
"""

MOCK_ENGINE_CODE = """#!/usr/bin/env python3
\"\"\"
Mock Chess Bot (UCI-compatible)
------------------------------
A lightweight dummy engine written in pure Python. Use this to quickly test
the UCI interface of chess_gui.py without needing compiled binaries.

Runs a simple stdin/stdout loop matching UCI protocols.
\"\"\"

import sys
import time
import random
import threading

def log_debug(msg):
    # UCI engines write debug info to standard error to prevent corrupting stdout
    sys.stderr.write(f"[MockEngine DEBUG] {msg}\\n")
    sys.stderr.flush()

class MockEngine:
    def __init__(self):
        self.running = True
        self.search_thread = None
        self.searching = False
        self.current_fen = ""
        self.moves_made = []

    def run(self):
        log_debug("Mock Engine initialized.")
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                cmd = line.strip()
                if not cmd:
                    continue
                
                self._handle_command(cmd)
            except Exception as e:
                log_debug(f"Exception in main execution: {str(e)}")
                break

    def _handle_command(self, cmd):
        parts = cmd.split()
        header = parts[0]

        if header == "uci":
            print("id name Mock C++ Bot Simulator")
            print("id author DeepMind AI")
            print("option name Hash type spin default 64 min 1 max 2048")
            print("option name Threads type spin default 1 min 1 max 128")
            print("uciok")
            sys.stdout.flush()

        elif header == "isready":
            print("readyok")
            sys.stdout.flush()

        elif header == "ucinewgame":
            self.moves_made = []
            self.current_fen = ""

        elif header == "position":
            # can be 'position startpos' or 'position startpos moves e2e4' or 'position fen ...'
            if len(parts) > 1:
                if parts[1] == "startpos":
                    self.current_fen = "start"
                    if "moves" in parts:
                        idx = parts.index("moves")
                        self.moves_made = parts[idx+1:]
                elif parts[1] == "fen":
                    # Reconstruct FEN
                    stop_idx = len(parts)
                    if "moves" in parts:
                        stop_idx = parts.index("moves")
                        self.moves_made = parts[stop_idx+1:]
                    self.current_fen = " ".join(parts[2:stop_idx])

        elif header == "go":
            # Command could be 'go depth 12', 'go infinite', etc.
            depth = 8
            if "depth" in parts:
                idx = parts.index("depth")
                if idx + 1 < len(parts):
                    depth = int(parts[idx+1])

            self.searching = True
            self.search_thread = threading.Thread(target=self._search_logic, args=(depth,), daemon=True)
            self.search_thread.start()

        elif header == "stop":
            self.searching = False

        elif header == "quit":
            self.running = False
            self.searching = False

    def _search_logic(self, target_depth):
        log_debug(f"Initiating search at target depth: {target_depth}")
        
        # Simulate active thinking ticks
        simulated_score = 15 # centipawns
        for d in range(1, target_depth + 1):
            if not self.searching:
                break
                
            time.sleep(0.12) # Thinking offset
            
            # Simulated analysis lines
            simulated_score += random.randint(-40, 45)
            nodes = d * 1541
            nps = 24500
            
            # standard info depths output string
            print(f"info depth {d} score cp {simulated_score} nodes {nodes} nps {nps} pv e2e4 g8f6 b1c3")
            sys.stdout.flush()

        # Decide a safe simulated legal coordinates response
        coords_src = ["e2", "d2", "g1", "b1", "c2", "f2"]
        coords_dst = ["e4", "d4", "f3", "c3", "c4", "f4"]
        
        best_move = random.choice(coords_src) + random.choice(coords_dst)
        
        # Print bestmove to let parser render the arrows on board
        print(f"bestmove {best_move}")
        sys.stdout.flush()
        self.searching = False

if __name__ == "__main__":
    engine = MockEngine()
    engine.run()
"""
