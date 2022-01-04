import sys
from pathlib import Path

import numpy as np
import pygame
from loguru import logger as log
from pygame.locals import *

pygame.init()

DISPLAYSURF = pygame.display.set_mode(
    (1024, 600), DOUBLEBUF
)  # set the display mode, window title and FPS clock

# Create The Backgound

background = pygame.Surface(DISPLAYSURF.get_size())
background = background.convert()
background.fill((100, 100, 255))

pygame.display.set_caption("City Scape")
FPSCLOCK = pygame.time.Clock()

# map_data = [
#     [1, 1, 1, 1, 1],
#     [1, 0, 0, 0, 1],
#     [1, 0, 0, 0, 1],
#     [1, 0, 1, 0, 1],
#     [1, 0, 0, 0, 1],
#     [1, 1, 1, 1, 1],
# ]  # the data for the map expressed as [row[tile]].

main_dir = Path(__file__).parent
wall = pygame.image.load(str(main_dir / "wall.png")).convert_alpha()  # load images
wall2 = pygame.image.load(str(main_dir / "wall2.png")).convert_alpha()  # load images
wall3 = pygame.image.load(str(main_dir / "wall3.png")).convert_alpha()  # load images
grass = pygame.image.load(str(main_dir / "grass.png")).convert_alpha()

TILEWIDTH = 64  # holds the tile width and height
TILEHEIGHT = 64
TILEHEIGHT_HALF = TILEHEIGHT / 2
TILEWIDTH_HALF = TILEWIDTH / 2

MAP_DATA = np.random.choice([0, 1, 2, 3], size=(15, 15))


def render_tiles():
    Mouse_x, Mouse_y = pygame.mouse.get_pos()
    log.debug("{}, {}", Mouse_x, Mouse_y)

    for row_nb, row in enumerate(MAP_DATA):  # for every row of the map...
        for col_nb, tile in enumerate(row):

            if tile == 1:
                tileImage = wall
            elif tile == 2:
                tileImage = wall2
            elif tile == 3:
                tileImage = wall3
            else:
                tileImage = grass

            cart_x = row_nb * TILEWIDTH_HALF
            cart_y = col_nb * TILEHEIGHT_HALF
            iso_x = cart_x - cart_y
            iso_y = (cart_x + cart_y) / 2
            centered_x = DISPLAYSURF.get_rect().centerx + iso_x - TILEWIDTH_HALF
            centered_y = DISPLAYSURF.get_rect().top / 2 + iso_y
            DISPLAYSURF.blit(
                tileImage, (centered_x, centered_y)
            )  # display the actual tile


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

    DISPLAYSURF.blit(background, (0, 0))
    render_tiles()
    pygame.display.flip()
    FPSCLOCK.tick(5)
