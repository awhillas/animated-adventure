from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import RenderContext
from kivy.graphics.opengl import GL_DEPTH_TEST, glDisable, glEnable
from kivy.resources import resource_find
from kivy.uix.widget import Widget


class Renderer(Widget):
    def __init__(self, **kwargs):
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find("simple.glsl")
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update_glsl, 1 / 60.0)

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)


class RendererApp(App):
    def build(self):
        return Renderer()


if __name__ == "__main__":
    RendererApp().run()
