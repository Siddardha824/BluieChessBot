from uci.engine_process import EngineProcess
from uci.uci_parser import UCIParser

class UCIClient:
    """
    High-level orchestrator and state manager for a UCI Chess Engine.
    Interfaces between the GUI event loop, low-level process thread queues,
    and the pure functional output parser.
    """
    def __init__(self, log_callback, info_callback, bestmove_callback):
        self.process = EngineProcess()
        self.log_callback = log_callback
        self.info_callback = info_callback
        self.bestmove_callback = bestmove_callback

    @property
    def is_running(self) -> bool:
        """
        Checks if the chess engine subprocess is currently running.
        """
        return self.process.is_running

    def start(self, executable_path: str) -> bool:
        """
        Spawns the engine process, starts background threads, and executes
        the initial UCI handshake protocol ('uci' and 'isready').
        """
        if self.is_running:
            self.stop()

        try:
            success = self.process.start(executable_path)
            if success:
                self.send_command("uci")
                self.send_command("isready")
                return True
            else:
                self.log_callback("Error starting bot executable: Process could not be initialized.\n", "error")
                return False
        except Exception as e:
            self.log_callback(f"Error starting bot executable: {str(e)}\n", "error")
            return False

    def send_command(self, cmd: str):
        """
        Writes a standard UCI command line to the engine's stdin and logs it.
        """
        self.log_callback(f"{cmd}\n", "sent")
        success = self.process.write(cmd)
        if not success:
            self.log_callback("Engine not connected.\n", "warning")

    def update(self):
        """
        Polls for raw engine output, logs it, parses it, and forwards structured
        data to the GUI telemetry and bestmove callbacks.
        Should be called periodically in the main GUI thread.
        """
        while True:
            line = self.process.read_line()
            if line is None:
                break
            
            # Log raw output line
            self.log_callback(f"{line}\n", "received")
            
            # Parse line functionality
            parsed = UCIParser.parse_line(line)
            if not parsed:
                continue
                
            if parsed["type"] == "info":
                # Convert back to flat dictionary format for backwards compatibility
                info_dict = parsed.copy()
                info_dict.pop("type")
                self.info_callback(info_dict)
            elif parsed["type"] == "bestmove":
                best = parsed.get("bestmove")
                ponder = parsed.get("ponder")
                self.bestmove_callback(best, ponder)

    def stop(self):
        """
        Gracefully shuts down the engine process and triggers disconnected logs.
        """
        self.process.stop()
        self.log_callback("Engine process disconnected.\n", "warning")
