import random
import sys
import time
from pathlib import Path

import pygame as pg
from pygame.locals import *

from stuff.games import load_image, loop_quit_keys

pg.init()
pg.display.set_caption("game base")
screen = pg.display.set_mode((900, 900), 0, 32)
display = pg.Surface((300, 300))

root_dir = Path(__file__).parent

grass_img = load_image(root_dir / "grass.png")

f = open(str(root_dir / "map.txt"))
map_data = [[int(c) for c in row] for row in f.read().split("\n")]
f.close()

while True:
    display.fill((0, 0, 0))

    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            if tile:
                # pg.draw.rect(display, (255, 255, 255), pg.Rect(x * 10, y * 10, 10, 10), 1)
                display.blit(grass_img, (150 + x * 10 - y * 10, 100 + x * 5 + y * 5))
                if random.randint(0, 1):
                    display.blit(
                        grass_img, (150 + x * 10 - y * 10, 100 + x * 5 + y * 5 - 14)
                    )

    for event in pg.event.get():
        loop_quit_keys(event)

    screen.blit(pg.transform.scale(display, screen.get_size()), (0, 0))
    pg.display.update()
    time.sleep(1)
