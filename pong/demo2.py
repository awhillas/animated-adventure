from __future__ import division

import base64
import json
import math
from collections import namedtuple
from random import choice, randint, random

from kivy import platform
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.image import Image
from kivy.core.window import Window
from kivy.graphics import Mesh
from kivy.graphics.instructions import RenderContext
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

UVMapping = namedtuple("UVMapping", "u0 v0 u1 v1 su sv")

GLSL = b"""
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
    glslc.write(GLSL)


def load_atlas():
    atlas = json.loads(
        """{
    "invader.png": {
        "frame1": [0, 0, 32, 32],
        "frame2": [32, 0, 32, 32]
    }
}"""
    )

    tex_name, mapping = atlas.popitem()
    data = """iVBORw0KGgoAAAANSUhEUgAAAEAAAAAgCAYAAACinX6EAAAC3UlEQVRoQ9VZy01EMQzcbYFWOHKhAwqhHgqhAy4caYUWQInWkeOM7XHe0wo4IHZfEnvG488L18vl8nPBP1fn+92vkZ2zbWjfPFyypttuv36eP18mUB9P7/JsF6zd153RdoCNMwIxzrCYtEM32x3jQgAJvuLsQnCzbOwsBKk1KAhWORRwQEKZAOho4iyK/CRDpEJPeip605Io4ugsCQCTAlO0q4YQ68AhqJIs/4SMzCe0ThPQ7Hh1YIpe5lD2PEivYd9GWMC17zOg1r45awq2JQCSkAFinwNHliLZwOnipBa4aZfZdwgXRY8uIOdsyTBzAhQ8tEWnmRS4beBexaerqdMWx/5NKUY9v4HVz722WU6DLACwndh+/f31OsA/PL71vyskkK11KNGe3/aLD81+xXaVgKkWaMNWPlVHCiRMqYh8qNqOSECynCqyjr4mATmhi92B6XKbgB37FAEi+0aAJ0UbKUvQUQWID82+R75N1WT07vEsEyAkIIDinCgFOODZ1OJyZxK9CCmMIGCxv0WABWiLFCJA5WFGQpkAsc+o5ObbwB0SIE7byEZVWsB7hYpIhejlCbZilgDZrH1Y2iBqMd54qiVZXOPNBOHwE83+jH1DQFciRYBtgbufmehXZ4yjvvw5AqpDztkETIPQ7uFon/OiM1X/M6NvUwLVragaU4XIAiWuocL3gSz6CFQQJGrMp4sREcGuHi+KSf5n+zTOIxepk53mEx0RooCJk9H9nkt48gZ6BLQVyTTqZwejm5psz1JHCPXc42Z6BEjfMpXAEEBgESXVs0t2pVYvL1olAmQyvFmEU6RXbZ33jqkLMC8vFbRgrSV5GYTQ+RV5VtYuuanJI1VT4WOJPpoEvQPh5ohheVYEMgqoaXmMUjMy/gUBOwU0A7605+hlCMrSyetKDahGECmheobbllkCsmmwOkRVAaCrcibaTG1pa7o/2VW1Z5ABc+9/h0fkWF+G/79XyyU5pxo9EQAAAABJRU5ErkJgggAA"""
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


class Particle:
    x = 0
    y = 0
    size = 1

    def __init__(self, parent, i):
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


class PSWidget(Widget):
    indices = []
    vertices = []
    particles = []
    tv = []
    refList = []
    refDict = {}
    updated = False

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

    def make_particles(self, Cls, num):
        count = len(self.particles)
        uv = self.uvmap[Cls.tex_name]
        for i in range(count, count + num):
            j = 4 * i
            self.indices.extend((j, j + 1, j + 2, j + 2, j + 3, j))
            vet = [
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
            ]
            self.refList.append(vet)
            self.vertices.extend(vet)

            p = Cls(self, i)
            self.particles.append(p)
            self.refDict[p] = vet
            vet = None

    def update_texture(self, me):
        self.updated = False
        uv = self.uvmap[me.tex_name]
        ind = self.refList.index(self.refDict[me])

        oo = [
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
        ]
        self.refDict[me] = oo
        self.refList[ind] = oo
        oo = None
        self.vertices = [
            item for sublist in self.refList for item in sublist
        ]  # sum(self.refList, [])
        self.updated = True

    def update_glsl(self, nap):

        for p in self.particles:
            p.advance(nap)
            p.update()

        if self.updated:
            self.canvas.clear()

            with self.canvas:
                Mesh(
                    fmt=self.vfmt,
                    mode="triangles",
                    indices=self.indices,
                    vertices=self.vertices,
                    texture=self.texture,
                )


class Enemy(Particle):
    active = False
    tex_name = "frame1"
    v = 0
    time = 0.0
    rate = 0.2

    def reset(self, created=False):
        self.active = False
        self.x = -100
        self.y = -100
        self.v = 0

    def advance(self, nap):
        if self.active:
            self.time += nap
            if self.time > self.rate:
                if self.tex_name == "frame1":
                    self.tex_name = "frame2"
                else:
                    self.tex_name = "frame1"
                self.time -= self.rate
                self.parent.update_texture(self)

            if self.check_hit():
                self.reset()
                return

            self.x -= 200 * nap
            if self.x < -50:
                self.reset()
                return

            self.y += self.v * nap
            if self.y <= 0:
                self.v = abs(self.v)
            elif self.y >= self.parent.height:
                self.v = -abs(self.v)

        elif self.parent.spawn_delay <= 0:
            self.active = True
            self.x = self.parent.width + 50
            self.y = self.parent.height * random()
            self.v = randint(-100, 100)
            self.parent.spawn_delay += 1

    def check_hit(self):
        # Not implementec
        return False


class Game(PSWidget):

    spawn_delay = 0.1

    use_mouse = platform not in ("ios", "android")

    def initialize(self):
        self.make_particles(Enemy, 1000)

    def update_glsl(self, nap):
        self.spawn_delay -= nap

        PSWidget.update_glsl(self, nap)


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
