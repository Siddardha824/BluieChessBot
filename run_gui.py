import os
import sys

# Ensure correct working directory so assets and relative build binaries load perfectly
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(script_dir, "gui"))

# Add the gui folder to the Python import path
sys.path.append(os.getcwd())

import ChessGUI

if __name__ == "__main__":
    app = ChessGUI.ChessGUI()
    
    def on_close():
        app.engine.stop()
        app.destroy()
        
    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()
