---VERTEX SHADER---
// Standard headers...
#ifdef GL_ES
    precision highp float;
#endif
/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord0;
/* vertex attributes */
attribute vec2     vPosition;
attribute vec2     vTexCoords0;
/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform vec4       color;
uniform float      opacity;
// ... end standard headers

void main (void) {
  frag_color = color * vec4(1.0, 1.0, 1.0, opacity);
  tex_coord0 = vTexCoords0;
  gl_Position = projection_mat * modelview_mat * vec4(vPosition.xy, 0.0, 1.0);
}


---FRAGMENT SHADER---
// Standard headers...
#ifdef GL_ES
    precision highp float;
#endif
/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;
/* uniform texture samplers */
uniform sampler2D texture0;
uniform mat4 frag_modelview_mat;
// ... end standard headers

uniform vec2 u_resolution;
uniform vec2 u_mouse;
uniform float u_time;       // Time in seconds since load

// void main (void){
//     gl_FragColor = vec4(0.5, 0.1, abs(sin(u_mouse.x)), 1.0);
// }

void main() {
	vec2 st = gl_FragCoord.xy/u_resolution;
	gl_FragColor = vec4(st.x,st.y,0.0,1.0);
}
