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
    console.log(stars)

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000)
    const renderer = new THREE.WebGLRenderer();
    scene.background = new THREE.Color(0x000000);

    renderer.setSize(window.innerWidth, window.innerHeight)
    container.appendChild(renderer.domElement);  // Add this line!

    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(stars.length * 3);
    const colors = new Float32Array(stars.length * 3);

    stars.forEach((star, i) => {
        positions[i*3] = star.x;
        positions[i*3 + 1] = star.y;
        positions[i*3 + 2] = star.z;
        // Set initial color to white
        colors[i*3] = 1;
        colors[i*3 + 1] = 1;
        colors[i*3 + 2] = 1;
    })
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    // const material = new THREE.PointsMaterial({
    //         size: 1,
    //         color: 0xFFFFFF
    // });
    const sprite = new THREE.TextureLoader().load( 'textures/sprites/circle.png' );
    sprite.colorSpace = THREE.SRGBColorSpace;

    const material = new THREE.PointsMaterial( { size: 1,
         sizeAttenuation: true,
          map: sprite, alphaTest: 0.5, 
          transparent: true, vertexColors: true} );

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    camera.position.z = 200;
    const controls = new OrbitControls(camera, renderer.domElement);
    let selectedPoints = [];

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
            const colors = points.geometry.attributes.color.array;
            // Change color to red
            selectedPoints.push(stars[index]);

            console.log("Intserects!!")
            colors[index * 3] = 1;    // R
            colors[index * 3 + 1] = 0; // G
            colors[index * 3 + 2] = 0; // B
            points.geometry.attributes.color.needsUpdate = true;

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
                const lineMaterial = new THREE.LineBasicMaterial({
                    color: 0xff0000,
                    linewidth: 5

                });
                for (let i = 0; i < selectedPoints.length; i++) {
                    
                    var lineGeometry = new THREE.BufferGeometry();
                    var geometry = new LineGeometry();

                    var linePositions = new Float32Array([
                    selectedPoints[i].x, selectedPoints[i].y, selectedPoints[i].z,
                    selectedPoints[i+1].x, selectedPoints[i+1].y, selectedPoints[i+1].z
                    ]);                    
                    geometry.setPositions(linePositions);
                    var line = new LineSegments2(geometry, material);
                    scene.add(line);
                   
                }
                
                function animateLines() {
        let allComplete = true;
        
        lines.forEach((lineData, index) => {
            if (lineData.progress < 1) {
                allComplete = false;
                lineData.progress += 0.02; // Adjust speed by changing this value
                
                // Calculate current end point
                const currentEnd = {
                    x: lineData.startPoint.x + (lineData.endPoint.x - lineData.startPoint.x) * lineData.progress,
                    y: lineData.startPoint.y + (lineData.endPoint.y - lineData.startPoint.y) * lineData.progress,
                    z: lineData.startPoint.z + (lineData.endPoint.z - lineData.startPoint.z) * lineData.progress
                };
                
                // Update line geometry
                const newPositions = new Float32Array([
                    lineData.startPoint.x, lineData.startPoint.y, lineData.startPoint.z,
                    currentEnd.x, currentEnd.y, currentEnd.z
                ]);
                lineData.line.geometry.setPositions(newPositions);
                lineData.line.geometry.attributes.position.needsUpdate = true;
            }
        });
        
        if (!allComplete) {
            requestAnimationFrame(animateLines);
        }
    }
    animateLines();

                // Reset selected points
                selectedPoints = [];
            }
        }

    }


    container.addEventListener('click', onClick);  // For individual stars

    function animate() {
        requestAnimationFrame(animate);
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