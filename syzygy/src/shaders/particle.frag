uniform sampler2D sprite;
uniform float time;

varying vec3 vColor;
varying float vRadius;

float rand(vec2 co) {
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f); // Smoother interpolation
    
    float a = rand(i);
    float b = rand(i + vec2(1.0, 0.0));
    float c = rand(i + vec2(0.0, 1.0));
    float d = rand(i + vec2(1.0, 1.0));
    
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}
void main() {
    vec2 center = vec2(0.5, 0.5);
    vec2 toCenter = gl_PointCoord - center;
    float dist = length(toCenter);

    // float dist = length(gl_PointCoord - center);
    
    // Create base texture
    vec4 texColor = texture2D(sprite, gl_PointCoord);
    

    float spotScale = 50.0; // Adjust for spot size
    float spotTime = sin(time * 0.01) * -cos(time * 0.01); // Slow movement
    vec2 spotUV = gl_PointCoord * spotScale + vec2(spotTime);
    float spots = noise(spotUV) * noise(spotUV * 2.0);
    spots = smoothstep(0.5, 0.8, spots);


    float sparkleTime = time * 3.0;
    float sparklePhase = rand(vec2(gl_PointCoord.x, gl_PointCoord.y)) * 6.28318;

    float sparkle = sin(sparkleTime + sparklePhase) * 0.5 + 0.5;
    sparkle *= exp(1.0 - dist * 1.5); // Fade sparkle at edges

    float glow = 1.0 - smoothstep(0.0, 0.2, dist);
    vec3 glowColor = vColor * glow * 0.1;
    vec3 sparkleColor = vColor + vec3(0.5, 0.0, 0.0); // Shifts toward purple-ish

    float rimWidth = 0.1;
    float rimPower = 3.0;
    float rim = 1.0 - smoothstep(0.5 - rimWidth, 0.5, dist);
    rim = pow(rim, rimPower);


    vec3 baseColor = vColor * texColor.rgb;
    vec3 rimColor = vColor + vec3(0.2, 0.1, 0.0);
    baseColor *= mix(1.0, 0.3, spots * (1.0 - dist * 2.0));

    // vec3 finalColor = vColor * texColor.rgb + glowColor;
    vec3 finalColor = baseColor;
    // finalColor += rimColor * rim * 0.5;
    // finalColor += vColor * sparkle * 0.5 * vRadius;
    // finalColor *= glow;

    // finalColor += baseColor
    finalColor += rimColor * rim * 0.5;
    finalColor += sparkleColor  * sparkle * 0.2 * vRadius; // Add sparkle effect

    float alpha = texColor.a * (glow + rim * 0.5);
    
    gl_FragColor = vec4(finalColor, alpha);
}