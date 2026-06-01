#version 330

uniform vec2 resolution;
uniform float time;

out vec4 final_color;


// random function
float	hash(vec2 p) {
    return fract(sin(dot(p.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

// main
void	main() {
    vec3 color = vec3(0.01, 0.01, 0.03);
    vec2 uv = gl_FragCoord.xy / resolution.xy;
    
    float speed = 30.0;

    // Nebuleuse 1
    float pattern1 = sin(uv.x * 3.0 + (time * speed * 0.05)) + sin(uv.y * 4.0 - (time * speed * 0.05));
    pattern1 = pattern1 * 0.25 + 0.5;
    vec3 nebula1 = vec3(0.0, 0.3, 0.4) * pattern1;

    // Nebuleuse 2
    float pattern2 = sin(uv.x * 5.0 - (time * speed * 0.05)) + sin(uv.y * 3.0 + (time * speed * 0.05));
    pattern2 = pattern2 * 0.25 + 0.5;
    vec3 nebula2 = vec3(0.3, 0.0, 0.5) * pattern2;

    color += nebula1 + nebula2;
    float scroll = mod(time * speed, 2000.0);
    vec2 offset = gl_FragCoord.xy + vec2(0.0, scroll);
    vec2 grid_size = vec2(15.0);
    vec2 grid = floor((offset) / grid_size);
    float star_chance = hash(grid);
    if ( star_chance> 0.992) {
        float dist = distance(offset, grid * grid_size + grid_size * 0.5);
        float star_intensity = smoothstep(1.5, 0.0, dist);
        float star_speed = 0.5 + (star_chance * 0.8);
        float twinkle = 0.7 + 0.3 * sin(time * star_speed + star_chance * 10.0);
        vec3 star_color = vec3(0.8, 0.9, 0.5);
        float random_color = hash(grid + 5.0);
        if (random_color < 0.3) {
            star_color = vec3(1.0, 0.7, 0.4);
        } else if (random_color > 0.85) {
            star_color = vec3(0.4, 0.7, 1.0);
        }
        color += star_color * star_intensity * twinkle;
    }
    final_color = vec4(color, 1.0);
}
