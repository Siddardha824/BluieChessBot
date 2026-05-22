from PIL import Image, ImageTk

class SpriteManager:

    PIECE_ORDER = [
        "K", "Q", "B", "N", "R", "P",
        "k", "q", "b", "n", "r", "p"
    ]

    def __init__(self, sprite_path):

        self.sprite_path = sprite_path

        self.original_sheet = Image.open(sprite_path)

        self.cache = {}

        self.sprite_map = {}

        self.load_sprites()

    def load_sprites(self):

        sheet_width, sheet_height = self.original_sheet.size

        piece_width = sheet_width // 6
        piece_height = sheet_height // 2

        index = 0

        for row in range(2):
            for col in range(6):
                piece = self.PIECE_ORDER[index]

                x1 = col * piece_width
                y1 = row * piece_height

                x2 = x1 + piece_width
                y2 = y1 + piece_height

                piece_img = self.original_sheet.crop((x1,y1,x2,y2))

                self.sprite_map[piece] = piece_img

                index += 1

    def get_piece_image(self, piece, tile_size):
        key = (piece, int(tile_size))

        if key in self.cache:
            return self.cache[key]
        
        piece_img = self.sprite_map[piece]

        scaled_img = piece_img.resize((int(tile_size), int(tile_size)), Image.Resampling.LANCZOS)

        tk_image = ImageTk.PhotoImage(scaled_img)

        self.cache[key] = tk_image

        return tk_image