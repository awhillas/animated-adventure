from random import randint, random
from re import A

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
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
    value = NumericProperty(1)
    texture = ObjectProperty(None)

    def __init__(self, start_pos, value, **kwargs):
        super().__init__(**kwargs)
        self.pos = start_pos
        self.value = value
        self.colour = (random(), random(), random(), 0.8)
        # Create a number and set it as the texture
        # from https://groups.google.com/g/kivy-users/c/zRCjfhBcX4c/m/G5WYz9SHFMUJ
        label = CoreLabel(text=str(value), font_size=25, color=(1.0, 1.0, 1.0, 1.0))
        label.refresh()
        self.texture = label.texture

    def move(self):
        if (self.y < self.parent.y) or (self.top > self.parent.top):
            self.velocity_y *= -1

        if (self.x < self.parent.x) or (self.right > self.parent.right):
            self.velocity_x *= -1

        self.pos = Vector(*self.velocity) + self.pos

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.add_to_score(self.value)
            self.parent.remove(self)
            return True
        return super().on_touch_down(touch)


class SpaceNumbersGame(Widget):
    baddies = []
    score_lbl = ObjectProperty(None)
    level_lbl = ObjectProperty(None)
    score: int = 0
    level: int = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.spawn_baddie, 1.0)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def spawn_baddie(self, dt):
        padding = 50
        nb = NaughtyBaddie(
            start_pos=Vector(
                randint(50, int(self.width) - padding),
                randint(50, int(self.height) - padding),
            ),
            value=randint(1, self.level),
        )
        nb.velocity = Vector(randint(2, 6), 0).rotate(randint(0, 360))
        self.baddies.append(nb)
        self.add_widget(nb)

    def update(self, dt):
        for b in self.baddies:
            b.move()

    def remove(self, widget):
        self.baddies.remove(widget)
        self.remove_widget(widget)

    def add_to_score(self, amount: int):
        self.score += amount
        self.score_lbl.text = str(self.score)
        if self.score >= 2 ^ self.level * 10:
            self.level += 1
            self.level_lbl.text = f"Level {self.level}"


class GameLayout(Widget):
    ...


class SpaceNumbersApp(App):
    def build(self):
        game = GameLayout()

        return game


if __name__ == "__main__":
    SpaceNumbersApp().run()
