$HEADER$

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
