from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle, RenderContext
from kivy.uix.scatter import Scatter

"""
Minimal template for viewing shaders in Kivy.
Variables are setup to do thebookofshaders.com examples
"""

# Standard vertex shader
vertex_shader_src = """
$HEADER$

void main (void) {
  frag_color = color * vec4(1.0, 1.0, 1.0, opacity);
  tex_coord0 = vTexCoords0;
  gl_Position = projection_mat * modelview_mat * vec4(vPosition.xy, 0.0, 1.0);
}
"""


class ShaderViewer(Scatter):
    def __init__(self, **kwargs):
        self.canvas = RenderContext()

        self.canvas.shader.vs = vertex_shader_src
        self.canvas.shader.fs = Path("shaders/frag/voronoi.frag").read_text()
        # or, if you have vertex and fragment shaders in one file:
        # self.canvas.shader.source = "shaders\dots5.frag"

        # Need to have something to render onto, could also be an image.
        with self.canvas:
            self.rect = Rectangle()

        super().__init__(**kwargs)

        Clock.schedule_interval(self.update_glsl, 0)

    def update_glsl(self, dt):
        self.canvas["u_time"] = Clock.get_boottime()
        self.canvas["u_resolution"] = list(map(float, Window.size))
        self.canvas["u_mouse"] = list(map(float, Window.mouse_pos))
        self.canvas["projection_mat"] = Window.render_context["projection_mat"]
        self.rect.size = self.size


class ShaderApp(App):
    def build(self):
        return ShaderViewer()


ShaderApp().run()
