<script>
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
  import { loadStarData } from '../services/starData';
  import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
  import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
  import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
  import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
  let container;
  let stars = [];

  const constellations = {
    ursa_major: {
        name: "Ursa Major",
        stars: [4301, 4295, 4660, 4905, 5191, 5054, 5055 , 5054, 5062 ],
        color: 0xff0000,
        visible: false,
        lines: [] // Store line objects for removal
    }
    }
  onMount(async () => {
    stars = await loadStarData();

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(1, window.innerWidth/window.innerHeight, 0.1, 10000)
    const renderer = new THREE.WebGLRenderer();
    const gui = new GUI();
    const mouseOver = gui.addFolder('SelectedStar');
    const guiState = { selectedStar: 'No star selected' };

    const constellationsFolder = gui.addFolder('Constellations');
    Object.keys(constellations).forEach(constId => {
    const constellation = constellations[constId];
    constellationsFolder.add(constellation, 'visible')
        .name(constellation.name)
        .onChange(() => updateConstellation(constId));
    });
    function updateConstellation(constId) {
        const constellation = constellations[constId];
        
        // Remove existing lines if they exist
        constellation.lines.forEach(line => {
            scene.remove(line);
        });
        constellation.lines = [];
        
        // If visible, draw new lines
        if (constellation.visible) {
            const selectedPoints = stars.filter(star => 
                constellation.stars.includes(star.hi)
            );
            
            const material = new LineMaterial({
                color: constellation.color,
                linewidth: 2,
                worldUnits: false,
                dashed: false,
                alphaToCoverage: true
            });

            // Create lines between consecutive points
            for (let i = 1; i < selectedPoints.length; i++) {
                const geometry = new LineGeometry();
                const linePositions = new Float32Array([
                    selectedPoints[i-1].x, selectedPoints[i-1].y, selectedPoints[i-1].z,
                    selectedPoints[i].x, selectedPoints[i].y, selectedPoints[i].z
                ]);
                
                geometry.setPositions(linePositions);
                const line = new LineSegments2(geometry, material);
                scene.add(line);
                constellation.lines.push(line);
            }
            }
    }
    function addConstellation(id, name, stars, color = 0xffffff) {
    constellations[id] = {
        name: name,
        stars: stars,
        color: color,
        visible: false,
        lines: []
    };
    
    // Add GUI control for new constellation
    constellationsFolder.add(constellations[id], 'visible')
        .name(name)
        .onChange(() => updateConstellation(id));
    }
    addConstellation('cassiopeia', 'Cassiopeia', [1234, 5678, 9012], 0x0000ff);

    scene.background = new THREE.Color(0x000000);
    const fogColor = new THREE.Color(0x000010);
    scene.fog = new THREE.FogExp2(fogColor, 0.02);

    renderer.setSize(window.innerWidth, window.innerHeight)
    container.appendChild(renderer.domElement);  // Add this line!

    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(stars.length * 3);
    const colors = new THREE.Float32BufferAttribute(stars.length * 3, 3);
    const color = new THREE.Color();

    const radius = new Float32Array(stars.length)
    stars.forEach((star, i) => {
        positions.set([star.x, star.y, star.z], i * 3);
        color.setHSL((star.y / 200 + 1) / 2, 1.0, 0.5, THREE.SRGBColorSpace);
        // const hue = Math.floor((200 + 1) / 2));
        // color.setHex(`${hue.toString(16)}${hue.toString(16)}${hue.toString(16)}`);
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
    let selectedPoints = [];
    // 1948, 1903
    // Add raycaster for clicking individual stars
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();



    function onClick(event) {
        const rect = renderer.domElement.getBoundingClientRect();

        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
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
            if (selectedPoints && selectedPoints.length >= 2) {
                // Create line between two selected points
                // Create material with additional options available with Line2
                console.log(selectedPoints)
                const material = new LineMaterial({
                        color: 0xffff00,
                        linewidth: 2, // In pixels
                        worldUnits: false, // Set true if you want the width in world units
                        dashed: false,
                        alphaToCoverage: true // Helps with antialiasing
                    });
                for (let i = 1; i < selectedPoints.length; i++) {
                    var geometry2 = new LineGeometry();
                    var linePositions = new Float32Array([
                        selectedPoints[i-1].x, selectedPoints[i-1].y, selectedPoints[i-1].z,
                        selectedPoints[i].x, selectedPoints[i].y, selectedPoints[i].z
                    ]);                    
                    geometry2.setPositions(linePositions);
                    var line = new LineSegments2(geometry2, material);
                    scene.add(line);   
                }
                selectedPoints = [];
            }
        }

    }


    mouseOver.add(guiState, 'selectedStar')
    .name('Label')
    .listen();

    container.addEventListener('click', onClick);  // For individual stars
    var lastHoveredIndex = -1
    function update(event) {
        mouse.x = (event.clientX/ window.innerWidth) * 2 -1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 +1;
        raycaster.setFromCamera(mouse, camera);
        var intersects_2 = raycaster.intersectObject(points);
        if (lastHoveredIndex !== -1) {
            const star = stars[lastHoveredIndex]
            color.setHSL((star.y / 200 + 1) / 2, 1.0, 0.5, THREE.SRGBColorSpace);
            colors.setXYZ(lastHoveredIndex, color.r, color.g, color.b);

        }
        if (intersects_2.length > 0) {
            const index = intersects_2[0].index;
            const star = stars[index]
            guiState.selectedStar = 'id:'+ star.hi + 'c:' + star.class || 'Unnamed star';

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
        raycaster.setFromCamera(mouse, camera);

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
        overflow: hidden;
    }
</style>