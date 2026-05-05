#version 330

uniform vec2 resolution;
uniform float time;

out vec4 final_color;

// random function


// main
void	main() {
	vec2 grid = floor(gl_FragCoord.xy * 0.5);
	vec3 color = vec3(0.8, 0.02, 0.05);
	final_color = vec4(color, 1.0);
}
