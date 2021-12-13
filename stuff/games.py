import sys
from pathlib import Path

import pygame as pg
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT

if not pg.font:
    print("Warning, fonts disabled")
if not pg.mixer:
    print("Warning, sound disabled")


def loop_quit_keys(event):
    if event.type == QUIT:
        pg.quit()
        sys.exit()
    if event.type == KEYDOWN:
        if event.key == K_ESCAPE:
            pg.quit()
            sys.exit()


# functions to create our resources
def load_image(filepath: Path, colorkey=-1, scale=1):
    image = pg.image.load(str(filepath))
    image = image.convert()

    if scale != 1:
        size = image.get_size()
        size = (size[0] * scale, size[1] * scale)
        image = pg.transform.scale(image, size)

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)

    return image


def load_sound(filepath):
    class NoneSound:
        def play(self):
            pass

    if not pg.mixer or not pg.mixer.get_init():
        return NoneSound()

    sound = pg.mixer.Sound(str(filepath))

    return sound
