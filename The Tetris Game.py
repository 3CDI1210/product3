import tkinter as tk
import random

CELL_SIZE = 30
COLS = 10
ROWS = 20

SHAPES = {
    'I': [(0,1), (1,1), (2,1), (3,1)],
    'J': [(0,0), (0,1), (1,1), (2,1)],
    'L': [(0,1), (1,1), (2,1), (2,0)],
    'O': [(0,0), (1,0), (0,1), (1,1)],
    'S': [(1,0), (2,0), (0,1), (1,1)],
    'T': [(1,0), (0,1), (1,1), (2,1)],
    'Z': [(0,0), (1,0), (1,1), (2,1)],
}

COLORS = {
    'I': 'cyan',
    'J': 'blue',
    'L': 'orange',
    'O': 'yellow',
    'S': 'green',
    'T': 'purple',
    'Z': 'red',
}

SCORE_TABLE = {
    1: 100,
    2: 300,
    3: 700,
    4: 1500,
}

class Tetris:
    def __init__(self, root, on_game_over_callback=None):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.score = 0
        self.score_label = tk.Label(self.frame, text=f"Score: {self.score}", font=("Helvetica", 16))
        self.score_label.pack()

        self.canvas = tk.Canvas(self.frame, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE, bg='black')
        self.canvas.pack()

        self.next_label = tk.Label(self.frame, text="Next:", font=("Helvetica", 14))
        self.next_label.pack()

        self.next_canvas = tk.Canvas(self.frame, width=6*CELL_SIZE, height=4*CELL_SIZE, bg='black')
        self.next_canvas.pack(pady=(0, 10))

        self.control_frame = tk.Frame(self.frame)
        self.btn_retry = tk.Button(self.control_frame, text="もう一度プレイ", font=("Helvetica", 14), command=self.restart_game)
        self.btn_title = tk.Button(self.control_frame, text="タイトルに戻る", font=("Helvetica", 14), command=self.return_to_title)
        self.btn_retry.pack(side='left', padx=10, pady=10)
        self.btn_title.pack(side='left', padx=10, pady=10)

        self.board = [[None]*COLS for _ in range(ROWS)]

        self.current_shape = None
        self.current_pos = [0, 3]
        self.current_type = None
        self.next_type = random.choice(list(SHAPES.keys()))

        self.game_over = False
        self.on_game_over_callback = on_game_over_callback

        self.drop_interval = 500  # ミリ秒で初期スピード
        self.root.bind('<Key>', self.key_handler)

        self.spawn_new_piece()
        self.speed_up_timer()
        self.game_loop()

    def update_score(self, lines_cleared):
        if lines_cleared > 0:
            self.score += SCORE_TABLE.get(lines_cleared, lines_cleared * 100)
            self.score_label.config(text=f"Score: {self.score}")

    def restart_game(self):
        self.control_frame.pack_forget()
        self.board = [[None]*COLS for _ in range(ROWS)]
        self.current_shape = None
        self.current_pos = [0, 3]
        self.current_type = None
        self.next_type = random.choice(list(SHAPES.keys()))
        self.game_over = False
        self.score = 0
        self.score_label.config(text=f"Score: {self.score}")
        self.drop_interval = 500
        self.spawn_new_piece()
        self.speed_up_timer()
        self.game_loop()

    def return_to_title(self):
        self.control_frame.pack_forget()
        self.frame.pack_forget()
        if self.on_game_over_callback:
            self.on_game_over_callback()

    def spawn_new_piece(self):
        self.current_type = self.next_type
        self.current_shape = SHAPES[self.current_type]
        self.current_pos = [0, COLS // 2 - 2]
        self.next_type = random.choice(list(SHAPES.keys()))
        if not self.can_move(self.current_shape, self.current_pos):
            self.draw_game_over()

    def rotate(self, shape):
        return [(y, -x) for (x, y) in shape]

    def can_move(self, shape, pos):
        for x, y in shape:
            new_x = pos[0] + x
            new_y = pos[1] + y
            if new_x < 0 or new_x >= ROWS or new_y < 0 or new_y >= COLS:
                return False
            if self.board[new_x][new_y] is not None:
                return False
        return True

    def freeze_piece(self):
        for x, y in self.current_shape:
            r = self.current_pos[0] + x
            c = self.current_pos[1] + y
            self.board[r][c] = COLORS[self.current_type]
        lines_cleared = self.clear_lines()
        self.update_score(lines_cleared)
        self.spawn_new_piece()

    def clear_lines(self):
        new_board = []
        lines_cleared = 0
        for row in self.board:
            if None not in row:
                lines_cleared += 1
            else:
                new_board.append(row)
        for _ in range(lines_cleared):
            new_board.insert(0, [None]*COLS)
        self.board = new_board
        return lines_cleared

    def move(self, dx, dy):
        new_pos = [self.current_pos[0] + dx, self.current_pos[1] + dy]
        if self.can_move(self.current_shape, new_pos):
            self.current_pos = new_pos
            return True
        return False

    def key_handler(self, event):
        if self.game_over:
            return
        if event.keysym == 'Left':
            self.move(0, -1)
        elif event.keysym == 'Right':
            self.move(0, 1)
        elif event.keysym == 'Down':
            if not self.move(1, 0):
                self.freeze_piece()
        elif event.keysym == 'Up':
            rotated = self.rotate(self.current_shape)
            if self.can_move(rotated, self.current_pos):
                self.current_shape = rotated
        self.draw()

    def game_loop(self):
        if self.game_over:
            return
        if not self.move(1, 0):
            self.freeze_piece()
        self.draw()
        self.root.after(self.drop_interval, self.game_loop)

    def speed_up_timer(self):
        if self.game_over:
            return
        self.drop_interval = max(100, self.drop_interval - 50)
        self.root.after(30000, self.speed_up_timer)  # 30秒ごとにスピードアップ

    def draw_cell(self, canvas, r, c, color):
        x0 = c * CELL_SIZE
        y0 = r * CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='grey')

    def draw_grid(self, canvas, rows, cols):
        for r in range(rows):
            for c in range(cols):
                x0 = c * CELL_SIZE
                y0 = r * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                canvas.create_rectangle(x0, y0, x1, y1, outline='gray')

    def draw_next_piece(self):
        self.next_canvas.delete("all")
        shape = SHAPES[self.next_type]
        color = COLORS[self.next_type]
        offset_x = 1
        offset_y = 1
        for x, y in shape:
            self.draw_cell(self.next_canvas, offset_y + x, offset_x + y, color)
        self.draw_grid(self.next_canvas, 4, 6)

    def draw(self):
        if self.game_over:
            return
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                color = self.board[r][c]
                if color:
                    self.draw_cell(self.canvas, r, c, color)
        for x, y in self.current_shape:
            r = self.current_pos[0] + x
            c = self.current_pos[1] + y
            self.draw_cell(self.canvas, r, c, COLORS[self.current_type])
        self.draw_grid(self.canvas, ROWS, COLS)
        self.draw_next_piece()

    def draw_game_over(self):
        self.game_over = True
        self.canvas.delete("all")
        self.canvas.create_text(COLS*CELL_SIZE//2, ROWS*CELL_SIZE//2 - 20,
                                text="Game Over", fill="white", font=("Helvetica", 32))
        self.control_frame.pack()

class TitleScreen:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE)
        self.frame.pack()

        self.title_label = tk.Label(self.frame, text="テトリス", font=("Helvetica", 32))
        self.title_label.pack(pady=40)

        self.start_button = tk.Button(self.frame, text="スタート", font=("Helvetica", 20), command=self.start_game)
        self.start_button.pack(pady=10)

        self.quit_button = tk.Button(self.frame, text="やめる", font=("Helvetica", 20), command=root.destroy)
        self.quit_button.pack(pady=10)

        self.game = None

    def start_game(self):
        self.frame.pack_forget()
        self.game = Tetris(self.root, on_game_over_callback=self.show_title)

    def show_title(self):
        if self.game:
            self.game.frame.pack_forget()
        self.frame.pack()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Tetris")
    root.resizable(False, False)
    title_screen = TitleScreen(root)
    root.mainloop()





