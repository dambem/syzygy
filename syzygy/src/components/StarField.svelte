<script>
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
  import { loadStarData } from '../services/starData';
  import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
  import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
  import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

  let container;
  let stars = [];

  onMount(async () => {
    stars = await loadStarData();

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 10000)
    const renderer = new THREE.WebGLRenderer();
    scene.background = new THREE.Color(0x000000);

    renderer.setSize(window.innerWidth, window.innerHeight)
    container.appendChild(renderer.domElement);  // Add this line!

    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(stars.length * 3);
    const colors = new THREE.Float32BufferAttribute(stars.length * 3, 3);
    const color = new THREE.Color();

    const radius = new Float32Array(stars.length)
    stars.forEach((star, i) => {
        positions[i*3] = star.x;
        positions[i*3 + 1] = star.y;
        positions[i*3 + 2] = star.z;
        // Set initial color to white
        color.setHSL((star.y / 200 + 1) / 2, 1.0, 0.5, THREE.SRGBColorSpace);
        colors.setXYZ(i, color.r, color.g, color.b);
        radius[i] = star.brightness;
    })
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', colors);
    geometry.setAttribute('radius', new THREE.BufferAttribute(radius, 1))

    // const material = new THREE.PointsMaterial({
    //         size: 1,
    //         color: 0xFFFFFF
    // });
    const sprite = new THREE.TextureLoader().load( 'textures/sprites/circle.png' );
    sprite.colorSpace = THREE.SRGBColorSpace;

    // Create custom shader material
    const material = new THREE.ShaderMaterial({
        uniforms: {
            sprite: { value: sprite },
            time: { value: 0.0 }

        },
        vertexShader: `
            attribute float radius;
            attribute vec3 color;
            varying vec3 vColor;
            varying float vRadius;

            void main() {
                vColor = color;
                vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                gl_PointSize = radius * 5.0 * (300.0 / -mvPosition.z);
                gl_Position = projectionMatrix * mvPosition;
            }
        `,
        fragmentShader: `
        uniform sampler2D sprite;
        uniform float time;

        varying vec3 vColor;
        varying float vRadius;
        float rand(vec2 co) {
            return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
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

    `,

        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending  // Important for glow effect
    });

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    camera.position.z = 200;
    const controls = new OrbitControls(camera, renderer.domElement);
    let selectedPoints = stars.filter(star => [4301, 4295, 4554, 4660, 4905, 5054, 5191].includes(star.hi));

    // Add raycaster for clicking individual stars
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();



    function onClick(event) {
        mouse.x = (event.clientX/ window.innerWidth) * 2 -1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 +1;
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObject(points);

        if (intersects.length > 0){
            const index = intersects[0].index;
            const colors = points.geometry.attributes.color;
            const star = stars[index];
            // Change color to red
            
            color.setHSL(1.0, 1.0, 0.5, THREE.SRGBColorSpace);
            colors.setXYZ(index, color.r, color.g, color.b);
            points.geometry.attributes.color.needsUpdate = true;
            selectedPoints.push(stars[index]);

            if (selectedPoints.length >= 2) {
                // Create line between two selected points
                // Create material with additional options available with Line2
                const material = new LineMaterial({
                        color: 0xff0000,
                        linewidth: 2, // In pixels
                        worldUnits: false, // Set true if you want the width in world units
                        dashed: false,
                        alphaToCoverage: true // Helps with antialiasing
                    });
                for (let i = 0; i < selectedPoints.length; i++) {
                    var geometry = new LineGeometry();
                    var linePositions = new Float32Array([
                    selectedPoints[i].x, selectedPoints[i].y, selectedPoints[i].z,
                    selectedPoints[i+1].x, selectedPoints[i+1].y, selectedPoints[i+1].z
                    ]);                    
                    geometry.setPositions(linePositions);
                    var line = new LineSegments2(geometry, material);
                    scene.add(line);   
                }
                selectedPoints = [];
            }
        }

    }


    container.addEventListener('click', onClick);  // For individual stars
    var lastHoveredIndex = -1
    function update(event) {
        mouse.x = (event.clientX/ window.innerWidth) * 2 -1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 +1;
        raycaster.setFromCamera(mouse, camera);
        // console.log("update!")
        var intersects_2 = raycaster.intersectObject(points);
        console.log(intersects_2)
        if (lastHoveredIndex !== -1) {
            const star = stars[lastHoveredIndex]
            color.setHSL((star.y / 200 + 1) / 2, 1.0, 0.5, THREE.SRGBColorSpace);
            colors.setXYZ(lastHoveredIndex, color.r, color.g, color.b);

        }
        if (intersects_2.length > 0) {
            const index = intersects_2[0].index;
            const star = stars[index]

            const colors = points.geometry.attributes.color;
            color.setHSL(1.0, 0.7, 0.5, THREE.SRGBColorSpace);
            colors.setXYZ(index, color.r, color.g, color.b);

            lastHoveredIndex = index;

            points.geometry.attributes.color.needsUpdate = true;
        }
    }


    container.addEventListener('mousemove', update);  // For individual stars

    function animate() {
        requestAnimationFrame(animate);
        material.uniforms.time.value = performance.now() / 1000;        
        controls.update();
        renderer.render(scene, camera);
    }

    animate();

    function handleResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight)
    }

    window.addEventListener('resize', handleResize)

    return () => {
        window.removeEventListener('resize', handleResize)
        container.removeChild(renderer.domElement)
    }
  })
</script>

<div bind:this={container} class="star-container"></div>

<style>
        .star-container {
        width: 100%;
        height: 100vh;
    }
</style>