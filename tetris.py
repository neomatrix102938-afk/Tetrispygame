import pygame
import random
import sys

# 1. Initialize Pygame
pygame.init()

# Mobile-Optimized Layout Configurations
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 700  # Taller window to make room for touch buttons
GRID_SIZE = 24       # Slightly bigger blocks for smaller screens
COLUMNS = 10
ROWS = 20

# Centering the grid horizontally
X_OFFSET = (SCREEN_WIDTH - (COLUMNS * GRID_SIZE)) // 2
Y_OFFSET = 30

# Colors
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
LIGHT_GRAY = (80, 80, 80)
WHITE = (255, 255, 255)
DARK_BLUE = (20, 20, 40)

SHAPE_COLORS = [
    (0, 255, 255),   # Cyan
    (0, 0, 255),     # Blue
    (255, 165, 0),   # Orange
    (255, 255, 0),   # Yellow
    (0, 255, 0),     # Green
    (128, 0, 128),   # Purple
    (255, 0, 0)      # Red
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]]
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mobile Tetris Concept")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 18, bold=True)
large_font = pygame.font.SysFont("Courier New", 28, bold=True)

# Define Touch Buttons Layout (X, Y, Width, Height)
button_w, button_h = 70, 60
pad_y = 540  # Vertical position of the control pad

btn_left  = pygame.Rect(30, pad_y, button_w, button_h)
btn_right = pygame.Rect(190, pad_y, button_w, button_h)
btn_down  = pygame.Rect(110, pad_y + 40, button_w, button_h)
btn_rot   = pygame.Rect(110, pad_y - 30, button_w, button_h)
btn_drop  = pygame.Rect(290, pad_y, button_w + 10, button_h) # Hard Drop / Instant

class Tetris:
    def __init__(self):
        self.grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.new_piece()

    def new_piece(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.current_shape = SHAPES[self.shape_idx]
        self.color = SHAPE_COLORS[self.shape_idx]
        self.piece_x = COLUMNS // 2 - len(self.current_shape[0]) // 2
        self.piece_y = 0
        if self.check_collision(self.piece_x, self.piece_y, self.current_shape):
            self.game_over = True

    def check_collision(self, x, y, shape):
        for r_idx, row in enumerate(shape):
            for c_idx, cell in enumerate(row):
                if cell:
                    next_x = x + c_idx
                    next_y = y + r_idx
                    if next_x < 0 or next_x >= COLUMNS or next_y >= ROWS:
                        return True
                    if next_y >= 0 and self.grid[next_y][next_x]:
                        return True
        return False

    def lock_piece(self):
        for r_idx, row in enumerate(self.current_shape):
            for c_idx, cell in enumerate(row):
                if cell:
                    self.grid[self.piece_y + r_idx][self.piece_x + c_idx] = self.color
        self.clear_lines()
        self.new_piece()

    def clear_lines(self):
        lines_cleared = 0
        for r in range(ROWS - 1, -1, -1):
            if 0 not in self.grid[r]:
                del self.grid[r]
                self.grid.insert(0, [0 for _ in range(COLUMNS)])
                lines_cleared += 1
        if lines_cleared > 0:
            self.score += (lines_cleared ** 2) * 100

    def move(self, dx):
        if not self.game_over and not self.check_collision(self.piece_x + dx, self.piece_y, self.current_shape):
            self.piece_x += dx

    def drop(self):
        if not self.game_over:
            if not self.check_collision(self.piece_x, self.piece_y + 1, self.current_shape):
                self.piece_y += 1
            else:
                self.lock_piece()

    def hard_drop(self):
        while not self.game_over and not self.check_collision(self.piece_x, self.piece_y + 1, self.current_shape):
            self.piece_y += 1
        self.lock_piece()

    def rotate(self):
        if not self.game_over:
            rotated = [list(x) for x in zip(*self.current_shape[::-1])]
            if not self.check_collision(self.piece_x, self.piece_y, rotated):
                self.current_shape = rotated

    def draw(self, surface):
        for r in range(ROWS):
            for c in range(COLUMNS):
                rect = pygame.Rect(X_OFFSET + c * GRID_SIZE, Y_OFFSET + r * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                if self.grid[r][c]:
                    pygame.draw.rect(surface, self.grid[r][c], rect)
                else:
                    pygame.draw.rect(surface, GRAY, rect, 1)

        for r_idx, row in enumerate(self.current_shape):
            for c_idx, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        X_OFFSET + (self.piece_x + c_idx) * GRID_SIZE,
                        Y_OFFSET + (self.piece_y + r_idx) * GRID_SIZE,
                        GRID_SIZE, GRID_SIZE
                    )
                    pygame.draw.rect(surface, self.color, rect)

        board_border = pygame.Rect(X_OFFSET, Y_OFFSET, COLUMNS * GRID_SIZE, ROWS * GRID_SIZE)
        pygame.draw.rect(surface, WHITE, board_border, 2)

game = Tetris()
fall_time = 0
fall_speed = 500

running = True
while running:
    screen.fill(BLACK)
    delta_time = clock.tick(60)
    fall_time += delta_time

    if fall_time >= fall_speed:
        game.drop()
        fall_time = 0

    fall_speed = max(100, 500 - (game.score // 500) * 50)

    # 2. Touch and Click Input Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Detect MOUSEBUTTONDOWN or FINGERDOWN (Pygame uses MOUSE events for basic mobile taps)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            if game.game_over:
                game = Tetris()
            else:
                # Check bounding boxes of the virtual D-pad buttons
                if btn_left.collidepoint(mouse_pos):
                    game.move(-1)
                elif btn_right.collidepoint(mouse_pos):
                    game.move(1)
                elif btn_rot.collidepoint(mouse_pos):
                    game.rotate()
                elif btn_down.collidepoint(mouse_pos):
                    game.drop()
                elif btn_drop.collidepoint(mouse_pos):
                    game.hard_drop()

        # Keyboard alternative inputs still active
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: game.move(-1)
            elif event.key == pygame.K_RIGHT: game.move(1)
            elif event.key == pygame.K_DOWN: game.drop()
            elif event.key == pygame.K_UP: game.rotate()
            elif event.key == pygame.K_SPACE: game.hard_drop()

    # 3. Draw Game Interface
    game.draw(screen)

    # Render Score Metrics Header
    score_txt = font.render(f"SCORE: {game.score}", True, WHITE)
    screen.fill(BLACK, (0, 0, SCREEN_WIDTH, Y_OFFSET)) # Clean header spacer
    screen.blit(score_txt, (X_OFFSET, 8))

    # --- DRAW MOBILE TOUCH CONTROLS PANEL ---
    # Bottom control tray background frame
    pygame.draw.rect(screen, DARK_BLUE, (0, 500, SCREEN_WIDTH, 200))
    pygame.draw.line(screen, WHITE, (0, 500), (SCREEN_WIDTH, 500), 2)

    # Render Buttons visually
    for btn, label in [(btn_left, "<"), (btn_right, ">"), (btn_down, "v"), (btn_rot, "ROT"), (btn_drop, "DROP")]:
        pygame.draw.rect(screen, LIGHT_GRAY, btn, 0, 5)
        pygame.draw.rect(screen, WHITE, btn, 2, 5)
        text_surf = font.render(label, True, WHITE)
        text_rect = text_surf.get_rect(center=btn.center)
        screen.blit(text_surf, text_rect)

    if game.game_over:
        # Transparent overlay over grid area
        overlay = pygame.Surface((COLUMNS * GRID_SIZE, ROWS * GRID_SIZE))
        overlay.fill(BLACK)
        overlay.set_alpha(200)
        screen.blit(overlay, (X_OFFSET, Y_OFFSET))
        
        go_txt = large_font.render("GAME OVER", True, (255, 0, 0))
        res_txt = font.render("Tap Screen to Restart", True, WHITE)
        screen.blit(go_txt, go_txt.get_rect(center=(SCREEN_WIDTH // 2, Y_OFFSET + 180)))
        screen.blit(res_txt, res_txt.get_rect(center=(SCREEN_WIDTH // 2, Y_OFFSET + 230)))

    pygame.display.flip()

pygame.quit()
sys.exit()
