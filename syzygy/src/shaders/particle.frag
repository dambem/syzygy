uniform sampler2D sprite;
uniform float time;

varying vec3 vColor;
varying float vRadius;
float rand(vec2 co) {
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 4758.5453);
}
void main() {
    vec2 center = vec2(0.5, 0.5);
    float dist = length(gl_PointCoord - center);
    
    // Create base texture
    vec4 texColor = texture2D(sprite, gl_PointCoord);
    
    float sparkleTime = time * 2.0;
    float sparklePhase = rand(vec2(gl_PointCoord.x, gl_PointCoord.y)) * 6.28318;
    float sparkle = sin(sparkleTime + sparklePhase) * 0.5 + 0.5;
    sparkle *= (1.0 - dist * 2.0); // Fade sparkle at edges
    float glow = 1.0 - smoothstep(0.0, 0.5, dist);
    vec3 glowColor = vColor * glow * 0.5;
    
    vec3 finalColor = vColor * texColor.rgb + glowColor;
    finalColor += finalColor * sparkle * 0.3 * vRadius; // Add sparkle effect
    
    float alpha = texColor.a + glow * 0.3;
    
    gl_FragColor = vec4(finalColor, alpha);
}