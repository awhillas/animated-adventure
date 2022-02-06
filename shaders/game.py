from __future__ import division

import kivy
from kivy.config import Config
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.lang import Builder

Config.set("modules", "monitor", "")


import base64
import json
import math
import random
from collections import namedtuple

from kivy import platform
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.image import Image
from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.graphics import Mesh
from kivy.graphics.instructions import RenderContext
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

UVMapping = namedtuple("UVMapping", "u0 v0 u1 v1 su sv")

GLSL = """
---vertex
$HEADER$

attribute vec2  vCenter;
attribute float vScale;

void main(void)
{
    tex_coord0 = vTexCoords0;
    mat4 move_mat = mat4
        (1.0, 0.0, 0.0, vCenter.x,
         0.0, 1.0, 0.0, vCenter.y,
         0.0, 0.0, 1.0, 0.0,
         0.0, 0.0, 0.0, 1.0);
    vec4 pos = vec4(vPosition.xy * vScale, 0.0, 1.0)
        * move_mat;
    gl_Position = projection_mat * modelview_mat * pos;
}

---fragment
$HEADER$

void main(void)
{
    gl_FragColor = texture2D(texture0, tex_coord0);
}

"""

with open("game.glsl", "wb") as glslc:
    glslc.write(GLSL.encode())


def load_atlas():
    atlas = json.loads("""{"game-0.png": {"Elien": [2, 26, 100, 100]}}""")

    tex_name, mapping = atlas.popitem()
    data = """iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAAACJklEQVR4nO3dy1ICQRAF0YLw/39ZVxMBGCjEMF23JvOsXPgounMaN61VQrtsH3x3TqFfLv9/ykdcq9z8RKv25Lro5yiUAcAZAJwBwBkAnAHAGQCcAcAZAJwBwBkAnAHAGQCcAcAZAJwBwBkAnAHAGQCcAcAZAJwBwBkAnAHAfXUPsNM79ydWXbYZZVoAey7MPH6tQdScAI64KbV9T3QI6QGsuCKHDiH5l8DVd1aRd2QTT4DOjcCdBmknQMpTmDLH4ZICSFv0tHkOkRJA6mKnzvUxCQGkL3L6fLskBKBG3QFMebqmzPm2zgCmLeq0eV/SfQKoWVcAU5+mqXM/5QkA1xHA9Kdo+vx3PAHgDADOAOBWB3CW98+zvA5PADoDgDMAOAOAMwA4A4AzADgDgDMAuNUBnOXCxVlehycAnQHAGQBcRwDT3z+nz3/HEwCuK4CpT9HUuZ/yBIDrDGDa0zRt3pd0nwBTFnXKnG/rDkDNEgJIf7rS59slIYCq3EVOnetjUgKoylvstHkOkRRAVc6ip8xxuMS/E7gtfsflC8zGb9JOgFurNwO3+VWZJ8CtFacBcuM36QFsjggBvfGbKQFsHjfNfxix07QAHrmpOyX/EqgFDADOAOAMAM4A4AwAzgDgDADOAOAMAM4A4AwAzgDgDADOAOAMAM4A4AwAzgDgDADOAOAMAM4A4AwA7lrl7YpE7okkSZIkSZIkSZIkSZIkSZIkSZL+9AMvSSThyPfOhQAAAABJRU5ErkJggg=="""
    with open(tex_name, "wb") as co:
        co.write(base64.b64decode(data))
    tex = Image(tex_name).texture
    tex_width, tex_height = tex.size

    uvmap = {}
    for name, val in mapping.items():
        x0, y0, w, h = val
        x1, y1 = x0 + w, y0 + h
        uvmap[name] = UVMapping(
            x0 / tex_width,
            1 - y1 / tex_height,
            x1 / tex_width,
            1 - y0 / tex_height,
            0.5 * w,
            0.5 * h,
        )

    return tex, uvmap


class Particle(EventDispatcher):
    # x = 0
    # y = 0
    x = NumericProperty(0)
    y = NumericProperty(0)
    size = 1

    def __init__(self, parent, i):
        super(Particle, self).__init__()
        self.parent = parent
        self.vsize = parent.vsize
        self.base_i = 4 * i * self.vsize
        self.reset(created=True)

    def update(self):
        for i in range(self.base_i, self.base_i + 4 * self.vsize, self.vsize):
            self.parent.vertices[i : i + 3] = (self.x, self.y, self.size)

    def reset(self, created=False):
        raise NotImplementedError()

    def advance(self, nap):
        raise NotImplementedError()


class GameScreen(Widget):
    indices = []
    vertices = []
    particles = []

    def __init__(self, **kwargs):
        Widget.__init__(self, **kwargs)
        self.canvas = RenderContext(use_parent_projection=True)
        self.canvas.shader.source = "game.glsl"

        self.vfmt = (
            (b"vCenter", 2, "float"),
            (b"vScale", 1, "float"),
            (b"vPosition", 2, "float"),
            (b"vTexCoords0", 2, "float"),
        )

        self.vsize = sum(attr[1] for attr in self.vfmt)
        self.texture, self.uvmap = load_atlas()

    def on_touch_down(self, touch):
        for w in self.particles:
            if w.collide_point(*touch.pos):
                w.reset()  # Not Working
        return super(GameScreen, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        for w in self.particles:
            if w.collide_point(*touch.pos):
                w.reset()  # Not Working
        return super(GameScreen, self).on_touch_move(touch)

    def make_particles(self, Ap, num):
        count = len(self.particles)
        uv = self.uvmap[Ap.tex_name]

        for i in range(count, count + num):
            j = 4 * i
            self.indices.extend((j, j + 1, j + 2, j + 2, j + 3, j))

            self.vertices.extend(
                (
                    0,
                    0,
                    1,
                    -uv.su,
                    -uv.sv,
                    uv.u0,
                    uv.v1,
                    0,
                    0,
                    1,
                    uv.su,
                    -uv.sv,
                    uv.u1,
                    uv.v1,
                    0,
                    0,
                    1,
                    uv.su,
                    uv.sv,
                    uv.u1,
                    uv.v0,
                    0,
                    0,
                    1,
                    -uv.su,
                    uv.sv,
                    uv.u0,
                    uv.v0,
                )
            )

            p = Ap(self, i)
            self.particles.append(p)

    def update_glsl(self, nap):
        for p in self.particles:
            p.advance(nap)
            p.update()

        self.canvas.clear()
        self.canvas.before.clear()  # temporary

        with self.canvas.before:  # temporary code block
            for p in self.particles:
                Rectangle(
                    pos=(p.left, p.bottom),
                    size=(p.size * p.texture_size, p.size * p.texture_size),
                )

        with self.canvas:
            Mesh(
                fmt=self.vfmt,
                mode="triangles",
                indices=self.indices,
                vertices=self.vertices,
                texture=self.texture,
            )


class Ufo(Particle):
    plane = 2.0
    tex_name = "Elien"
    texture_size = 129
    right = NumericProperty(129)
    top = NumericProperty(129)
    left = NumericProperty(0)
    bottom = NumericProperty(0)

    def reset(self, created=False):
        self.plane = random.uniform(2.0, 2.8)
        self.size = random.uniform(0.5, 1.0)  # every particle must have a random size
        self.x = random.randint(15, self.parent.right - 15)
        self.y = self.parent.top + random.randint(100, 2500)

    def collide_point(self, x, y):
        """Check if a point (x, y) is inside the Ufo's axis aligned bounding box."""
        return self.left <= x <= self.right and self.bottom <= y <= self.top

    def advance(self, nap):
        self.y -= 100 * self.plane * nap
        if self.y < 0:
            self.reset()

    def on_x(self, instance, new_x):
        self.right = new_x + self.size * self.texture_size / 2.0
        self.left = new_x - self.size * self.texture_size / 2.0

    def on_y(self, instance, new_y):
        self.top = new_y + self.size * self.texture_size / 2.0
        self.bottom = new_y - self.size * self.texture_size / 2.0


class Game(GameScreen):
    def initialize(self):
        self.make_particles(Ufo, 20)

    def update_glsl(self, nap):
        GameScreen.update_glsl(self, nap)


class GameApp(App):
    def build(self):
        EventLoop.ensure_window()
        return Game()

    def on_start(self):
        self.root.initialize()
        Clock.schedule_interval(self.root.update_glsl, 60 ** -1)


if __name__ == "__main__":
    Window.clearcolor = get_color_from_hex("111110")
    GameApp().run()
