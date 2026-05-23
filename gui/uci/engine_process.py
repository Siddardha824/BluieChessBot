import os
import sys
import subprocess
import threading
import queue

class EngineProcess:
    """
    Manages low-level OS process communication for a UCI Chess Engine.
    Handles thread-safe writing to standard input and non-blocking background
    reading from standard output into a thread-safe queue.
    """
    def __init__(self):
        self.process = None
        self.read_thread = None
        self.is_running = False
        self.output_queue = queue.Queue()

    def start(self, executable_path: str) -> bool:
        """
        Spawns the engine process and starts a background reader thread.
        """
        if self.process:
            self.stop()
        
        try:
            cmd = [executable_path]
            # If a python file is provided, run it using the current python interpreter
            if executable_path.endswith('.py'):
                cmd = [sys.executable, executable_path]

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, # Suppress standard error to avoid polluting streams
                text=True
            )
            self.is_running = True
            
            # Start background reader thread
            self.read_thread = threading.Thread(target=self._reader_loop, daemon=True)
            self.read_thread.start()
            return True
        except Exception:
            self.is_running = False
            self.process = None
            return False

    def write(self, line: str) -> bool:
        """
        Writes a single command line to the engine's standard input in a thread-safe manner.
        """
        if not self.process or not self.is_running:
            return False
        
        try:
            self.process.stdin.write(line + "\n")
            self.process.stdin.flush()
            return True
        except Exception:
            self.stop()
            return False

    def _reader_loop(self):
        """
        Continuously reads lines from the process's standard output and puts them
        into the thread-safe queue.
        """
        while self.is_running and self.process:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    self.output_queue.put(line)
            except Exception:
                break
        self.is_running = False

    def read_line(self) -> str | None:
        """
        Pulls a line from the output queue in a non-blocking manner.
        Returns None if the queue is empty.
        """
        try:
            return self.output_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        """
        Gracefully terminates the process, falling back to a hard kill if needed.
        """
        self.is_running = False
        if self.process:
            try:
                # Try to write quit command to standard input
                self.process.stdin.write("quit\n")
                self.process.stdin.flush()
            except Exception:
                pass
            
            try:
                self.process.terminate()
                self.process.wait(timeout=0.5)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None
