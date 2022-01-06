# Import the pygame module
import random

import pygame

# from enemys import Enemy
from pygame.locals import K_ESCAPE, KEYDOWN, MOUSEBUTTONDOWN, MOUSEMOTION, QUIT

pygame.init()
clock = pygame.time.Clock()

# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.Surface((50, 50))
        self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(2, 10)

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# Create a custom event for adding a new enemy
ADDENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(ADDENEMY, 250)

# Main loop
running = True
while running:
    clock.tick(30)

    # Look at every event in the queue
    for event in pygame.event.get():
        # Touch screen events
        if event.type == MOUSEBUTTONDOWN or event.type == MOUSEMOTION:
            x, y = event.pos
            for e in enemies:
                if e.rect.collidepoint(x, y):
                    e.kill()

        if event.type == KEYDOWN:
            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False

        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False

        # Add a new enemy?
        elif event.type == ADDENEMY:
            # Create the new enemy and add it to sprite groups
            new_enemy = Enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        # pressed_keys = pygame.key.get_pressed()

    enemies.update()

    # Fill the screen with white
    screen.fill((255, 255, 255))

    # Draw all sprites
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)

    # Flip everything to the display
    pygame.display.flip()
