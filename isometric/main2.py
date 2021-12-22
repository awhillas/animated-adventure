import sys
from pathlib import Path

import numpy as np
import pygame
from loguru import logger as log
from pygame.locals import DOUBLEBUF

from stuff.games import load_image, loop_quit_keys

pygame.init()

WIDTH = 800
HEIGHT = 600
DISPLAYSURF = pygame.display.set_mode(
    (800, 600), DOUBLEBUF
)  # set the display mode, window title and FPS clock

# Create The Backgound

background = pygame.Surface(DISPLAYSURF.get_size())
background = background.convert()
background.fill((100, 100, 255))

pygame.display.set_caption("City Scape")
FPSCLOCK = pygame.time.Clock()


main_dir = Path(__file__).parent
wall = load_image(main_dir / "wall.png")
grass = load_image(main_dir / "grass.png")

width_n_height = np.asarray([wall.get_size()])
x_offset = width_n_height[0] / 2
isometric_transformation = np.asarray([[1, -1], [0.5, 0.5]], dtype=np.float16)
transform = isometric_transformation * width_n_height / 2
inv_transform = np.linalg.inv(transform)  # inverse transform

map_data = np.random.choice([0, 1], size=(15, 15)).tolist()


def render_tiles():
    Mouse_x, Mouse_y = pygame.mouse.get_pos()
    x_m, y_m = inv_transform @ (np.asarray([Mouse_x, Mouse_y]))
    log.debug("{}, {}", x_m, y_m)

    for i, row in enumerate(map_data):  # for every row of the map...
        for j, tile in enumerate(row):

            # if i = x_m

            # tileImage = wall if tile == 1 else grass
            tileImage = grass

            x, y = transform @ (np.asarray([i, j]))
            x_delta = WIDTH / 2 - width_n_height[0][0] / 2
            DISPLAYSURF.blit(tileImage, (x + x_delta, y))  # display the actual tile


while True:
    for event in pygame.event.get():
        loop_quit_keys(event)

        DISPLAYSURF.blit(background, (0, 0))

        render_tiles()

        pygame.display.flip()
        FPSCLOCK.tick(5)
