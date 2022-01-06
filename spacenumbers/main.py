from random import randint, random

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color
from kivy.properties import (
    ListProperty,
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty,
)
from kivy.uix.widget import Widget
from kivy.vector import Vector


class NaughtyBaddie(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    colour = ListProperty([])

    def __init__(self, start_pos, **kwargs):
        super().__init__(**kwargs)
        self.pos = start_pos
        self.colour = (random(), random(), random(), 0.8)

    def move(self):
        if (self.y < self.parent.y) or (self.top > self.parent.top):
            self.velocity_y *= -1

        if (self.x < self.parent.x) or (self.right > self.parent.right):
            self.velocity_x *= -1

        self.pos = Vector(*self.velocity) + self.pos

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.remove(self)
            return True
        return super().on_touch_down(touch)


class SpaceNumbersGame(Widget):
    baddies = []
    level = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.spawn_baddie, 2.0)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def spawn_baddie(self, dt):
        padding = 50
        nb = NaughtyBaddie(
            start_pos=Vector(
                randint(50, int(self.width) - padding),
                randint(50, int(self.height) - padding),
            )
        )
        nb.velocity = Vector(randint(1, 6), 0).rotate(randint(0, 360))
        self.baddies.append(nb)
        self.add_widget(nb)

    def update(self, dt):
        for b in self.baddies:
            b.move()

    def remove(self, widget):
        self.baddies.remove(widget)
        self.remove_widget(widget)


class GameLayout(Widget):
    ...


class SpaceNumbersApp(App):
    def build(self):
        game = GameLayout()

        return game


if __name__ == "__main__":
    SpaceNumbersApp().run()
