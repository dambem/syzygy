<script>
  import { onMount } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
  import { loadStarData } from '../services/starData';

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

    stars.forEach((star, i) => {
        positions[i*3] = star.x;
        positions[i*3 + 1] = star.y;
        positions[i*3 + 2] = star.z;
    })
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    // const material = new THREE.PointsMaterial({
    //         size: 1,
    //         color: 0xFFFFFF
    // });
    const sprite = new THREE.TextureLoader().load( 'textures/sprites/circle.png' );
    sprite.colorSpace = THREE.SRGBColorSpace;

    const material = new THREE.PointsMaterial( { size: 1, sizeAttenuation: true, map: sprite, alphaTest: 0.5, transparent: true } );

    const points = new THREE.Points(geometry, material);
    scene.add(points);

    camera.position.z = 200;
    const controls = new OrbitControls(camera, renderer.domElement);

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