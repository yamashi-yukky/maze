import pygame as pg
import random
import sys

pg.mixer.init()

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 30, 30
CELL_SIZE = WIDTH // COLS

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ORANGE = (255,165,0)

replay_img = pg.image.load("originalgame/images/replaybtn.png")
pushFlag = False
ignore_wall = False
page = 1
screen = pg.display.set_mode((WIDTH, HEIGHT))

def button_to_jump(btn, newpage):
    global page, pushFlag

    mdown = pg.mouse.get_pressed()
    (mx, my) = pg.mouse.get_pos()
    if mdown[0]:
        if btn.collidepoint(mx, my) and pushFlag == False:
            page = newpage
            pushFlag = True
        else:
            pushFlag = False

def draw_grid(screen):
    for x in range(0, WIDTH, CELL_SIZE):
        pg.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pg.draw.line(screen, BLACK, (0, y), (WIDTH, y))

def carve_maze(grid, x, y):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    random.shuffle(directions)

    for dx, dy in directions:
        nx, ny = x + dx * 2, y + dy * 2

        if 0 <= nx < COLS and 0 <= ny < ROWS and grid[ny][nx] == 1:
            grid[ny][nx] = 0
            grid[y + dy][x + dx] = 0
            carve_maze(grid, nx, ny)

def generate_maze():
    max_attempts = 1000  # 最大試行回数
    attempts = 0

    while attempts < max_attempts:
        maze = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        start_x, start_y = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
        end_x, end_y = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)
        item_x, item_y = random.randint(0, COLS - 1), random.randint(0, ROWS - 1)

        if maze[start_y][start_x] == 1 and maze[end_y][end_x] == 1 and maze[item_y][item_x] == 1:
            maze[start_y][start_x] = 0
            maze[end_y][end_x] = 0
            maze[item_y][item_x] = 2
            carve_maze(maze, start_x, start_y)

            if is_accessible(maze, (start_x, start_y), (end_x, end_y)) and is_accessible(maze, (start_x, start_y), (item_x, item_y)):
                return maze, (start_x, start_y), (end_x, end_y), (item_x, item_y)

        attempts += 1
    
    return None, None, None, None

def is_accessible(maze, start, goal):
    queue = [start]
    visited = set()
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    while queue:
        x, y = queue.pop(0)
        if (x, y) == goal:
            return True
        if (x, y) in visited:
            continue
        visited.add((x, y))

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 1 and (nx, ny) not in visited:
                queue.append((nx, ny))

    return False

def draw_maze(screen, maze, start, end, player, item, ignore_wall):
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if (x, y) == start:
                pg.draw.rect(screen, GREEN, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif (x, y) == end:
                pg.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif (x, y) == player:
                pg.draw.rect(screen, YELLOW, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif (x, y) == item:
                pg.draw.rect(screen, ORANGE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif cell == 1 and not ignore_wall:
                pg.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif cell == 2:
                pg.draw.rect(screen, GRAY, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        if player == item:
            ignore_wall = True
            for y in range(ROWS):
                for x in range(COLS):
                    maze[y][x] = 0

def gameclear(screen):
    screen.fill(WHITE)
    font = pg.font.Font(None, 75)
    text = font.render("GAME CLEAR", True, RED)
    screen.blit(text, (60, 150))
    pg.mixer.music.load("originalgame/sounds/sounds/nc294214.mp3")

    # リセットボタンを表示する
    replay_rect = screen.blit(replay_img, (WIDTH // 2 - 50, HEIGHT // 2))
    pg.display.flip()

    # ボタンがクリックされたらリスタート
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if replay_rect.collidepoint(event.pos):
                    return True
        pg.time.Clock().tick(30)

def gamereset():
    return generate_maze()

def start_screen():#スタート画面
    screen.fill(WHITE)
    font = pg.font.Font(None, 64)
    text = font.render("MAZE CHALLENGE", True, BLACK)
    screen.blit(text, (100, 150))
    expression = pg.font.Font(None, 32)
    text_1 = expression.render("red goal", True, BLACK)
    screen.blit(text_1, (400, 250))
    text_2 = expression.render("yellow player", True, BLACK)
    screen.blit(text_2, (400, 300))
    text_3 = expression.render("orange item", True, BLACK)
    screen.blit(text_3, (400, 350))

    start_button = pg.Rect(WIDTH // 2 - 50, HEIGHT // 2, 100, 50)
    pg.draw.rect(screen, GREEN, start_button)
    button_font = pg.font.Font(None, 15)
    button_text = button_font.render("PRESS TO START", True, BLACK)
    button_text_rect = button_text.get_rect(center=start_button.center)
    screen.blit(button_text, button_text_rect)
    pg.display.flip()

    pg.mixer.music.load("originalgame/sounds/sounds/hitori.wav")
    pg.mixer.music.play(-1)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return
        pg.time.Clock().tick(30)

def gamestage():
    global ignore_wall
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption('迷路にチャレンジ!!')

    start_screen()

    pg.mixer.music.load("originalgame/sounds/sounds/Puzzle.mp3")
    pg.mixer.music.play(-1)

    maze, start, end, item = generate_maze()
    player = start
    ignore_wall = False

    running = True
    game_clear = False

    clock = pg.time.Clock()

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    new_position = (player[0], player[1] - 1)
                    if 0 <= new_position[1] < ROWS and maze[new_position[1]][new_position[0]] != 1:
                        player = new_position
                elif event.key == pg.K_DOWN:
                    new_position = (player[0], player[1] + 1)
                    if 0 <= new_position[1] < ROWS and maze[new_position[1]][new_position[0]] != 1:
                        player = new_position
                elif event.key == pg.K_LEFT:
                    new_position = (player[0] - 1, player[1])
                    if 0 <= new_position[0] < COLS and maze[new_position[1]][new_position[0]] != 1:
                        player = new_position
                elif event.key == pg.K_RIGHT:
                    new_position = (player[0] + 1, player[1])
                    if 0 <= new_position[0] < COLS and maze[new_position[1]][new_position[0]] != 1:
                        player = new_position

        screen.fill(WHITE)
        draw_grid(screen)
        draw_maze(screen, maze, start, end, player, item, ignore_wall)
        pg.display.flip()

        if player == end and not game_clear:
            game_clear = gameclear(screen)
            if game_clear:
                maze, start, end, item = gamereset()
                player = start
                game_clear = False
                pg.mixer.music.load("originalgame/sounds/sounds/Puzzle.mp3")
                pg.mixer.music.play(-1)

        clock.tick(15)
    
    pg.quit()

if __name__ == '__main__':
    gamestage()