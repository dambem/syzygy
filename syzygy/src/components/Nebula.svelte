<script>
    import renderer from '@astrojs/svelte/server.js';
    import { init } from 'astro/virtual-modules/prefetch.js';
    import { onMount } from 'svelte';
    import * as THREE from 'three';
    let scene, camera;
    let container;
    let cloudParticles = [];
    let cloudGEO;
    let cloudMaterial;

    onMount(async () => {
        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight,1,1000)
        camera.position.x = 1;
        camera.rotation.x = 1.20;
        camera.rotation.y = -0.12;
        camera.rotation.z = 0.30;

        let ambient = new THREE.AmbientLight(0x555555)
        let directionalLight = new THREE.DirectionalLight(0xff8c19)
        directionalLight.position.set(0,0,0.5)

        let orangeLight = new THREE.PointLight(0xcc6600, 50, 450, 1.7)
        orangeLight.position.set(200,200,100)
        
        let redLight = new THREE.PointLight(0xd8547e, 50, 450, 1.7)
        redLight.position.set(100,300,100)
        
        let blueLight = new THREE.PointLight(0x3677ac, 50, 450, 1.7)
        blueLight.position.set(300,300,200)        // let orangeLight = new THREE.PointLight(0xcc6600, 50, 450, 1.7)
        // orangeLight.position.set(200,200,100)
        scene.add(ambient);
        scene.add(directionalLight)
        scene.add(orangeLight)
        scene.add(redLight)
        scene.add(blueLight)

        
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(window.innerWidth, window.innerHeight)
        scene.fog = new THREE.FogExp2(0x03544e, 0.001);
        renderer.setClearColor(scene.fog.color)
        container.appendChild(renderer.domElement);  // Add this line!

        let loader = new THREE.TextureLoader();
        
        loader.load("textures/sprites/100.png", function(texture) {
            // texture.colorSpace = THREE.SRGBColorSpace

            cloudGEO = new THREE.PlaneGeometry(500,500);
            cloudMaterial = new THREE.MeshLambertMaterial({
                map:texture,
                transparent: true,
                alphaTest: 0.20
            });

            for(let p=0; p<50; p++) {
                let cloud = new THREE.Mesh(cloudGEO, cloudMaterial);
                cloud.position.set(
                    Math.random()*800 -400,
                    500,
                    Math.random()*500-500
                );
                cloud.rotation.x = 1.20
                cloud.rotation.y -0.12
                cloud.rotation.z = Math.random()*2*Math.PI;
                cloud.material.opacity = 0.55;
                cloudParticles.push(cloud);
                scene.add(cloud);
                
            }
        })

        function render() {
            // cloudParticles.forEach(p => {
            //     p.rotation.z -= 0.001
            // })
            renderer.render(scene, camera)
            requestAnimationFrame(render)
        }
        render();
    })

</script>


<div bind:this={container} class="star-container">


</div>
