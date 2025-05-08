import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Weather Dashboard 🌦️", layout="wide")

st.markdown("""
This interactive 3D globe is created using Three.js with realistic textures and lighting.
- Rotates automatically
- Try zooming in/out with your mouse/trackpad
- Drag to rotate the view
""")

# Embed HTML + Three.js Globe
threejs_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>3D Earth Globe</title>
    <style>
        body { margin: 0; overflow: hidden; }
        canvas { display: block; width: 100%; height: 100%; }
        #info {
            position: absolute;
            top: 10px;
            width: 100%;
            text-align: center;
            color: white;
            font-family: Arial, sans-serif;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div id="info">Drag to rotate • Scroll to zoom</div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.min.js"></script>
    <script>
        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000000);

        // Camera
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 2.5;

        // Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        document.body.appendChild(renderer.domElement);

        // Add orbit controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 1.5;
        controls.maxDistance = 5;

        // Earth geometry
        const geometry = new THREE.SphereGeometry(1, 64, 64);

        // Load textures
        const textureLoader = new THREE.TextureLoader();
        const texture = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_atmos_2048.jpg');
        const bumpMap = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_normal_2048.jpg');
        const specularMap = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_specular_2048.jpg');

        // Earth material
        const material = new THREE.MeshPhongMaterial({
            map: texture,
            bumpMap: bumpMap,
            bumpScale: 0.05,
            specularMap: specularMap,
            specular: new THREE.Color('grey'),
            shininess: 5
        });

        // Earth mesh
        const earth = new THREE.Mesh(geometry, material);
        scene.add(earth);

        // Clouds
        const cloudGeometry = new THREE.SphereGeometry(1.01, 64, 64);
        const cloudMaterial = new THREE.MeshPhongMaterial({
            map: textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_clouds_1024.png'),
            transparent: true,
            opacity: 0.4
        });
        const clouds = new THREE.Mesh(cloudGeometry, cloudMaterial);
        scene.add(clouds);

        // Stars
        const starGeometry = new THREE.BufferGeometry();
        const starMaterial = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 0.05
        });

        const starVertices = [];
        for (let i = 0; i < 10000; i++) {
            const x = (Math.random() - 0.5) * 2000;
            const y = (Math.random() - 0.5) * 2000;
            const z = (Math.random() - 0.5) * 2000;
            starVertices.push(x, y, z);
        }

        starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
        const stars = new THREE.Points(starGeometry, starMaterial);
        scene.add(stars);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x333333);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(5, 3, 5);
        scene.add(directionalLight);

        // Animation loop
        function animate() {
            requestAnimationFrame(animate);
            earth.rotation.y += 0.001;
            clouds.rotation.y += 0.0015;
            controls.update();
            renderer.render(scene, camera);
        }

        // Handle window resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        animate();
    </script>
</body>
</html>
"""



# Input for city and API key
city = st.text_input("Enter a city name:", "Sofia")
api_key = "5dc93fe1be4655d1693091ba3dc6c853"



if city and api_key:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract info
        city_name = data['name']
        temp_celsius = data['main']['temp'] - 273.15
        weather_main = data['weather'][0]['main']
        weather_description = data['weather'][0]['description'].capitalize()
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        pressure = data['main']['pressure']
        cloudiness = data['clouds']['all']
        icon_id = data['weather'][0]['icon']

        # Get weather icon
        icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        icon_response = requests.get(icon_url)
        icon_img = Image.open(BytesIO(icon_response.content))

        # Display
        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(icon_img, width=120)
            st.markdown(f"### {weather_main}")
            st.caption(weather_description)

        with col2:
            st.markdown(f"## {city_name}")
            st.metric("🌡 Temperature", f"{temp_celsius:.2f} °C")
            st.metric("💧 Humidity", f"{humidity} %")
            st.metric("🌬 Wind Speed", f"{wind_speed} m/s")
            st.metric("📈 Pressure", f"{pressure} hPa")
            st.metric("☁️ Cloudiness", f"{cloudiness} %")

        st.markdown("---")

        # Optional: fancy globe background (animated GIF)
        st.markdown("#### 🌐 World Weather Vibe")
        components.html(threejs_html, height=600)

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
    except (KeyError, ValueError) as e:
        st.error(f"Error processing data: {e}")