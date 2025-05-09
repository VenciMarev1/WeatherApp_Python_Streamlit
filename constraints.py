from app import selected_city, city_lat, city_lon




globeHtml = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>3D Earth Globe</title>
    <style>
        body {{margin: 0; }}
        #globe-container {{
    width: 100%;
            height: 600px;
            overflow: hidden;
            position: relative;
        }}
        canvas {{display: block; }}
        #info {{
    position: absolute;
            top: 10px;
            width: 100%;
            text-align: center;
            color: white;
            font-family: Arial, sans-serif;
            pointer-events: none;
            z-index: 100;
            text-shadow: 1px 1px 2px black;
        }}
    </style>
</head>
<body>
    <div id="globe-container">
        <div id="info">Showing: {selected_city}</div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.min.js"></script>
        <script>
            // Initialize Three.js scene
            const container = document.getElementById('globe-container');
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x000000);

            // Camera setup
            const camera = new THREE.PerspectiveCamera(
                75, 
                container.clientWidth / container.clientHeight, 
                0.1, 
                1000
            );
            camera.position.z = 2.5;

            // Renderer setup
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer.domElement);

            // Orbit controls
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.minDistance = 1.5;
            controls.maxDistance = 5;

            // Create Earth
            const earthGeometry = new THREE.SphereGeometry(1, 64, 64);
            const earthMaterial = new THREE.MeshPhongMaterial({{
                map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_atmos_2048.jpg'),
                bumpMap: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_normal_2048.jpg'),
                bumpScale: 0.05,
                specularMap: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_specular_2048.jpg'),
                specular: new THREE.Color('grey'),
                shininess: 5
            }});
            const earth = new THREE.Mesh(earthGeometry, earthMaterial);
            scene.add(earth);

            // Add clouds
            const cloudGeometry = new THREE.SphereGeometry(1.01, 64, 64);
            const cloudMaterial = new THREE.MeshPhongMaterial({{
                map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_clouds_1024.png'),
                transparent: true,
                opacity: 0.4
            }});
            const clouds = new THREE.Mesh(cloudGeometry, cloudMaterial);
            scene.add(clouds);

            // Add stars
            const starGeometry = new THREE.BufferGeometry();
            const starMaterial = new THREE.PointsMaterial({{
                color: 0xffffff,
                size: 0.05
            }});

            const starVertices = [];
            for (let i = 0; i < 10000; i++) {{
                starVertices.push(
                    (Math.random() - 0.5) * 2000,
                    (Math.random() - 0.5) * 2000,
                    (Math.random() - 0.5) * 2000
                );
            }}

            starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
            const stars = new THREE.Points(starGeometry, starMaterial);
            scene.add(stars);

            // Lighting
            const ambientLight = new THREE.AmbientLight(0x333333);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
            directionalLight.position.set(5, 3, 5);
            scene.add(directionalLight);

            // Marker for selected city
            const markerGeometry = new THREE.SphereGeometry(0.03, 16, 16);
            const markerMaterial = new THREE.MeshBasicMaterial({{ color: 0xff0000 }});
            const marker = new THREE.Mesh(markerGeometry, markerMaterial);

            // Position marker for selected city
            const lat = {city_lat}
            const lon = {city_lon}
            const phi = (90 - lat) * (Math.PI / 180);
            const theta = (lon + 180) * (Math.PI / 180);

            marker.position.set(
                -Math.sin(phi) * Math.cos(theta),
                Math.cos(phi),
                Math.sin(phi) * Math.sin(theta)
            );

            // Add marker as a child of the earth so it rotates with it
            earth.add(marker);

            // Point camera at the marker
            camera.lookAt(marker.position);

            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);
                earth.rotation.y += 0.001;
                clouds.rotation.y += 0.0015;
                controls.update();
                renderer.render(scene, camera);
            }}

            // Handle resize
            function onWindowResize(){{
                camera.aspect = container.clientWidth / container.clientHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(container.clientWidth, container.clientHeight);
            }}

            window.addEventListener('resize', onWindowResize);

            animate();
        </script>
    </div>
</body>
</html>
    """