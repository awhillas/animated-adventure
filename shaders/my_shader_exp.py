import time

from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle, RenderContext
from kivy.uix.image import Image
from kivy.uix.widget import Widget

"""
From https://github.com/kivy/kivy/wiki/Advanced-Graphics:-In-Progress#your-first-custom-shader
"""


class CustomShaderWidget(Widget):
    def __init__(self, **kwargs):
        # We must do this, if no other widget has been loaded the
        # GL context may not be fully prepared
        EventLoop.ensure_window()
        # Most likely you will want to use the parent projection
        # and modelviev in order for your widget to behave the same
        # as the rest of the widgets
        self.canvas = RenderContext(
            use_parent_projection=True, use_parent_modelview=True
        )
        # self.canvas.shader.source = "shaders/my_shader_exp.glsl"
        self.canvas.shader.source = "shaders/crazy_dots.glsl"
        with self.canvas:
            self.rect = Rectangle()
        super().__init__(**kwargs)

        Clock.schedule_interval(self.update_glsl, 0)

        self.start_time = time.time()

    def update_glsl(self, dt):
        self.canvas["u_time"] = self.start_time - time.time()
        self.canvas["u_resolution"] = list(map(float, Window.size))
        self.canvas["u_mouse"] = list(map(float, Window.mouse_pos))


class CustomShaderApp(App):
    def build(self):
        shader_widget = CustomShaderWidget()
        im = Image(source="shaders/kitten.jpg")
        shader_widget.add_widget(im)
        shader_widget.bind(size=im.setter("size"))
        return shader_widget


if __name__ == "__main__":
    CustomShaderApp().run()
