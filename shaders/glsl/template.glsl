phong.glslphong.glsl// anything before a meaningful section such as this comment are ignored

---VERTEX SHADER--- // vertex shader starts here
$HEADER$
// Standard GLSL vertex shader stuff
void main (void) {
  frag_color = color * vec4(1.0, 1.0, 1.0, opacity);
  tex_coord0 = vTexCoords0;
  gl_Position = projection_mat * modelview_mat * vec4(vPosition.xy, 0.0, 1.0);
}

---FRAGMENT SHADER--- // fragment shader starts here
$HEADER$
void main(){
    gl_FragColor = frag_color
}
