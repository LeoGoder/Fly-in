#version 330

uniform vec2 resolution;
uniform float time;

out vec4 final_color;

// random function
float	hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

// main
void	main() {
	vec3 color = vec3(0.02, 0.02, 0.05);
	vec2 uv = gl_FragCoord.xy / resolution.xy;
	// vec3 color2 = vec3(0.02, abs(sin(time)), 1.00);
	
	float speed = 35.0;

	// Nebuleuse 1
	float pattern1 = sin(uv.x * 3.0 + (time * speed * 0.05)) + sin(uv.y * 4.0 - (time * speed * 0.05));
    pattern1 = pattern1 * 0.25 + 0.5;
    vec3 nebula1 = vec3(0.0, 0.3, 0.4) * pattern1;

	// Nebuleuse 2
    float pattern2 = sin(uv.x * 5.0 - (time * speed * 0.05)) + sin(uv.y * 3.0 + (time * speed * 0.05));
    pattern2 = pattern2 * 0.25 + 0.5;
    vec3 nebula2 = vec3(0.3, 0.0, 0.5) * pattern2;

    color += nebula1 + nebula2;
	vec2 offset = vec2(0.0, time * speed);
	vec2 grid = floor((gl_FragCoord.xy + offset) * 0.5);
	if (hash(grid)> 0.997) {
		float sparkle = 1.0;
		// color.r += 0.1;
		// color.g = abs(sin(time));
		// color.b = 1.0;
		color += vec3(1.0) * sparkle;
	}
	final_color = vec4(color, 1.0);
}
