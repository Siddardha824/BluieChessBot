#!/usr/bin/env python3
"""
Mock Chess Bot (UCI-compatible)
------------------------------
A lightweight dummy engine written in pure Python. Use this to quickly test
the UCI interface of chess_gui.py without needing compiled binaries.

Runs a simple stdin/stdout loop matching UCI protocols.
"""

import sys
import time
import random
import threading

def log_debug(msg):
    # UCI engines write debug info to standard error to prevent corrupting stdout
    sys.stderr.write(f"[MockEngine DEBUG] {msg}\n")
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
