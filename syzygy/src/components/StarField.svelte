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
  import { LuminosityShader } from 'three/addons/shaders/LuminosityShader.js';
  import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
  import { RGBShiftShader } from 'three/addons/shaders/RGBShiftShader.js';
  import { FontLoader } from 'three/addons/loaders/FontLoader.js';
  import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';
  import { gsap } from 'gsap';
//   let toggleScale = false;

  let container;
  let stars = [];
  let scaled = true;
  let camera_s = true;
  let animationStartTime;
  let animationProgress = 0; // 1 = fully scaled, 0 = fully unscaled
  let animationDuration = 2; // Animation duration in milliseconds
  const state = { animationProgress: 1 };

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
        stars: [4301, 4295, 4660, 4905, 5191, 5054, 5055 , 5054 ],
        color: 0xff0000,
        visible: false,
        lines: [] // Store line objects for removal
    },
      "aries": {
    "name": "Ursa Major Additional",
    "stars": [    4335, 4033, 4069, 3775, 3888, 3569, 3594, 4377, 4518    ],
    "color": 16711680,
    "visible": false,
    "lines": []
  },

    }



    
  onMount(async () => {
    stars = await loadStarData();
    const scene = new THREE.Scene();
    const playButton = document.querySelector('.play-button');
    const viewButton = document.querySelector('.view-button')

    const scaleButton = document.querySelector('.scale-button')
    const textureLoader = new THREE.TextureLoader()
    const earthNightTexture = textureLoader.load('./textures/sprites/earth_night.jpg')
    const earthNormal = textureLoader.load('./textures/sprites/earth_normal.tif')
    const earthSpecular = textureLoader.load('./textures/sprites/earth_specular.tif')
    let textGeo, textMesh1;
    let materials;
    earthNightTexture.colorSpace = THREE.SRGBColorSpace
    let currentAnimation = 'linear';
    const camera = new THREE.PerspectiveCamera(1, window.innerWidth/window.innerHeight, 0.1, 1000000000)
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
                color: 0xffff00,
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
    scene.add(new THREE.AmbientLight(0xffffff, 0.5))
    const loader = new FontLoader();

    scene.background = new THREE.Color(0x000000);
    renderer.setSize(window.innerWidth, window.innerHeight)
    container.appendChild(renderer.domElement);  // Add this line!

    const geometry = new THREE.BufferGeometry();
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
    loader.load('./fonts/optimer_regular.typeface.json', function (font) {
        const geometry_t = new TextGeometry('syzygy', {
            font:font,
            size: 6,
            height: 3
        })

        const textMesh1 = new THREE.Mesh(geometry_t, [
            new THREE.MeshPhongMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 0.35 }),
            new THREE.MeshPhongMaterial({ color: 0x5544ff, emissive: 0x5544ff, emissiveIntensity: 0.50 })
            ])

        // textMesh1.castShadow = true
        textMesh1.position.z = 1000
        textMesh1.position.x -= 12
        textMesh1.position.y -= 20
        textMesh1.scale.z = 0.01
        scene.add(textMesh1)
    })
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

    const effect2 = new ShaderPass( RGBShiftShader );
    effect2.uniforms[ 'amount' ].value = 0.0002;
    
    composer.addPass( effect2 );
    composer.addPass(bloomPass);
    camera.position.z = 6000;
    
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
    const options = {
        duration: 2.0,
        ease: "power2.inOut"
    }

    mouseOver.add(guiState, 'selectedStar')
    .name('Label')
    .listen();

    function toggleCamera() {
        camera_s = !camera_s;
    }
    

    viewButton.addEventListener('click', ()=> {
        camera_s = !camera_s;
        gsap.to(camera.position, {
        z: camera_s ? 500 : 0,
        duration: options.duration,
        ease: options.ease,

        onComplete: () => {
            scene.remove(textMesh1);
            camera.fov = camera_s ? 1: 90
            camera.updateProjectionMatrix();

        }
    });
    })
    playButton.addEventListener('click', ()=> {
        gsap.to(camera.position, {
        z: 150,
        duration: options.duration,
        ease: options.ease,
        onComplete: () => {
            scene.remove(textMesh1);
            playButton.remove()        }
    });
    })
    toggleScale()
    function toggleScale() {
    scaled = !scaled;
    gsap.to(state, {
      animationProgress: scaled ? 0 : 1,
      duration: animationDuration,
      ease: 'power2.inOut',
      onUpdate: function() {
        animationProgress = state.animationProgress;
        console.log("Animation Progress:", state.animationProgress);
        updatePositions(animationProgress);
      },
    });
    }
    scaleButton.addEventListener('click', toggleScale)

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
        material.uniforms.time.value = performance.now()/1000;        
        controls.update();
        // points.rotation.z += 0.0001
        raycaster.setFromCamera(mouse, camera);
        composer.render();
    }


    function updatePositions(progress) {
        stars.forEach((star, i) => {
            const scaledX = star.distance * star.x;
            const scaledY = star.distance * star.y;
            const scaledZ = star.distance * star.z;

            const interpolatedX = star.x + (scaledX - star.x) * progress;
            const interpolatedY = star.y + (scaledY - star.y) * progress;
            const interpolatedZ = star.z + (scaledZ - star.z) * progress;

            positions[i * 3] = interpolatedX;
            positions[i * 3 + 1] = interpolatedY;
            positions[i * 3 + 2] = interpolatedZ;
        });

        geometry.attributes.position.needsUpdate = true;
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

<div bind:this={container} class="star-container">
    <!-- <button class="scale-button">Toggle Scale</button> -->
    <div class="scale-button">
        <p style='color:white;'>
            <b>@</b>
        </p>
    </div>
    <div class="view-button button">
        <p style='color:white;'>
            <b>V</b>
        </p>
    </div>
    <div class="play-button">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="1">
            <polygon points="5,3 19,12 5,21" fill="white"/>
        </svg>
    </div>
</div>

<style>
        .star-container {
        width: 100%;
        height: 100vh;
        overflow: hidden;
    }
    .button {
        position: absolute;
        top: 40%;
        left: 10%;
        transform: translate(-50%, -50%);
        width: 80px;
        height: 80px;
        background: rgba(30, 30, 30, 0.3);
        border-radius: 25%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    .button:hover {
        background: rgba(0, 0, 0, 0.5);
        transform: translate(-50%, -50%) scale(1.1);
    }
    .scale-button {
        position: absolute;
        top: 20%;
        left: 10%;
        transform: translate(-50%, -50%);
        width: 80px;
        height: 80px;
        background: rgba(30, 30, 30, 0.3);
        border-radius: 25%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    .scale-button:hover {
        background: rgba(0, 0, 0, 0.5);
        transform: translate(-50%, -50%) scale(1.1);
    }
    .play-button {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 80px;
        height: 80px;
        background: rgba(0, 0, 0, 0.3);
        border-radius: 25%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }

    .play-button:hover {
        background: rgba(0, 0, 0, 0.5);
        transform: translate(-50%, -50%) scale(1.1);
    }
</style>