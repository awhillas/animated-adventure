from kivy.app import App
from kivy.uix.scatter import Scatter

vertex_shader_src = """
$HEADER$
varying vec2 position;
void main()
{
    vec4 p;
    gl_Position = projection_mat * modelview_mat * vec4(vPosition.xy, 0.0, 1.0);
    p = projection_mat * vec4(vPosition.xy, 0.0, 1.0);
    position = vec2(p.xy) * 10.0;
}
"""

fragment_shader_src = """
$HEADER$
varying vec2 position;
uniform int maxIterations;
uniform float zoom;
void main()
{
    vec2 center = vec2(-0.65,0);
    vec3 outerColor1 = vec3(0.0,0.2,0.7);
    vec3 outerColor2 = vec3(1.0,1.0,1.0);
    float real = position.x * (1.0/zoom) + center.x;
    float imag = position.y * (1.0/zoom) + center.y;
    float cReal = real;
    float cImag = imag;
    float r2 = 0.0;
    int iter;
    for (iter = 0; iter < maxIterations && r2 < 4.0; ++iter)
    {
        float tempreal = real;
        real = (tempreal * tempreal) - (imag * imag) + cReal;
        imag = 2.0 * tempreal * imag + cImag;
        r2 = real*real;  // this line is missing in the tutorial
    }
    vec3 color;
    if (r2 < 4.0)
        color = vec3(0.1,0.0,0.0);
    else{
        float intensity = float(iter) + 1.0 -  (( log( log( sqrt(r2) ) )/log(2.0)  )  /log(2.0));
        float val = float(intensity)*0.02;
        if (mod(val,2.0) < 1.0){
            color = mix(outerColor1, outerColor2, fract(float(intensity)*0.02));
        }else{
            color = mix(outerColor2, outerColor1, fract(float(intensity)*0.02));
        }
    }
    gl_FragColor = vec4 (clamp(color, 0.0, 1.0), 1.0);
}
"""

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle, RenderContext


class MandelbrotViewer(Scatter):
    def __init__(self, **kwargs):
        self.canvas = RenderContext()
        self.canvas.shader.vs = vertex_shader_src
        self.canvas.shader.fs = fragment_shader_src
        # self.canvas.shader.source = "shaders\mandelbrot.glsl"
        with self.canvas:
            self.rect = Rectangle()
        super().__init__(**kwargs)
        # We'll update our glsl variables in a clock
        Clock.schedule_interval(self.update_glsl, 0)
        self.zoom = 14.8
        self.iterations = 100

    def update_glsl(self, dt):
        self.canvas["zoom"] = self.zoom
        self.canvas["maxIterations"] = self.iterations
        self.canvas["projection_mat"] = Window.render_context["projection_mat"]
        self.rect.size = self.size


class MandelbrotApp(App):
    def build(self):
        return MandelbrotViewer()


MandelbrotApp().run()
