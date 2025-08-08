import pygame
import random
import sys

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

def create_pipe():
    pipe_height = random.randint(100, 400)
    return {'x': WIDTH, 'gap_y': pipe_height, 'scored': False}

def draw_bird(y):
    pygame.draw.circle(screen, BLUE, (BIRD_X, int(y)), BIRD_RADIUS)

def draw_pipes(pipes_list):
    for pipe in pipes_list:
        x = pipe['x']
        gap_y = pipe['gap_y']
        pygame.draw.rect(screen, GREEN, (x, 0, PIPE_WIDTH, gap_y))
        pygame.draw.rect(screen, GREEN, (x, gap_y + PIPE_GAP, PIPE_WIDTH, HEIGHT - gap_y - PIPE_GAP))

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
    return bird_y - BIRD_RADIUS <= 0 or bird_y + BIRD_RADIUS >= HEIGHT

def update_pipes(pipes, bird_y, score):
    new_pipes = []
    new_score = score
    for pipe in pipes:
        pipe = pipe.copy()
        pipe['x'] -= PIPE_SPEED

        # Faster smart dodge: pipe gap moves quickly toward bird's y position
        if BIRD_X < pipe['x'] < BIRD_X + 200:
            target_gap_y = int(bird_y - PIPE_GAP // 2)
            # Move gap_y toward bird's y position with higher speed
            dodge_speed = 14  # Increased speed for faster dodge
            if pipe['gap_y'] < target_gap_y:
                pipe['gap_y'] += min(dodge_speed, target_gap_y - pipe['gap_y'])
            elif pipe['gap_y'] > target_gap_y:
                pipe['gap_y'] -= min(dodge_speed, pipe['gap_y'] - target_gap_y)
            pipe['gap_y'] = max(50, min(pipe['gap_y'], HEIGHT - PIPE_GAP - 50))

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

def auto_safe_bird(bird_y, pipes):
    # Find the nearest pipe in front of the bird
    nearest_pipe = None
    min_dist = float('inf')
    for pipe in pipes:
        if pipe['x'] + PIPE_WIDTH > BIRD_X and pipe['x'] < BIRD_X + 200:
            dist = pipe['x'] - BIRD_X
            if dist < min_dist:
                min_dist = dist
                nearest_pipe = pipe
    # If near wall, or near pipe edge, set bird_y to center of gap
    if bird_y - BIRD_RADIUS <= 0 or bird_y + BIRD_RADIUS >= HEIGHT:
        if nearest_pipe:
            bird_y = nearest_pipe['gap_y'] + PIPE_GAP // 2
        else:
            bird_y = HEIGHT // 2
    else:
        for pipe in pipes:
            in_pipe_x = BIRD_X + BIRD_RADIUS > pipe['x'] and BIRD_X - BIRD_RADIUS < pipe['x'] + PIPE_WIDTH
            in_pipe_y = bird_y - BIRD_RADIUS < pipe['gap_y'] or bird_y + BIRD_RADIUS > pipe['gap_y'] + PIPE_GAP
            if in_pipe_x and in_pipe_y:
                bird_y = pipe['gap_y'] + PIPE_GAP // 2
    return bird_y

def run_game():
    bird_y = HEIGHT // 2
    bird_speed = 0
    pipes = [create_pipe()]
    score = 0

    running = True
    while running:
        screen.fill(WHITE)

        bird_speed = handle_events(bird_speed)
        bird_y, bird_speed = update_bird(bird_y, bird_speed)

        pipes, score = update_pipes(pipes, bird_y, score)
        pipes = manage_pipes(pipes)

        # Auto-safe bird position
        bird_y = auto_safe_bird(bird_y, pipes)

        draw_bird(bird_y)
        draw_pipes(pipes)
        display_score(score)

        pygame.display.update()
        clock.tick(FPS)

# Main Loop
while True:
    score = run_game()
    game_over_screen(score)
