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


class SpaceNumbersGame(Widget):
    baddie = ObjectProperty(None)

    def start(self):
        self.baddie.velocity = Vector(4, 0).rotate(randint(0, 360))

    def update(self, dt):
        self.baddie.move()


class SpaceNumbersApp(App):
    def build(self):
        game = SpaceNumbersGame()
        game.start()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == "__main__":
    SpaceNumbersApp().run()
