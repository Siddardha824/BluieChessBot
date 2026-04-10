import pygame
import sys
import chess
import ChessBot

class ChessGUI:
    def __init__(self):
        # Initializing Pygame subsystems
        pygame.init()
        pygame.font.init()

        # Display settings
        self.WIDTH = 640
        self.HEIGHT = 640
        self.SQ_SIZE = self.WIDTH // 8
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('ChessGUI')
        self.clock = pygame.time.Clock()

        # Game State
        self.board = chess.Board()
        self.pieces = self.load_assets('images/Pieces.png')
        self.selected_square = None

        # Design Theme
        self.light_color = (181, 230, 230)
        self.dark_color = (83, 151, 151)
        self.font = pygame.font.SysFont('arial', 18, bold=True)

    def load_assets(self, filepath):
        """Loads a sprite sheet and extracts the individual chess pieces."""
        sprite_sheet = pygame.image.load(filepath).convert_alpha()
        sheet_width, sheet_height = sprite_sheet.get_size()
        piece_width = sheet_width // 6
        piece_height = sheet_height // 2

        white_symbols = ['K', 'Q', 'B', 'N', 'R', 'P']
        black_symbols = ['k', 'q', 'b', 'n', 'r', 'p']
        pieces = {}

        for col, symbol in enumerate(white_symbols):
            rect = pygame.Rect(col * piece_width, 0, piece_width, piece_height)
            image = sprite_sheet.subsurface(rect)
            pieces[symbol] = pygame.transform.smoothscale(image, (self.SQ_SIZE, self.SQ_SIZE))
        
        for col, symbol in enumerate(black_symbols):
            rect = pygame.Rect(col * piece_width, piece_height, piece_width, piece_height)
            image = sprite_sheet.subsurface(rect)
            pieces[symbol] = pygame.transform.smoothscale(image, (self.SQ_SIZE, self.SQ_SIZE))

        return pieces
    
    def draw_board(self):
        """Draws the 8x8 alternating checkerboard."""
        colors = [self.light_color, self.dark_color]
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self.screen, color, pygame.Rect(col*self.SQ_SIZE, row*self.SQ_SIZE, self.SQ_SIZE, self.SQ_SIZE))
    
    def draw_coordinates(self):
        """Draws rank and file indicators on the board edges."""
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']

        for i in range(8):
            file_color = self.dark_color if i % 2 != 0 else self.light_color
            file_text = self.font.render(files[i], True, file_color)
            self.screen.blit(file_text, (i * self.SQ_SIZE + self.SQ_SIZE - 15, 7 * self.SQ_SIZE + self.SQ_SIZE - 22))

            rank_color = self.dark_color if i % 2 == 0 else self.light_color
            rank_text = self.font.render(ranks[i], True, rank_color)
            self.screen.blit(rank_text, (3, i * self.SQ_SIZE + 3))

    def draw_highlight(self):
        """Highlights the last move and the currently selected square."""

        # 1. Highlight the last move played
        if len(self.board.move_stack) > 0:
            last_move = self.board.peek()
            # Loop through both the starting and destination square of the last move
            for square in [last_move.from_square, last_move.to_square]:
                s_file = chess.square_file(square)
                s_rank = 7- chess.square_rank(square)

                # Create a semi-transparent surface
                last_move_highlight = pygame.Surface((self.SQ_SIZE, self.SQ_SIZE))
                last_move_highlight.set_alpha(80)
                last_move_highlight.fill((255, 255, 0))
                self.screen.blit(last_move_highlight, (s_file * self.SQ_SIZE, s_rank * self.SQ_SIZE))

        # 2. Highlight the currently selected square (if the user clicks a piece)
        if self.selected_square is not None:
            s_file = chess.square_file(self.selected_square)
            s_rank = 7 - chess.square_rank(self.selected_square)

            selection_highlight = pygame.Surface((self.SQ_SIZE, self.SQ_SIZE))
            selection_highlight.set_alpha(100)
            selection_highlight.fill((255, 255, 0))
            self.screen.blit(selection_highlight, (s_file * self.SQ_SIZE, s_rank * self.SQ_SIZE))

    def draw_pieces(self):
        """Draws the pieces on the board based on the python-chess state."""
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                self.screen.blit(self.pieces[piece.symbol()], (col * self.SQ_SIZE, row * self.SQ_SIZE))
    
    def handle_click(self, pos):
        """Processes mouse clicks to select pieces and make moves."""
        x, y = pos
        file_idx = x // self.SQ_SIZE
        rank_idx = 7 - (y // self.SQ_SIZE)
        clicked_square = chess.square(file_idx, rank_idx)

        if self.selected_square is None:
            if self.board.piece_at(clicked_square):
                self.selected_square = clicked_square
        else:
            move = chess.Move(self.selected_square, clicked_square)

            # Handle Pawn Promotion
            if self.board.piece_at(self.selected_square) and self.board.piece_at(self.selected_square).piece_type == chess.PAWN:
                if rank_idx == 0 or rank_idx == 7:
                    move = chess.Move(self.selected_square, clicked_square, promotion=chess.QUEEN)

            
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
            else:
                if self.board.piece_at(clicked_square) and self.board.color_at(clicked_square) == self.board.turn:
                    self.selected_square = clicked_square
                else:
                    self.selected_square = None
    
    def render(self):
        """Compiles all drawing functions into a single frame update."""
        self.draw_board()
        self.draw_coordinates()
        self.draw_highlight()
        self.draw_pieces()
        pygame.display.flip()

    def run(self):
        """The main execution loop of the game."""
        running = True
        Bot = ChessBot.ChessBot()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
            
            self.render()
            if not self.board.is_game_over():
                move = Bot.best_move(self.board)
                self.board.push(move)
            self.clock.tick(60)
        print("Game Over:", self.board.result())
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = ChessGUI()
    app.run()