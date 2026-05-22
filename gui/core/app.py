import tkinter as tk

from themes.theme_manager import ThemeManager
from board.chessboard import ChessBoard


class BluieApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Bluie Chess Bot")

        self.geometry("1100x650")
        self.state("zoomed")

        self.theme_manager = ThemeManager()

        self.theme = self.theme_manager.get_theme()

        self.configure(bg=self.theme.WINDOW_BG)

        self.board = ChessBoard(self, self.theme)

        self.board.pack(
            expand=True,
            fill="both",
            padx=20,
            pady=20
        )