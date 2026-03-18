import pygame
import sys
import math
import random
from enum import Enum

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
W, H = 1280, 720
PADDLE_W = 14
LPADDLE_MAXH = RPADDLE_MAXH = 120
LPADDLE_H = 120
RPADDLE_H = 120
BALL_SIZE = 16
LPADDLE_MAXS = RPADDLE_MAXS = 7
LPADDLE_SPEED = 7
RPADDLE_SPEED = 7
LENERGY_W = RENERGY_W = LMAX_ENERGY = RMAX_ENERGY = 80
ENERGY_H = 14
WIN_SCORE = 7
INIT_SPEED = 7.0
SPEED_INC = 0.6
MAX_SPEED = 16.0
FPS = 60

class DEBUFFS(Enum):
    SIZEDOWN = 1
    SPEEDDOWN = 2
    STAMINADOWN = 3

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
font_hint = pygame.font.SysFont("Courier", 13, bold=True)


# ── 2. STATE────
lp_x = rp_x = 30                    # paddle X positions
lp_y = rp_y = (H - 120) // 2        # paddle Y positions
bx = by = 0.0                       # ball center
bvx = bvy = 0.0                     # ball velocity
l_score = r_score = 0
state = "waiting"                   # waiting | playing | gameover
rng = random.Random()


# ── 3. RESET────
def reset():
    global lp_y, rp_y, bx, by, bvx, bvy
    global LPADDLE_MAXH, RPADDLE_MAXH
    global LPADDLE_MAXS, RPADDLE_MAXS
    global LMAX_ENERGY, RMAX_ENERGY
    global LPADDLE_H, RPADDLE_H
    bx, by = W / 2, H / 2
    bvx = bvy = 0
    lp_y = rp_y = (H - 120) // 2
    LPADDLE_MAXH = RPADDLE_MAXH = 120
    LPADDLE_MAXS = RPADDLE_MAXS = 7
    LMAX_ENERGY = RMAX_ENERGY = 80
    LPADDLE_H = LPADDLE_MAXH
    RPADDLE_H = RPADDLE_MAXH


# ── 4. LAUNCH BALL
def launch_ball():
    global bvx, bvy
    angle = math.radians(rng.randint(-20, 20))
    d = 1 if rng.random() > 0.5 else -1
    bvx = d * INIT_SPEED * math.cos(angle)
    bvy = INIT_SPEED * math.sin(angle)


# ── 5. UPDATE───
def update(keys):
    global lp_x, lp_y, rp_x, rp_y, bx, by, bvx, bvy
    global l_score, r_score, state
    global LPADDLE_SPEED, RPADDLE_SPEED
    global LENERGY_W, RENERGY_W
    global LPADDLE_H, RPADDLE_H

    if LPADDLE_H > LPADDLE_MAXH:
        LPADDLE_H = min(LPADDLE_H-0.1, LPADDLE_MAXH*2)
        lp_y += 0.05

    if RPADDLE_H > RPADDLE_MAXH:
        RPADDLE_H = min(RPADDLE_H-0.1, RPADDLE_MAXH*2)
        rp_y += 0.05

    if LENERGY_W and keys[pygame.K_LSHIFT]:
        LPADDLE_SPEED = LPADDLE_MAXS*2+1
        LENERGY_W = max(0, LENERGY_W-2)
    else:
        LPADDLE_SPEED = LPADDLE_MAXS
        if not keys[pygame.K_LSHIFT]: LENERGY_W = min(LENERGY_W+1, LMAX_ENERGY)
    
    if RENERGY_W and keys[pygame.K_RSHIFT]:
        RPADDLE_SPEED = RPADDLE_MAXS*2+1
        RENERGY_W = max(0, RENERGY_W-2)
    else:
        RPADDLE_SPEED = RPADDLE_MAXS
        if not keys[pygame.K_RSHIFT]: RENERGY_W = min(RENERGY_W+1, RMAX_ENERGY)

    if keys[pygame.K_a] and lp_x > 0:
        lp_x -= LPADDLE_SPEED
    if keys[pygame.K_d] and lp_x < W/2 - PADDLE_W - 64:
        lp_x += LPADDLE_SPEED
    if keys[pygame.K_LEFT] and rp_x < W/2 - PADDLE_W - 64:
        rp_x += RPADDLE_SPEED
    if keys[pygame.K_RIGHT] and rp_x > 0:
        rp_x -= RPADDLE_SPEED

    if keys[pygame.K_w] and lp_y > 0:
        lp_y -= LPADDLE_SPEED
    if keys[pygame.K_s] and lp_y < H - LPADDLE_H:
        lp_y += LPADDLE_SPEED
    if keys[pygame.K_UP] and rp_y > 0:
        rp_y -= RPADDLE_SPEED
    if keys[pygame.K_DOWN] and rp_y < H - RPADDLE_H:
        rp_y += RPADDLE_SPEED

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
    l_face = lp_x + PADDLE_W
    if (bvx < 0
            and bx - BALL_SIZE / 2 <= l_face
            and bx + BALL_SIZE / 2 >= lp_x
            and lp_y <= by <= lp_y + LPADDLE_H):
        bx = l_face + BALL_SIZE / 2
        bvx = abs(bvx)
        bvy += calcDeflectionAngle(by, lp_y, bx > W/2)
        speed_up()

    # Right paddle collision
    r_face = W - rp_x - PADDLE_W
    if (bvx > 0
            and bx + BALL_SIZE / 2 >= r_face
            and bx - BALL_SIZE / 2 <= W - rp_x
            and rp_y <= by <= rp_y + RPADDLE_H):
        bx = r_face - BALL_SIZE / 2
        bvx = -abs(bvx)
        bvy += calcDeflectionAngle(by, rp_y, bx > W/2)
        speed_up()

    # Scoring
    if bx + BALL_SIZE / 2 < 0:
        next_point(1)
    if bx - BALL_SIZE / 2 > W:
        next_point(0)


def calcDeflectionAngle(ball_cy, paddle_top, paddle):
    return ((ball_cy - paddle_top) / ((not paddle)*LPADDLE_H + paddle*RPADDLE_H) - 0.5) * 4.0


def speed_up():
    global bvx, bvy
    spd = math.sqrt(bvx**2 + bvy**2)
    scale = min(spd + SPEED_INC, MAX_SPEED) / spd
    bvx *= scale
    bvy *= scale


def next_point(player):
    global state
    global l_score, r_score
    global LPADDLE_MAXH, RPADDLE_MAXH
    global LPADDLE_H, RPADDLE_H
    global LPADDLE_MAXS, RPADDLE_MAXS
    global LMAX_ENERGY, RMAX_ENERGY

    l_score += not player
    r_score += player

    LPADDLE_MAXH = RPADDLE_MAXH = 120
    LPADDLE_MAXS = RPADDLE_MAXS = 7
    LMAX_ENERGY = RMAX_ENERGY = 80
    LPADDLE_H = LPADDLE_MAXH
    RPADDLE_H = RPADDLE_MAXH

    debuff = random.choice(list(DEBUFFS))
    match debuff:
        case DEBUFFS.SIZEDOWN:
            LPADDLE_MAXH /= (not player)+1
            RPADDLE_MAXH /= player+1
            LPADDLE_H = LPADDLE_MAXH
            RPADDLE_H = RPADDLE_MAXH
        case DEBUFFS.SPEEDDOWN:
            LPADDLE_MAXS /= (not player)+1
            RPADDLE_MAXS /= player+1
        case DEBUFFS.STAMINADOWN:
            LMAX_ENERGY /= (not player)+1
            RMAX_ENERGY /= player+1
        

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
        screen, WHITE, (lp_x, lp_y, PADDLE_W, LPADDLE_H), border_radius=4
    )
    lenergy = pygame.Surface((LENERGY_W, ENERGY_H))
    lenergy.fill(WHITE)
    lenergy.set_alpha(128)
    screen.blit(lenergy, (lp_x - LENERGY_W/2 + PADDLE_W/2, lp_y - 20))
    pygame.draw.rect(
        screen, WHITE,
        (W - rp_x - PADDLE_W, rp_y, PADDLE_W, RPADDLE_H), border_radius=4
    )
    renergy = pygame.Surface((RENERGY_W, ENERGY_H))
    renergy.fill(WHITE)
    renergy.set_alpha(128)
    screen.blit(renergy, (W - rp_x - RENERGY_W/2 - PADDLE_W/2, rp_y - 20))
    pygame.draw.circle(screen, WHITE, (int(bx), int(by)), BALL_SIZE // 2)

    # Overlay messages
    if state == "waiting":
        centered("Press ENTER to serve", H // 2 + 30, font_small, DIM)
    elif state == "gameover":
        winner = "LEFT" if l_score >= WIN_SCORE else "RIGHT"
        centered(f"{winner} PLAYER WINS!", H // 2 - 20, font_mid, YELLOW)
        centered("Press ENTER to play again", H // 2 + 35, font_small, DIM)

    # Control hints
    screen.blit(font_hint.render("Left: W/A/S/D", True, WHITE), (20, H - 60))
    screen.blit(font_hint.render("Left: LSHIFT", True, WHITE), (20, H - 40))
    screen.blit(font_hint.render("Left: LCTRL", True, WHITE), (20, H - 20))
    rh = font_hint.render("Right: ↑/←/↓/→", True, WHITE)
    screen.blit(rh, (W - rh.get_width() - 20, H - 60))
    rh2 = font_hint.render("Right: RSHIFT", True, WHITE)
    screen.blit(rh2, (W - rh2.get_width() - 20, H - 40))
    rh3 = font_hint.render("Right: RCTRL", True, WHITE)
    screen.blit(rh3, (W - rh3.get_width() - 20, H - 20))

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
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LCTRL:
                if LPADDLE_H < 240:
                    LPADDLE_H += 5
                    lp_y -= 2.5
            if event.key == pygame.K_RCTRL:
                if RPADDLE_H < 240:
                    RPADDLE_H += 5
                    rp_y -= 2.5

    update(pygame.key.get_pressed())
    draw()
    clock.tick(FPS)
