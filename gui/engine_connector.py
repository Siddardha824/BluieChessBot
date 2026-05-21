import os
import sys
import subprocess
import threading
import queue

class UCIEngineConnector:
    def __init__(self, log_callback, info_callback, bestmove_callback):
        self.process = None
        self.read_thread = None
        self.is_running = False
        self.log_callback = log_callback
        self.info_callback = info_callback
        self.bestmove_callback = bestmove_callback
        self.msg_queue = queue.Queue()

    def start(self, executable_path):
        if self.process:
            self.stop()
        
        try:
            # Standardize command execution list matching user's connection syntax
            cmd = [executable_path]
            
            # If a python file is provided, run it using the standard interpreter
            if executable_path.endswith('.py'):
                cmd = [sys.executable, executable_path]

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )
            self.is_running = True
            
            # Start reader thread to avoid blocking GUI
            self.read_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self.read_thread.start()
            
            # Send initial UCI commands
            self.send_command("uci")
            self.send_command("isready")
            return True
        except Exception as e:
            self.is_running = False
            self.log_callback(f"🔴 Error starting bot executable: {str(e)}\n", "error")
            return False

    def send_command(self, cmd):
        if not self.process or not self.is_running:
            self.log_callback("⚠️ Engine not connected.\n", "warning")
            return
        
        try:
            self.log_callback(f"➡️ {cmd}\n", "sent")
            self.process.stdin.write(cmd + "\n")
            self.process.stdin.flush()
        except Exception as e:
            self.log_callback(f"🔴 Write Error: {str(e)}\n", "error")
            self.stop()

    def _reader_loop(self):
        while self.is_running and self.process:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    self.msg_queue.put(line)
            except Exception:
                break
        self.is_running = False

    def update(self):
        """Called periodically by Tkinter main loop to process engine output"""
        while not self.msg_queue.empty():
            line = self.msg_queue.get()
            self.log_callback(f"⬅️ {line}\n", "received")
            self._parse_line(line)

    def _parse_line(self, line):
        tokens = line.split()
        if not tokens:
            return
            
        if tokens[0] == "info":
            info_dict = {}
            # Parse key-values from engine info
            # e.g., "info depth 12 seldepth 14 score cp 34 nodes 120531 nps 152123 pv e2e4..."
            i = 1
            while i < len(tokens):
                key = tokens[i]
                if key in ["depth", "seldepth", "nodes", "nps", "hashfull", "time"]:
                    if i + 1 < len(tokens):
                        info_dict[key] = tokens[i+1]
                        i += 2
                elif key == "score":
                    if i + 2 < len(tokens):
                        info_dict["score_type"] = tokens[i+1] # cp or mate
                        info_dict["score_val"] = tokens[i+2]
                        i += 3
                elif key == "pv":
                    info_dict["pv"] = " ".join(tokens[i+1:])
                    break
                else:
                    i += 1
            if info_dict:
                self.info_callback(info_dict)
                
        elif tokens[0] == "bestmove":
            bestmove = tokens[1]
            ponder = tokens[3] if len(tokens) > 3 and tokens[2] == "ponder" else None
            self.bestmove_callback(bestmove, ponder)

    def stop(self):
        self.is_running = False
        if self.process:
            try:
                self.send_command("quit")
                self.process.terminate()
                self.process.wait(timeout=1)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None
        self.log_callback("🔌 Engine process disconnected.\n", "warning")
