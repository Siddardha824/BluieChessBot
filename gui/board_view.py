import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from constants import PIECE_CHARS, BOARD_THEMES, DEFAULT_BOARD, STARTING_FEN

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class EvaluationBar(tk.Canvas):
    def __init__(self, parent, app, **kwargs):
        width = kwargs.pop('width', int(22 * app.dpi_scale))
        height = kwargs.pop('height', app.tile_size * 8)
        super().__init__(parent, width=width, height=height, borderwidth=0, highlightthickness=0, **kwargs)
        self.app = app

    def draw(self):
        self.delete("all")
        height = self.app.tile_size * 8
        width = int(22 * self.app.dpi_scale)
        
        eval_val = self.app.last_engine_eval
        if self.app.last_score_mate:
            prob = 1.0 if eval_val > 0 else 0.0
        else:
            clamped = max(-6.0, min(6.0, eval_val))
            prob = (clamped + 6.0) / 12.0 # Scale to 0 to 1 range
            
        white_height = int(height * prob)
        black_height = height - white_height
        
        # Black portion (top score)
        self.create_rectangle(0, 0, width, black_height, fill="#020617", outline="")
        # White portion (bottom score)
        self.create_rectangle(0, black_height, width, height, fill="#f8fafc", outline="")
        # Thin visual divider line between split
        self.create_line(0, black_height, width, black_height, fill="#38bdf8", width=2)
        
        # Draw dynamic text label on top of the visual elements
        lbl_text = f"{eval_val:+.1f}" if not self.app.last_score_mate else (f"M{int(eval_val)}" if eval_val >= 0 else f"-M{abs(int(eval_val))}")
        if abs(eval_val) < 0.01:
            lbl_text = "0.0"
            
        fill_color = "#f87171" if eval_val < 0 else "#0ea5e9"
        offset_y = int(25 * self.app.dpi_scale)
        y_pos = black_height + offset_y if black_height < height / 2 else black_height - offset_y
        font_size = max(6, int(8 * self.app.dpi_scale))
        self.create_text(width / 2, y_pos, text=lbl_text, font=("Segoe UI", font_size, "bold"), fill=fill_color)


class ChessBoardCanvas(tk.Canvas):
    def __init__(self, parent, app, **kwargs):
        width = kwargs.pop('width', app.tile_size * 8)
        height = kwargs.pop('height', app.tile_size * 8)
        super().__init__(parent, width=width, height=height, borderwidth=0, highlightthickness=0, **kwargs)
        self.app = app
        
        self.bind("<Button-1>", self.on_board_press)
        self.bind("<B1-Motion>", self.on_board_drag)
        self.bind("<ButtonRelease-1>", self.on_board_release)

    def load_piece_sprites(self):
        self.app.piece_sprites = {}
        path = self.app.sprite_path_var.get()
        if not path or not os.path.exists(path):
            # Try in assets directory
            script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
            path = os.path.join(script_dir, "assets", "Pieces.png")
            if not os.path.exists(path):
                path = os.path.join(script_dir, "Pieces.png")
                if not os.path.exists(path):
                    path = os.path.join(os.getcwd(), "assets", "Pieces.png")
                    if not os.path.exists(path):
                        path = os.path.join(os.getcwd(), "Pieces.png")
                        if not os.path.exists(path):
                            return False
        
        try:
            # Try high quality scaling via Pillow (PIL)
            if HAS_PIL:
                pil_img = Image.open(path)
                sheet_width, sheet_height = pil_img.size
                piece_width = sheet_width // 6
                piece_height = sheet_height // 2
                
                piece_order = ['K', 'Q', 'B', 'N', 'R', 'P']
                # Scaled dynamically based on board tile size to prevent blurriness
                target_size = (self.app.tile_size, self.app.tile_size)
                
                for row in range(2):
                    for col in range(6):
                        piece_char = piece_order[col]
                        if row == 1:
                            piece_char = piece_char.lower() # Black pieces
                        
                        x1 = col * piece_width
                        y1 = row * piece_height
                        x2 = x1 + piece_width
                        y2 = y1 + piece_height
                        
                        cropped = pil_img.crop((x1, y1, x2, y2))
                        
                        try:
                            resampling_filter = Image.Resampling.LANCZOS
                        except AttributeError:
                            resampling_filter = Image.ANTIALIAS
                            
                        scaled = cropped.resize(target_size, resampling_filter)
                        self.app.piece_sprites[piece_char] = ImageTk.PhotoImage(scaled)
                
                # Keep a reference to prevent garbage collection
                self.app.sprite_sheet_img = None
                
                if hasattr(self.app, 'lbl_sprite_status'):
                    self.app.lbl_sprite_status.config(text=f"{os.path.basename(path)}: Loaded (HD)", foreground="#34d399")
                return True
                
            else:
                # Fallback to Tcl/Tk native subsampling if PIL is not installed
                self.app.sprite_sheet_img = tk.PhotoImage(file=path)
                
                piece_order = ['K', 'Q', 'B', 'N', 'R', 'P']
                
                for row in range(2):
                    for col in range(6):
                        piece_char = piece_order[col]
                        if row == 1:
                            piece_char = piece_char.lower() # Black pieces
                        
                        x1 = col * 400
                        y1 = row * 400
                        x2 = x1 + 400
                        y2 = y1 + 400
                        
                        cropped = tk.PhotoImage()
                        cropped.tk.call(cropped, 'copy', self.app.sprite_sheet_img, '-from', x1, y1, x2, y2)
                        
                        # Dynamically calculate the closest integer subsampling factor to match piece size
                        sub_factor = max(1, 400 // self.app.tile_size)
                        scaled = cropped.subsample(sub_factor, sub_factor)
                        self.app.piece_sprites[piece_char] = scaled
                
                if hasattr(self.app, 'lbl_sprite_status'):
                    self.app.lbl_sprite_status.config(text=f"{os.path.basename(path)}: Loaded (Fallback)", foreground="#34d399")
                return True
                
        except Exception as e:
            print(f"Error loading piece sprites: {e}")
            if hasattr(self.app, 'lbl_sprite_status'):
                self.app.lbl_sprite_status.config(text="Load Failed", foreground="#f87171")
            return False

    def draw(self):
        self.delete("all")
        
        # Read colors from modern theme configuration
        theme_name = self.app.active_theme_name.get()
        cfg = BOARD_THEMES.get(theme_name, BOARD_THEMES["Classic Emerald"])
        
        dark_color = cfg["dark"]
        light_color = cfg["light"]
        highlight_color = cfg["select"]
        last_move_color = cfg["last_move"]
        
        for r in range(8):
            for c in range(8):
                # Calculate coordinates
                x1 = c * self.app.tile_size
                y1 = r * self.app.tile_size
                x2 = x1 + self.app.tile_size
                y2 = y1 + self.app.tile_size
                
                # Determine standard block color
                base_color = light_color if (r + c) % 2 == 0 else dark_color
                
                # Highlight if selected or part of last move
                if self.app.selected_square == (r, c):
                    color = highlight_color
                elif (r, c) in self.app.last_move_squares:
                    color = last_move_color
                else:
                    color = base_color
                    
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                
                # Present standard Chess Piece
                piece = self.app.board_state[r][c]
                if piece != '.':
                    # Skip drawing on the square if we are actively dragging this piece
                    if self.app.dragged_piece is not None and self.app.drag_start_square == (r, c):
                        continue
                        
                    # Draw with high quality sprites if enabled and loaded
                    if self.app.use_sprites.get() and piece in self.app.piece_sprites:
                        self.create_image(
                            x1 + self.app.tile_size/2,
                            y1 + self.app.tile_size/2,
                            image=self.app.piece_sprites[piece],
                            anchor="center"
                        )
                    else:
                        # Fallback to Unicode Chess pieces
                        tag = piece
                        if piece.isupper():
                            tag_key = f"{piece}_white"
                        else:
                            tag_key = piece
                            
                        unicode_char = PIECE_CHARS.get(tag_key, piece)
                        text_color = cfg.get("piece_white", "#f8fafc") if piece.isupper() else cfg.get("piece_black", "#1e293b")
                            
                        font_size = int(self.app.tile_size * 0.37)
                        self.create_text(
                            x1 + self.app.tile_size/2,
                            y1 + self.app.tile_size/2,
                            text=unicode_char,
                            font=("Segoe UI", font_size, "bold"),
                            fill=text_color
                        )
                        
        # Draw rank and file indicators on the board edges (bottom row and left-most col)
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
        font_size = max(7, int(self.app.tile_size * 0.18))
        
        for i in range(8):
            # File label (bottom-right of each square in row 7)
            # Alternate colors: if square is dark, use light color, otherwise dark color.
            file_color = light_color if (7 + i) % 2 != 0 else dark_color
            x_file = (i + 1) * self.app.tile_size - int(10 * self.app.dpi_scale)
            y_file = 8 * self.app.tile_size - int(8 * self.app.dpi_scale)
            self.create_text(
                x_file, y_file,
                text=files[i],
                font=("Segoe UI", font_size, "bold"),
                fill=file_color,
                anchor="center"
            )
            
            # Rank label (top-left of each square in column 0)
            # Alternate colors: if square is dark, use light color, otherwise dark color.
            rank_color = light_color if i % 2 != 0 else dark_color
            x_rank = int(10 * self.app.dpi_scale)
            y_rank = i * self.app.tile_size + int(10 * self.app.dpi_scale)
            self.create_text(
                x_rank, y_rank,
                text=ranks[i],
                font=("Segoe UI", font_size, "bold"),
                fill=rank_color,
                anchor="center"
            )

        # Draw the dragged piece on top of everything if drag is active
        if self.app.dragged_piece is not None:
            px = self.app.drag_x
            py = self.app.drag_y
            piece = self.app.dragged_piece
            if self.app.use_sprites.get() and piece in self.app.piece_sprites:
                self.create_image(
                    px,
                    py,
                    image=self.app.piece_sprites[piece],
                    anchor="center"
                )
            else:
                # Fallback to Unicode Chess pieces
                tag = piece
                if piece.isupper():
                    tag_key = f"{piece}_white"
                else:
                    tag_key = piece
                    
                unicode_char = PIECE_CHARS.get(tag_key, piece)
                text_color = cfg.get("piece_white", "#f8fafc") if piece.isupper() else cfg.get("piece_black", "#1e293b")
                    
                font_size = int(self.app.tile_size * 0.37)
                self.create_text(
                    px,
                    py,
                    text=unicode_char,
                    font=("Segoe UI", font_size, "bold"),
                    fill=text_color
                )

    def on_board_press(self, event):
        col = event.x // self.app.tile_size
        row = event.y // self.app.tile_size
        
        if not (0 <= col < 8 and 0 <= row < 8):
            return
            
        brush = self.app.selected_brush.get()
        if brush == "move":
            # Deselect if clicking the already selected square
            if self.app.selected_square == (row, col):
                self.app.selected_square = None
                self.draw()
                return

            # Click-to-move trigger: if we clicked a different square and had a selection
            if self.app.selected_square is not None and self.app.selected_square != (row, col):
                start_row, start_col = self.app.selected_square
                
                p_start = self.app.board_state[start_row][start_col]
                p_dest = self.app.board_state[row][col]
                
                # Check if the destination contains a piece of the same color to switch selection instead of moving
                same_color = False
                if p_start != '.' and p_dest != '.':
                    same_color = (p_start.isupper() and p_dest.isupper()) or (p_start.islower() and p_dest.islower())
                
                if same_color:
                    # Switch selection and start dragging the friendly piece
                    self.app.selected_square = (row, col)
                    self.app.dragged_piece = p_dest
                    self.app.drag_start_square = (row, col)
                    self.app.drag_x = event.x
                    self.app.drag_y = event.y
                    self.draw()
                    return
                
                self.app.selected_square = None
                
                # Propose a move sequence
                files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
                ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
                
                from_sq = f"{files[start_col]}{ranks[start_row]}"
                to_sq = f"{files[col]}{ranks[row]}"
                move_str = f"{from_sq}{to_sq}"
                
                # Simple visual shift
                p = self.app.board_state[start_row][start_col]
                self.app.board_state[start_row][start_col] = '.'
                self.app.board_state[row][col] = p
                
                self.app.last_move_squares = [(start_row, start_col), (row, col)]
                self.app.custom_moves.append(move_str)
                self.app.lbl_moves.config(text=f"Moves sent: {' '.join(self.app.custom_moves)}")
                
                if self.app.engine.is_running:
                    if self.app.current_fen == STARTING_FEN or not self.app.current_fen:
                        position_payload = f"position startpos moves {' '.join(self.app.custom_moves)}"
                    else:
                        position_payload = f"position fen {self.app.current_fen} moves {' '.join(self.app.custom_moves)}"
                    self.app.engine.send_command(position_payload)
                    
                self.draw()
                return

            # Otherwise, start a drag-and-drop event
            piece = self.app.board_state[row][col]
            if piece != '.':
                self.app.dragged_piece = piece
                self.app.drag_start_square = (row, col)
                self.app.drag_x = event.x
                self.app.drag_y = event.y
                self.app.selected_square = (row, col)
                self.draw()
        elif brush == "erase":
            self.app.board_state[row][col] = '.'
            self.app.last_move_squares = []
            self.app.on_sandbox_change()
            self.draw()
        else:
            # Piece paintbrush
            self.app.board_state[row][col] = brush
            self.app.last_move_squares = []
            self.app.on_sandbox_change()
            self.draw()

    def on_board_drag(self, event):
        brush = self.app.selected_brush.get()
        if brush == "move":
            if self.app.dragged_piece is not None:
                self.app.drag_x = event.x
                self.app.drag_y = event.y
                self.draw()
        else:
            # Sandbox Paintbrush drag drawing (continuous drag-to-paint/erase)
            col = event.x // self.app.tile_size
            row = event.y // self.app.tile_size
            if 0 <= col < 8 and 0 <= row < 8:
                if brush == "erase":
                    if self.app.board_state[row][col] != '.':
                        self.app.board_state[row][col] = '.'
                        self.app.on_sandbox_change()
                        self.draw()
                else:
                    if self.app.board_state[row][col] != brush:
                        self.app.board_state[row][col] = brush
                        self.app.on_sandbox_change()
                        self.draw()

    def on_board_release(self, event):
        brush = self.app.selected_brush.get()
        if brush == "move":
            if self.app.dragged_piece is not None:
                start_row, start_col = self.app.drag_start_square
                col = event.x // self.app.tile_size
                row = event.y // self.app.tile_size
                
                dragged_p = self.app.dragged_piece
                self.app.dragged_piece = None
                self.app.drag_start_square = None
                
                if 0 <= col < 8 and 0 <= row < 8:
                    # Drop piece: if dropped on a different square, make the move
                    if (start_row, start_col) != (row, col):
                        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
                        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
                        
                        from_sq = f"{files[start_col]}{ranks[start_row]}"
                        to_sq = f"{files[col]}{ranks[row]}"
                        move_str = f"{from_sq}{to_sq}"
                        
                        p = self.app.board_state[start_row][start_col]
                        self.app.board_state[start_row][start_col] = '.'
                        self.app.board_state[row][col] = p
                        
                        self.app.last_move_squares = [(start_row, start_col), (row, col)]
                        self.app.custom_moves.append(move_str)
                        self.app.lbl_moves.config(text=f"Moves sent: {' '.join(self.app.custom_moves)}")
                        self.app.selected_square = None
                        
                        if self.app.engine.is_running:
                            if self.app.current_fen == STARTING_FEN or not self.app.current_fen:
                                position_payload = f"position startpos moves {' '.join(self.app.custom_moves)}"
                            else:
                                position_payload = f"position fen {self.app.current_fen} moves {' '.join(self.app.custom_moves)}"
                            self.app.engine.send_command(position_payload)
                    else:
                        # Dropped on same square, leave as selected for standard click-to-move click support
                        pass
                self.draw()

    def generate_fen(self):
        rows = []
        for r in range(8):
            empty_count = 0
            row_str = ""
            for c in range(8):
                piece = self.app.board_state[r][c]
                if piece == '.':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += piece
            if empty_count > 0:
                row_str += str(empty_count)
            rows.append(row_str)
        board_fen = "/".join(rows)
        return f"{board_fen} w KQkq - 0 1"

    def parse_fen(self, fen):
        try:
            parts = fen.split()
            board_part = parts[0]
            new_board = []
            rows = board_part.split('/')
            for r in rows:
                new_row = []
                for char in r:
                    if char.isdigit():
                        new_row.extend(['.'] * int(char))
                    else:
                        new_row.append(char)
                new_board.append(new_row)
            
            if len(new_board) == 8 and all(len(row) == 8 for row in new_board):
                self.app.board_state = new_board
                return True
            return False
        except Exception:
            return False
