attribute float radius;
attribute vec3 color;
varying vec3 vColor;
varying float vRadius;

void main() {
    vColor = color;
    vRadius = radius; 

    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    gl_PointSize = radius * 3.0 * (300.0 / -mvPosition.z);
    gl_Position = projectionMatrix * mvPosition;
}