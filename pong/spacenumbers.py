from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget


class SpaceNumbersGame(Widget):
    def start(self):
        ...

    def update(self, dt):
        ...


class SpaceNumbersApp(App):
    def build(self):
        game = SpaceNumbersGame()
        game.start()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == "__main__":
    SpaceNumbersApp().run()
