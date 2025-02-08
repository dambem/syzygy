<script>
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
  import { loadStarData } from '../services/starData';
  import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
  import { LineGeometry } from 'three/addons/lines/LineGeometry.js';
  import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
  import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
  import vertexShader from '../shaders/particle.vert?raw';
  import fragmentShader from '../shaders/particle.frag?raw';
  import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
  import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
  import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';

  let container;
  let stars = [];
  const class_to_color = {
    'O': [0.667, 1.000, 0.500],  // Deep blue
    'B': [0.581, 0.730, 0.780],  // Light blue
    'A': [0.000, 0.000, 1.000],  // Pure white
    'F': [0.142, 1.000, 0.890],  // Very light yellow
    'G': [0.136, 1.000, 0.740],  // Yellow
    'K': [0.108, 1.000, 0.500],  // Orange
    'M': [0.011, 1.000, 0.690],   // Reddish
    'S': [0.050, 1.000, 0.500],   // Orange-red
    'C': [0.029, 1.000, 0.500]   // Deep red

    }
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
    const textureLoader = new THREE.TextureLoader()
    const earthNightTexture = textureLoader.load('./textures/sprites/earth_night.jpg')
    earthNightTexture.colorSpace = THREE.SRGBColorSpace

    const camera = new THREE.PerspectiveCamera(1, window.innerWidth/window.innerHeight, 0.1, 10000000)
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

    renderer.setSize(window.innerWidth, window.innerHeight)
    container.appendChild(renderer.domElement);  // Add this line!

    const geometry = new THREE.BufferGeometry();
    const sphereGeometry = new THREE.SphereGeometry(0.05, 16, 16);
    const material2 = new THREE.MeshStandardMaterial({
        map: earthNightTexture,
        metalness: 0,
        roughness: 1
    });
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0xffffff, 20);
    pointLight.position.set(-1, 1, -1);
    scene.add(pointLight);
    const sphere = new THREE.Mesh(sphereGeometry, material2);
    scene.add(sphere);
    
    const positions = new Float32Array(stars.length * 3);
    const colors = new THREE.Float32BufferAttribute(stars.length * 3, 3);
    const color = new THREE.Color();

    const radius = new Float32Array(stars.length)
    stars.forEach((star, i) => {
        positions.set([star.x, star.y, star.z], i * 3);
        color.setHSL(
            class_to_color[star.class][0],  // hue
            class_to_color[star.class][1],  // saturation
            class_to_color[star.class][2]   // lightness
            , THREE.SRGBColorSpace
        );

        colors.setXYZ(i, color.r, color.g, color.b);
        radius[i] = star.brightness;
    })

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', colors);
    geometry.setAttribute('radius', new THREE.BufferAttribute(radius, 1))
 
    const sprite = new THREE.TextureLoader().load( 'textures/sprites/circle.png' );
    sprite.colorSpace = THREE.SRGBColorSpace;
 
    const material = new THREE.ShaderMaterial({
        uniforms: {
            sprite: { value: sprite },
            time: { value: 0.0 }

        },
        vertexShader: vertexShader,
        fragmentShader: fragmentShader,
        transparent: true,
        depthWrite: false,
        blending: THREE.AdditiveBlending  // Important for glow effect
    });

    const points = new THREE.Points(geometry, material);
    scene.add(points);
    const bloomParams = {
        exposure: 5,
        bloomStrength: 2.5,
        bloomThreshold: 0.5,
        bloomRadius: 0.1
    };
    const renderScene = new RenderPass(scene, camera);
        const bloomPass = new UnrealBloomPass(
        new THREE.Vector2(window.innerWidth, window.innerHeight),
        bloomParams.bloomStrength,
        bloomParams.bloomRadius,
        bloomParams.bloomThreshold
    );
    const composer = new EffectComposer(renderer);
    composer.addPass(renderScene);
    composer.addPass(bloomPass);
    camera.position.z = 150;
    
    const controls = new OrbitControls(camera, renderer.domElement);
    let selectedPoints = [];

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

    // container.addEventListener('click', onClick);  // For individual stars
    var lastHoveredIndex = -1
    function update(event) {
        mouse.x = (event.clientX/ window.innerWidth) * 2 -1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 +1;
        raycaster.setFromCamera(mouse, camera);
        var intersects_2 = raycaster.intersectObject(points);
        if (lastHoveredIndex !== -1) {
            const star = stars[lastHoveredIndex]
            color.setHSL(
            class_to_color[star.class][0],  // hue
            class_to_color[star.class][1],  // saturation
            class_to_color[star.class][2]   // lightness
            , THREE.SRGBColorSpace
            );            
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
        material.uniforms.time.value = performance.now()/10;        
        controls.update();
        raycaster.setFromCamera(mouse, camera);
        composer.render();
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