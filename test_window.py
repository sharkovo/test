import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 900, 520
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vision Test Window")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 28)

player_w, player_h = 60, 60
player_x = WIDTH // 2 - player_w // 2
player_y = HEIGHT - 100
player_speed = 8

target_w, target_h = 40, 40
target_x = random.randint(50, WIDTH - 50 - target_w)
target_y = 120

score = 0

def respawn_target():
    global target_x, target_y
    target_x = random.randint(50, WIDTH - 50 - target_w)
    target_y = 120

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                player_x -= player_speed
            elif event.key == pygame.K_d:
                player_x += player_speed
            elif event.key == pygame.K_SPACE:
                player_center = player_x + player_w // 2
                target_center = target_x + target_w // 2
                if abs(player_center - target_center) < 35:
                    score += 1
                    respawn_target()

    if player_x < 0:
        player_x = 0
    if player_x > WIDTH - player_w:
        player_x = WIDTH - player_w

    screen.fill((245, 245, 245))

    pygame.draw.line(screen, (200, 200, 200), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)
    pygame.draw.rect(screen, (255, 0, 0), (target_x, target_y, target_w, target_h))
    pygame.draw.rect(screen, (0, 100, 255), (player_x, player_y, player_w, player_h))

    text1 = font.render("A/D move, SPACE attack", True, (30, 30, 30))
    text2 = font.render(f"Score: {score}", True, (30, 30, 30))

    screen.blit(text1, (20, 20))
    screen.blit(text2, (20, 60))

    pygame.display.flip()

pygame.quit()
sys.exit()