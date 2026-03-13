import pygame
import sys
import math
import random

"""
PONG — single-file Python game built with pygame.
Controls: Left = W/S   Right = UP/DOWN   Serve = ENTER

File structure:
  1. Constants       – tweak these to change game feel
  2. State           – everything that changes at runtime
  3. reset()         – re-centers ball and paddles
  4. launch_ball()   – randomizes starting velocity
  5. update()        – moves objects, checks collisions/scoring
  6. draw()          – renders the current frame
  7. Main loop       – event handling + game loop
"""

pygame.init()

# ── 1. CONSTANTS
W, H = 900, 600
PADDLE_W = 14
PADDLE_H = 90
INSET = 30
BALL_SIZE = 16
PADDLE_SPEED = 6
WIN_SCORE = 7
INIT_SPEED = 5.0
SPEED_INC = 0.4
MAX_SPEED = 14.0
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
YELLOW = (255, 255, 0)
DIM = (200, 200, 200)
GREY = (100, 100, 100)

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Courier", 64, bold=True)
font_mid = pygame.font.SysFont("Courier", 40, bold=True)
font_small = pygame.font.SysFont("Courier", 22, bold=True)
font_hint = pygame.font.SysFont("Courier", 13)


# ── 2. STATE────
lp_y = rp_y = (H - PADDLE_H) // 2  # paddle Y positions
bx = by = 0.0                       # ball center
bvx = bvy = 0.0                     # ball velocity
l_score = r_score = 0
state = "waiting"                   # waiting | playing | gameover
rng = random.Random()


# ── 3. RESET────
def reset():
    global lp_y, rp_y, bx, by, bvx, bvy
    bx, by = W / 2, H / 2
    bvx = bvy = 0
    lp_y = rp_y = (H - PADDLE_H) // 2


# ── 4. LAUNCH BALL
def launch_ball():
    global bvx, bvy
    angle = math.radians(rng.randint(-20, 20))
    d = 1 if rng.random() > 0.5 else -1
    bvx = d * INIT_SPEED * math.cos(angle)
    bvy = INIT_SPEED * math.sin(angle)


# ── 5. UPDATE───
def update(keys):
    global lp_y, rp_y, bx, by, bvx, bvy
    global l_score, r_score, state

    if keys[pygame.K_w] and lp_y > 0:
        lp_y -= PADDLE_SPEED
    if keys[pygame.K_s] and lp_y < H - PADDLE_H:
        lp_y += PADDLE_SPEED
    if keys[pygame.K_UP] and rp_y > 0:
        rp_y -= PADDLE_SPEED
    if keys[pygame.K_DOWN] and rp_y < H - PADDLE_H:
        rp_y += PADDLE_SPEED

    if state != "playing":
        return

    bx += bvx
    by += bvy

    # Wall bounce
    if by - BALL_SIZE / 2 <= 0:
        by = BALL_SIZE / 2
        bvy = abs(bvy)
    if by + BALL_SIZE / 2 >= H:
        by = H - BALL_SIZE / 2
        bvy = -abs(bvy)

    # Left paddle collision
    l_face = INSET + PADDLE_W
    if (bvx < 0
            and bx - BALL_SIZE / 2 <= l_face
            and bx + BALL_SIZE / 2 >= INSET
            and lp_y <= by <= lp_y + PADDLE_H):
        bx = l_face + BALL_SIZE / 2
        bvx = abs(bvx)
        bvy += calcDeflectionAngle(by, lp_y)
        speed_up()

    # Right paddle collision
    r_face = W - INSET - PADDLE_W
    if (bvx > 0
            and bx + BALL_SIZE / 2 >= r_face
            and bx - BALL_SIZE / 2 <= W - INSET
            and rp_y <= by <= rp_y + PADDLE_H):
        bx = r_face - BALL_SIZE / 2
        bvx = -abs(bvx)
        bvy += calcDeflectionAngle(by, rp_y)
        speed_up()

    # Scoring
    if bx + BALL_SIZE / 2 < 0:
        r_score += 1
        next_point()
    if bx - BALL_SIZE / 2 > W:
        l_score += 1
        next_point()


def calcDeflectionAngle(ball_cy, paddle_top):
    return ((ball_cy - paddle_top) / PADDLE_H - 0.5) * 4.0


def speed_up():
    global bvx, bvy
    spd = math.sqrt(bvx**2 + bvy**2)
    scale = min(spd + SPEED_INC, MAX_SPEED) / spd
    bvx *= scale
    bvy *= scale


def next_point():
    global state
    reset()
    won = l_score >= WIN_SCORE or r_score >= WIN_SCORE
    state = "gameover" if won else "waiting"


# ── 6. DRAW─────
def centered(text, y, font, color):
    s = font.render(text, True, color)
    screen.blit(s, ((W - s.get_width()) // 2, y))


def draw():
    screen.fill(BLACK)

    # Dashed center line
    for yy in range(0, H, 24):
        pygame.draw.rect(screen, GREY, (W // 2 - 1, yy, 2, 12))

    # Scores
    ls = font_big.render(str(l_score), True, WHITE)
    rs = font_big.render(str(r_score), True, WHITE)
    screen.blit(ls, (W // 2 - ls.get_width() - 40, 20))
    screen.blit(rs, (W // 2 + 40, 20))

    # Paddles & ball
    pygame.draw.rect(
        screen, WHITE, (INSET, lp_y, PADDLE_W, PADDLE_H), border_radius=4
    )
    pygame.draw.rect(
        screen, WHITE,
        (W - INSET - PADDLE_W, rp_y, PADDLE_W, PADDLE_H), border_radius=4
    )
    pygame.draw.circle(screen, WHITE, (int(bx), int(by)), BALL_SIZE // 2)

    # Overlay messages
    if state == "waiting":
        centered("Press ENTER to serve", H // 2 + 30, font_small, DIM)
    elif state == "gameover":
        winner = "LEFT" if l_score >= WIN_SCORE else "RIGHT"
        centered(f"{winner} PLAYER WINS!", H // 2 - 20, font_mid, YELLOW)
        centered("Press ENTER to play again", H // 2 + 35, font_small, DIM)

    # Control hints
    screen.blit(font_hint.render("Left: W/S", True, GREY), (20, H - 20))
    rh = font_hint.render("Right: \u2191/\u2193", True, GREY)
    screen.blit(rh, (W - rh.get_width() - 20, H - 20))

    pygame.display.flip()


# ── 7. MAIN LOOP
reset()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if state == "waiting":
                launch_ball()
                state = "playing"
            elif state == "gameover":
                l_score = r_score = 0
                reset()
                state = "waiting"

    update(pygame.key.get_pressed())
    draw()
    clock.tick(FPS)
