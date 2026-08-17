import os
import sys
import random
import math

# ─────────────────────────────────────────
# CODESPACES / HEADLESS SETUP
# ─────────────────────────────────────────

if not os.environ.get("DISPLAY"):
    os.environ["DISPLAY"] = ":99"

if not os.environ.get("XDG_RUNTIME_DIR"):
    os.environ["XDG_RUNTIME_DIR"] = "/tmp/runtime-vscode"
    os.makedirs("/tmp/runtime-vscode", exist_ok=True)

os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame


# ─────────────────────────────────────────
# INITIALISE
# ─────────────────────────────────────────

pygame.init()

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
FPS = 60

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption("DODGE RUSH")

clock = pygame.time.Clock()


# ─────────────────────────────────────────
# COLOURS
# ─────────────────────────────────────────

BLACK = (8, 8, 18)
WHITE = (255, 255, 255)

RED = (255, 60, 70)
GREEN = (50, 255, 120)
BLUE = (70, 170, 255)
YELLOW = (255, 220, 60)
PURPLE = (190, 80, 255)
CYAN = (50, 240, 255)
ORANGE = (255, 130, 40)

DARK_RED = (70, 10, 20)
DARK_BLUE = (10, 20, 50)


# ─────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────

font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 24)
big_font = pygame.font.Font(None, 70)


# ─────────────────────────────────────────
# GAME SETTINGS
# ─────────────────────────────────────────

PLAYER_SIZE = 30

PLAYER_SPEED = 240
DASH_SPEED = 700
DASH_DURATION = 0.15
DASH_COOLDOWN = 1.2

MAX_LIVES = 3

COIN_SIZE = 14

ENEMY_SIZE = 25

POWERUP_SIZE = 20
POWERUP_DURATION = 5


# ─────────────────────────────────────────
# GAME VARIABLES
# ─────────────────────────────────────────

score = 0
high_score = 0

lives = MAX_LIVES

combo = 1
combo_timer = 0

level = 1

game_over = False

screen_shake = 0

flash_timer = 0


# ─────────────────────────────────────────
# PLAYER
# ─────────────────────────────────────────

player = pygame.Rect(
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT // 2,
    PLAYER_SIZE,
    PLAYER_SIZE
)

dash_timer = 0
dash_cooldown = 0

speed_boost_timer = 0

invincible_timer = 0


# ─────────────────────────────────────────
# OBJECT LISTS
# ─────────────────────────────────────────

coins = []
enemies = []
particles = []
powerups = []


# ─────────────────────────────────────────
# PARTICLE
# ─────────────────────────────────────────

class Particle:

    def __init__(self, x, y, color):

        self.x = x
        self.y = y

        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(50, 180)

        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.life = random.uniform(0.3, 0.8)

        self.max_life = self.life

        self.size = random.randint(2, 5)

        self.color = color

    def update(self, dt):

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.vx *= 0.96
        self.vy *= 0.96

        self.life -= dt

    def draw(self):

        if self.life <= 0:
            return

        alpha = self.life / self.max_life

        color = tuple(
            int(c * alpha)
            for c in self.color
        )

        pygame.draw.circle(
            screen,
            color,
            (int(self.x), int(self.y)),
            self.size
        )


def create_particles(x, y, color, amount=12):

    for _ in range(amount):
        particles.append(
            Particle(x, y, color)
        )


# ─────────────────────────────────────────
# RANDOM POSITION
# ─────────────────────────────────────────

def random_position(size):

    return pygame.Rect(
        random.randint(20, SCREEN_WIDTH - size - 20),
        random.randint(50, SCREEN_HEIGHT - size - 20),
        size,
        size
    )


# ─────────────────────────────────────────
# SPAWN COIN
# ─────────────────────────────────────────

def spawn_coin():

    for _ in range(50):

        coin = random_position(COIN_SIZE)

        if not coin.colliderect(player):
            coins.append(coin)
            return


# ─────────────────────────────────────────
# SPAWN ENEMY
# ─────────────────────────────────────────

def spawn_enemy():

    for _ in range(50):

        enemy = random_position(ENEMY_SIZE)

        # Don't spawn directly on player.
        if enemy.centerx - player.centerx > 100:
            enemies.append(enemy)
            return


# ─────────────────────────────────────────
# SPAWN POWERUP
# ─────────────────────────────────────────

def spawn_powerup():

    powerup = random_position(POWERUP_SIZE)

    powerups.append({
        "rect": powerup,
        "type": "speed",
        "timer": 8
    })


# ─────────────────────────────────────────
# RESET GAME
# ─────────────────────────────────────────

def reset_game():

    global score
    global lives
    global combo
    global combo_timer
    global level
    global game_over
    global dash_timer
    global dash_cooldown
    global speed_boost_timer
    global invincible_timer
    global screen_shake
    global flash_timer

    score = 0
    lives = MAX_LIVES

    combo = 1
    combo_timer = 0

    level = 1

    game_over = False

    dash_timer = 0
    dash_cooldown = 0

    speed_boost_timer = 0
    invincible_timer = 0

    screen_shake = 0
    flash_timer = 0

    player.center = (
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2
    )

    coins.clear()
    enemies.clear()
    particles.clear()
    powerups.clear()

    for _ in range(4):
        spawn_coin()

    for _ in range(2):
        spawn_enemy()


# ─────────────────────────────────────────
# ADD SCORE
# ─────────────────────────────────────────

def add_score(amount):

    global score
    global combo
    global combo_timer
    global high_score
    global level
    global screen_shake

    score += amount * combo

    high_score = max(high_score, score)

    combo += 1
    combo_timer = 2.5

    screen_shake = 4

    # Increase difficulty every 10 points.
    new_level = score // 10 + 1

    if new_level > level:

        level = new_level

        create_particles(
            player.centerx,
            player.centery,
            PURPLE,
            30
        )

        spawn_enemy()


# ─────────────────────────────────────────
# PLAYER MOVEMENT
# ─────────────────────────────────────────

def update_player(dt):

    global dash_timer
    global dash_cooldown

    keys = pygame.key.get_pressed()

    direction = pygame.Vector2(0, 0)

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        direction.x -= 1

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        direction.x += 1

    if keys[pygame.K_UP] or keys[pygame.K_w]:
        direction.y -= 1

    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        direction.y += 1

    if direction.length_squared() > 0:
        direction = direction.normalize()

    speed = PLAYER_SPEED

    if speed_boost_timer > 0:
        speed *= 1.8

    # DASH
    if dash_timer > 0:

        speed = DASH_SPEED

        dash_timer -= dt

        create_particles(
            player.centerx,
            player.centery,
            CYAN,
            1
        )

    player.x += int(direction.x * speed * dt)
    player.y += int(direction.y * speed * dt)

    player.clamp_ip(screen.get_rect())

    dash_cooldown = max(
        0,
        dash_cooldown - dt
    )


# ─────────────────────────────────────────
# ENEMY MOVEMENT
# ─────────────────────────────────────────

def update_enemies(dt):

    global level

    for enemy in enemies:

        direction = pygame.Vector2(
            player.centerx - enemy.centerx,
            player.centery - enemy.centery
        )

        if direction.length_squared() > 0:

            direction = direction.normalize()

            speed = 60 + level * 10

            enemy.x += int(direction.x * speed * dt)
            enemy.y += int(direction.y * speed * dt)


# ─────────────────────────────────────────
# COIN COLLISION
# ─────────────────────────────────────────

def update_coins():

    for coin in coins[:]:

        if player.colliderect(coin):

            coins.remove(coin)

            add_score(1)

            create_particles(
                coin.centerx,
                coin.centery,
                YELLOW,
                15
            )

            # Spawn another coin.
            spawn_coin()


# ─────────────────────────────────────────
# POWERUPS
# ─────────────────────────────────────────

def update_powerups(dt):

    global speed_boost_timer

    for powerup in powerups[:]:

        powerup["timer"] -= dt

        if powerup["timer"] <= 0:

            powerups.remove(powerup)

            continue

        if player.colliderect(
            powerup["rect"]
        ):

            powerups.remove(powerup)

            speed_boost_timer = POWERUP_DURATION

            create_particles(
                player.centerx,
                player.centery,
                BLUE,
                25
            )


# ─────────────────────────────────────────
# ENEMY COLLISION
# ─────────────────────────────────────────

def check_enemy_collisions():

    global lives
    global game_over
    global invincible_timer
    global screen_shake
    global flash_timer

    if invincible_timer > 0:
        return

    for enemy in enemies:

        if player.colliderect(enemy):

            lives -= 1

            invincible_timer = 2

            screen_shake = 15

            flash_timer = 0.25

            create_particles(
                player.centerx,
                player.centery,
                RED,
                40
            )

            # Push enemy away.
            direction = pygame.Vector2(
                enemy.centerx - player.centerx,
                enemy.centery - player.centery
            )

            if direction.length_squared() == 0:
                direction = pygame.Vector2(1, 0)

            direction = direction.normalize()

            enemy.x += int(direction.x * 80)
            enemy.y += int(direction.y * 80)

            if lives <= 0:
                game_over = True

            return


# ─────────────────────────────────────────
# PARTICLES
# ─────────────────────────────────────────

def update_particles(dt):

    for particle in particles[:]:

        particle.update(dt)

        if particle.life <= 0:
            particles.remove(particle)


# ─────────────────────────────────────────
# DIFFICULTY / POWERUPS
# ─────────────────────────────────────────

powerup_spawn_timer = 5


def update_spawning(dt):

    global powerup_spawn_timer

    powerup_spawn_timer -= dt

    if powerup_spawn_timer <= 0:

        if len(powerups) == 0:
            spawn_powerup()

        powerup_spawn_timer = random.uniform(
            6,
            10
        )

    # More enemies at higher levels.
    desired_enemies = min(
        2 + level // 2,
        8
    )

    while len(enemies) < desired_enemies:
        spawn_enemy()


# ─────────────────────────────────────────
# UPDATE TIMERS
# ─────────────────────────────────────────

def update_timers(dt):

    global combo
    global combo_timer
    global speed_boost_timer
    global invincible_timer
    global screen_shake
    global flash_timer

    combo_timer -= dt

    if combo_timer <= 0:
        combo = 1

    speed_boost_timer = max(
        0,
        speed_boost_timer - dt
    )

    invincible_timer = max(
        0,
        invincible_timer - dt
    )

    screen_shake = max(
        0,
        screen_shake - 30 * dt
    )

    flash_timer = max(
        0,
        flash_timer - dt
    )


# ─────────────────────────────────────────
# DRAW GRID
# ─────────────────────────────────────────

def draw_background():

    screen.fill(BLACK)

    # Grid
    for x in range(0, SCREEN_WIDTH, 40):

        pygame.draw.line(
            screen,
            (18, 18, 35),
            (x, 0),
            (x, SCREEN_HEIGHT)
        )

    for y in range(0, SCREEN_HEIGHT, 40):

        pygame.draw.line(
            screen,
            (18, 18, 35),
            (0, y),
            (SCREEN_WIDTH, y)
        )


# ─────────────────────────────────────────
# DRAW PLAYER
# ─────────────────────────────────────────

def draw_player():

    # Flicker while invincible.
    if invincible_timer > 0:

        if int(invincible_timer * 10) % 2 == 0:
            return

    color = BLUE

    if speed_boost_timer > 0:
        color = CYAN

    pygame.draw.rect(
        screen,
        color,
        player,
        border_radius=8
    )

    # Player glow.
    pygame.draw.rect(
        screen,
        WHITE,
        player,
        2,
        border_radius=8
    )


# ─────────────────────────────────────────
# DRAW COINS
# ─────────────────────────────────────────

def draw_coins():

    for coin in coins:

        pygame.draw.circle(
            screen,
            YELLOW,
            coin.center,
            COIN_SIZE // 2
        )

        pygame.draw.circle(
            screen,
            WHITE,
            coin.center,
            COIN_SIZE // 2,
            2
        )


# ─────────────────────────────────────────
# DRAW ENEMIES
# ─────────────────────────────────────────

def draw_enemies():

    for enemy in enemies:

        pygame.draw.rect(
            screen,
            RED,
            enemy,
            border_radius=6
        )

        # Enemy eyes.
        pygame.draw.circle(
            screen,
            WHITE,
            (enemy.x + 7, enemy.y + 8),
            3
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (enemy.x + 18, enemy.y + 8),
            3
        )


# ─────────────────────────────────────────
# DRAW POWERUPS
# ─────────────────────────────────────────

def draw_powerups():

    for powerup in powerups:

        rect = powerup["rect"]

        pygame.draw.rect(
            screen,
            CYAN,
            rect,
            border_radius=5
        )

        # Lightning symbol.
        pygame.draw.polygon(
            screen,
            WHITE,
            [
                (rect.centerx + 2, rect.y + 2),
                (rect.centerx - 4, rect.centery),
                (rect.centerx, rect.centery),
                (rect.centerx - 3, rect.bottom - 2),
                (rect.centerx + 5, rect.centery - 3),
                (rect.centerx + 1, rect.centery - 3)
            ]
        )


# ─────────────────────────────────────────
# DRAW HUD
# ─────────────────────────────────────────

def draw_hud():

    score_surface = font.render(
        f"SCORE  {score}",
        True,
        WHITE
    )

    level_surface = font.render(
        f"LEVEL  {level}",
        True,
        PURPLE
    )

    combo_surface = font.render(
        f"x{combo} COMBO",
        True,
        YELLOW
    )

    screen.blit(
        score_surface,
        (12, 10)
    )

    screen.blit(
        level_surface,
        (12, 40)
    )

    if combo > 1:

        screen.blit(
            combo_surface,
            (
                SCREEN_WIDTH // 2 -
                combo_surface.get_width() // 2,
                10
            )
        )

    # Lives
    for i in range(MAX_LIVES):

        color = RED if i < lives else (60, 30, 35)

        pygame.draw.circle(
            screen,
            color,
            (
                SCREEN_WIDTH - 25 - i * 25,
                22
            ),
            8
        )

    # Dash bar
    bar_x = 12
    bar_y = SCREEN_HEIGHT - 22
    bar_width = 120
    bar_height = 8

    pygame.draw.rect(
        screen,
        (50, 50, 60),
        (
            bar_x,
            bar_y,
            bar_width,
            bar_height
        )
    )

    if dash_cooldown <= 0:

        dash_progress = 1

    else:

        dash_progress = 1 - (
            dash_cooldown / DASH_COOLDOWN
        )

    pygame.draw.rect(
        screen,
        CYAN,
        (
            bar_x,
            bar_y,
            int(bar_width * dash_progress),
            bar_height
        )
    )

    dash_text = small_font.render(
        "SPACE = DASH",
        True,
        WHITE
    )

    screen.blit(
        dash_text,
        (
            bar_x,
            SCREEN_HEIGHT - 45
        )
    )


# ─────────────────────────────────────────
# GAME OVER
# ─────────────────────────────────────────

def draw_game_over():

    overlay = pygame.Surface(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    overlay.set_alpha(190)
    overlay.fill(DARK_RED)

    screen.blit(
        overlay,
        (0, 0)
    )

    title = big_font.render(
        "GAME OVER",
        True,
        WHITE
    )

    score_text = font.render(
        f"Score: {score}",
        True,
        YELLOW
    )

    high_text = font.render(
        f"High Score: {high_score}",
        True,
        CYAN
    )

    restart_text = font.render(
        "Press R to restart",
        True,
        WHITE
    )

    screen.blit(
        title,
        title.get_rect(
            center=(SCREEN_WIDTH // 2, 160)
        )
    )

    screen.blit(
        score_text,
        score_text.get_rect(
            center=(SCREEN_WIDTH // 2, 225)
        )
    )

    screen.blit(
        high_text,
        high_text.get_rect(
            center=(SCREEN_WIDTH // 2, 260)
        )
    )

    screen.blit(
        restart_text,
        restart_text.get_rect(
            center=(SCREEN_WIDTH // 2, 320)
        )
    )


# ─────────────────────────────────────────
# EVENT HANDLING
# ─────────────────────────────────────────

running = True

def handle_events():

    global running
    global dash_timer
    global dash_cooldown

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_r and game_over:
                reset_game()

            # Dash
            if (
                event.key == pygame.K_SPACE
                and not game_over
                and dash_cooldown <= 0
            ):

                dash_timer = DASH_DURATION
                dash_cooldown = DASH_COOLDOWN

                create_particles(
                    player.centerx,
                    player.centery,
                    CYAN,
                    20
                )


# ─────────────────────────────────────────
# MAIN UPDATE
# ─────────────────────────────────────────

def update(dt):

    if game_over:

        update_particles(dt)

        return

    update_timers(dt)

    update_player(dt)

    update_enemies(dt)

    update_coins()

    update_powerups(dt)

    check_enemy_collisions()

    update_particles(dt)

    update_spawning(dt)


# ─────────────────────────────────────────
# DRAW EVERYTHING
# ─────────────────────────────────────────

def draw():

    draw_background()

    # Camera shake.
    offset_x = 0
    offset_y = 0

    if screen_shake > 0:

        offset_x = random.randint(
            -int(screen_shake),
            int(screen_shake)
        )

        offset_y = random.randint(
            -int(screen_shake),
            int(screen_shake)
        )

    # We draw normal objects first.
    draw_coins()
    draw_powerups()
    draw_enemies()
    draw_player()

    for particle in particles:
        particle.draw()

    draw_hud()

    if speed_boost_timer > 0:

        boost_text = small_font.render(
            "⚡ SPEED BOOST!",
            True,
            CYAN
        )

        screen.blit(
            boost_text,
            (
                SCREEN_WIDTH // 2 -
                boost_text.get_width() // 2,
                45
            )
        )

    if game_over:
        draw_game_over()

    # Red damage flash.
    if flash_timer > 0:

        flash = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

        flash.set_alpha(100)

        flash.fill(RED)

        screen.blit(
            flash,
            (0, 0)
        )

    pygame.display.flip()


# ─────────────────────────────────────────
# START
# ─────────────────────────────────────────

reset_game()


# ─────────────────────────────────────────
# GAME LOOP
# ─────────────────────────────────────────

while running:

    dt = clock.tick(FPS) / 1000.0

    handle_events()

    update(dt)

    draw()


# ─────────────────────────────────────────
# CLEANUP
# ─────────────────────────────────────────

pygame.quit()
sys.exit()
