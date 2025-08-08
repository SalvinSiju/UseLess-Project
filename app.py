import pygame
import random
import sys
import math  # Import math for sine function

# Initialize
pygame.init()
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Smart Pipes")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
BLUE = (0, 150, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.SysFont(None, 40)
big_font = pygame.font.SysFont(None, 80)

# Bird
BIRD_X = 100
BIRD_RADIUS = 20
GRAVITY = 0.5
JUMP_STRENGTH = -8

# Pipe
PIPE_WIDTH = 80
PIPE_GAP = 120  # Minimized gap size
PIPE_SPEED = 4

# Load bird image at the top (after pygame.init())
bird_img = pygame.image.load("bird.png").convert_alpha()
bird_img = pygame.transform.scale(bird_img, (48, 36))  # Resize as needed

def create_pipe():
    pipe_height = random.randint(100, 400)
    return {'x': WIDTH, 'gap_y': pipe_height, 'scored': False}

def draw_background():
    # Sky gradient
    for i in range(HEIGHT):
        color = (
            int(135 + (120 * i / HEIGHT)),
            int(206 + (40 * i / HEIGHT)),
            int(235 + (20 * i / HEIGHT))
        )
        pygame.draw.line(screen, color, (0, i), (WIDTH, i))
    # Sun
    pygame.draw.circle(screen, (255, 255, 120), (WIDTH - 80, 80), 50)
    # Clouds
    for cx, cy in [(80, 120), (200, 80), (350, 150), (420, 60)]:
        pygame.draw.ellipse(screen, (255, 255, 255), (cx, cy, 60, 30))
        pygame.draw.ellipse(screen, (240, 240, 240), (cx + 20, cy + 10, 40, 20))

def draw_ground():
    ground_height = 60
    pygame.draw.rect(screen, (180, 140, 60), (0, HEIGHT - ground_height, WIDTH, ground_height))
    # Add some grass
    for x in range(0, WIDTH, 20):
        pygame.draw.rect(screen, (60, 180, 60), (x, HEIGHT - ground_height, 16, 10))

def draw_bird(y):
    screen.blit(bird_img, (BIRD_X - 24, int(y) - 18))

def draw_pipes(pipes_list):
    for pipe in pipes_list:
        x = pipe['x']
        gap_y = pipe['gap_y']
        # Main pipe body
        pygame.draw.rect(screen, (34, 177, 76), (x, 0, PIPE_WIDTH, gap_y))
        pygame.draw.rect(screen, (34, 177, 76), (x, gap_y + PIPE_GAP, PIPE_WIDTH, HEIGHT - gap_y - PIPE_GAP))
        # Pipe shading
        pygame.draw.rect(screen, (24, 127, 56), (x + PIPE_WIDTH - 15, 0, 15, gap_y))
        pygame.draw.rect(screen, (24, 127, 56), (x + PIPE_WIDTH - 15, gap_y + PIPE_GAP, 15, HEIGHT - gap_y - PIPE_GAP))
        # Pipe top lip
        pygame.draw.rect(screen, (180, 255, 180), (x - 6, gap_y - 12, PIPE_WIDTH + 12, 12))
        pygame.draw.rect(screen, (180, 255, 180), (x - 6, gap_y + PIPE_GAP, PIPE_WIDTH + 12, 12))

def display_score(score):
    text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(text, (10, 10))

def game_over_screen(score):
    screen.fill(WHITE)
    msg = big_font.render("Game Over!", True, RED)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 100))
    final_score = font.render(f"Final Score: {score}", True, BLACK)
    screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2))
    prompt = font.render("Press any key to restart", True, BLACK)
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.update()
    wait_for_key()

def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                return

def handle_events(bird_speed):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            bird_speed = JUMP_STRENGTH
    return bird_speed

def update_bird(bird_y, bird_speed):
    bird_speed += GRAVITY
    bird_y += bird_speed
    return bird_y, bird_speed

def check_wall_collision(bird_y):
    # Remove wall collision, allow unlimited vertical movement
    return False

def update_pipes(pipes, bird_y, score):
    new_pipes = []
    new_score = score
    for pipe in pipes:
        pipe = pipe.copy()
        pipe['x'] -= PIPE_SPEED

        # Smart dodge: pipe gap moves toward bird's y position, unlimited
        if BIRD_X < pipe['x'] < BIRD_X + 200:
            target_gap_y = int(bird_y - PIPE_GAP // 2)
            dodge_speed = 14
            if pipe['gap_y'] < target_gap_y:
                pipe['gap_y'] += min(dodge_speed, target_gap_y - pipe['gap_y'])
            elif pipe['gap_y'] > target_gap_y:
                pipe['gap_y'] -= min(dodge_speed, pipe['gap_y'] - target_gap_y)
            # Remove vertical limits
            # pipe['gap_y'] = max(50, min(pipe['gap_y'], HEIGHT - PIPE_GAP - 50))

        # Score
        if not pipe['scored'] and pipe['x'] + PIPE_WIDTH < BIRD_X:
            new_score += 1
            pipe['scored'] = True

        new_pipes.append(pipe)
    return new_pipes, new_score

def check_pipe_collision(pipes, bird_y):
    for pipe in pipes:
        in_pipe_x = BIRD_X + BIRD_RADIUS > pipe['x'] and BIRD_X - BIRD_RADIUS < pipe['x'] + PIPE_WIDTH
        in_pipe_y = bird_y - BIRD_RADIUS < pipe['gap_y'] or bird_y + BIRD_RADIUS > pipe['gap_y'] + PIPE_GAP
        if in_pipe_x and in_pipe_y:
            return True
    return False

def manage_pipes(pipes):
    pipes = [pipe for pipe in pipes if pipe['x'] >= -PIPE_WIDTH]
    if not pipes or pipes[-1]['x'] < WIDTH - 300:
        pipes.append(create_pipe())
    return pipes

def auto_safe_bird(bird_y, bird_speed, pipes):
    # Find the nearest pipe in front of the bird
    nearest_pipe = None
    min_dist = float('inf')
    for pipe in pipes:
        if pipe['x'] + PIPE_WIDTH > BIRD_X and pipe['x'] < BIRD_X + 200:
            dist = pipe['x'] - BIRD_X
            if dist < min_dist:
                min_dist = dist
                nearest_pipe = pipe

    # Only auto-move if bird is in danger
    in_danger = False
    if nearest_pipe:
        gap_top = nearest_pipe['gap_y']
        gap_bottom = nearest_pipe['gap_y'] + PIPE_GAP
        # If bird is about to hit pipe (within 1.5*radius of gap edge)
        if bird_y - BIRD_RADIUS < gap_top + 1.5 * BIRD_RADIUS or bird_y + BIRD_RADIUS > gap_bottom - 1.5 * BIRD_RADIUS:
            in_danger = True

    # Smoothly move bird toward gap center if in danger
    if in_danger and nearest_pipe:
        target_y = nearest_pipe['gap_y'] + PIPE_GAP // 2
        smoothing = 0.08  # Lower is smoother
        bird_y += (target_y - bird_y) * smoothing
        # Optionally, slow down bird_speed for more control
        bird_speed *= 0.85
    return bird_y, bird_speed

def run_game():
    bird_y = HEIGHT // 2
    bird_speed = 0
    pipes = [create_pipe()]
    score = 0

    camera_offset = 0
    camera_target = 0

    running = True
    while running:
        # Camera target follows bird
        camera_target = int(bird_y - HEIGHT // 2)
        # Smooth camera movement
        camera_offset += (camera_target - camera_offset) * 0.1

        draw_background_with_camera(camera_offset)
        draw_ground_with_camera(camera_offset)

        bird_speed = handle_events(bird_speed)
        bird_y, bird_speed = update_bird(bird_y, bird_speed)

        pipes, score = update_pipes(pipes, bird_y, score)
        pipes = manage_pipes(pipes)

        bird_y, bird_speed = auto_safe_bird(bird_y, bird_speed, pipes)

        draw_bird_with_camera(bird_y, camera_offset)
        draw_pipes_with_camera(pipes, camera_offset)
        display_score(score)
        draw_vertical_indicator(bird_y, camera_offset)

        if abs(camera_offset) > HEIGHT // 2:
            warn = font.render("Out of bounds!", True, RED)
            screen.blit(warn, (WIDTH // 2 - warn.get_width() // 2, 60))

        pygame.display.update()
        clock.tick(FPS)

# Update your draw functions to use camera_offset:
def draw_background_with_camera(camera_offset):
    # Sky gradient (shifted by camera)
    for i in range(HEIGHT):
        color = (
            int(135 + (120 * i / HEIGHT)),
            int(206 + (40 * i / HEIGHT)),
            int(235 + (20 * i / HEIGHT))
        )
        pygame.draw.line(screen, color, (0, i), (WIDTH, i))
    # Sun and clouds (fixed positions)

def draw_ground_with_camera(camera_offset):
    ground_height = 60
    pygame.draw.rect(screen, (180, 140, 60), (0, HEIGHT - ground_height - camera_offset, WIDTH, ground_height))
    for x in range(0, WIDTH, 20):
        pygame.draw.rect(screen, (60, 180, 60), (x, HEIGHT - ground_height - camera_offset, 16, 10))

def draw_bird_with_camera(y, camera_offset):
    # Bobbing effect
    bob = 4 * math.sin(pygame.time.get_ticks() / 200)
    # Shadow
    shadow_y = int(y) - camera_offset + 18
    pygame.draw.ellipse(screen, (80, 80, 80, 80), (BIRD_X - 20, shadow_y, 40, 10))
    # Bird image
    screen.blit(bird_img, (BIRD_X - 24, int(y) - 18 - camera_offset + bob))

def draw_pipes_with_camera(pipes_list, camera_offset):
    for pipe in pipes_list:
        x = pipe['x']
        gap_y = pipe['gap_y'] - camera_offset
        pygame.draw.rect(screen, (34, 177, 76), (x, 0, PIPE_WIDTH, gap_y))
        pygame.draw.rect(screen, (34, 177, 76), (x, gap_y + PIPE_GAP, PIPE_WIDTH, HEIGHT - gap_y - PIPE_GAP))
        pygame.draw.rect(screen, (24, 127, 56), (x + PIPE_WIDTH - 15, 0, 15, gap_y))
        pygame.draw.rect(screen, (24, 127, 56), (x + PIPE_WIDTH - 15, gap_y + PIPE_GAP, 15, HEIGHT - gap_y - PIPE_GAP))
        pygame.draw.rect(screen, (180, 255, 180), (x - 6, gap_y - 12, PIPE_WIDTH + 12, 12))
        pygame.draw.rect(screen, (180, 255, 180), (x - 6, gap_y + PIPE_GAP, PIPE_WIDTH + 12, 12))

def draw_vertical_indicator(bird_y, camera_offset):
    # Draw a ruler/bar on the right side
    pygame.draw.rect(screen, (200, 200, 200), (WIDTH - 30, 0, 20, HEIGHT))
    # Bird position marker
    marker_y = int(bird_y - camera_offset)
    pygame.draw.circle(screen, (255, 100, 100), (WIDTH - 20, marker_y), 8)

def run_game():
    bird_y = HEIGHT // 2
    bird_speed = 0
    pipes = [create_pipe()]
    score = 0

    camera_offset = 0
    camera_target = 0

    running = True
    while running:
        # Camera target follows bird
        camera_target = int(bird_y - HEIGHT // 2)
        # Smooth camera movement
        camera_offset += (camera_target - camera_offset) * 0.1

        draw_background_with_camera(camera_offset)
        draw_ground_with_camera(camera_offset)

        bird_speed = handle_events(bird_speed)
        bird_y, bird_speed = update_bird(bird_y, bird_speed)

        pipes, score = update_pipes(pipes, bird_y, score)
        pipes = manage_pipes(pipes)

        bird_y, bird_speed = auto_safe_bird(bird_y, bird_speed, pipes)

        draw_bird_with_camera(bird_y, camera_offset)
        draw_pipes_with_camera(pipes, camera_offset)
        display_score(score)
        draw_vertical_indicator(bird_y, camera_offset)

        if abs(camera_offset) > HEIGHT // 2:
            warn = font.render("Out of bounds!", True, RED)
            screen.blit(warn, (WIDTH // 2 - warn.get_width() // 2, 60))

        pygame.display.update()
        clock.tick(FPS)

# Main Loop
while True:
    score = run_game()
    game_over_screen(score)
