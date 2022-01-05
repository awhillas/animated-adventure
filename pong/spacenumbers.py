from random import randint

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, ReferenceListProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector


class NaughtyBaddie(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        if (self.y < 0) or (self.top > self.parent.height):
            self.velocity_y *= -1

        if (self.x < 0) or (self.right > self.parent.width):
            self.velocity_x *= -1

        self.pos = Vector(*self.velocity) + self.pos

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print("clicked/touched", touch)
            return True
        return super().on_touch_down(touch)


class SpaceNumbersGame(Widget):
    baddies = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.spawn_baddie, 2.0)

    def spawn_baddie(self, dt):
        nb = NaughtyBaddie()
        nb.velocity = Vector(randint(1, 6), 0).rotate(randint(0, 360))
        self.baddies.append(nb)
        self.add_widget(nb)

    def update(self, dt):
        for b in self.baddies:
            b.move()


class SpaceNumbersApp(App):
    def build(self):
        game = SpaceNumbersGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == "__main__":
    SpaceNumbersApp().run()
