import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import streamlit.components.v1 as components
import math
import json

# Page setup
st.set_page_config(page_title="Weather Globe 🌍", layout="wide")

st.title("🌍 City Locator Globe")
st.markdown("""
Search for a city by name to locate it on the globe.
- Type a city name and press Enter
- The globe will automatically rotate to show the location
- Weather information will be displayed
""")

# API key (in production, use st.secrets)
api_key = "5dc93fe1be4655d1693091ba3dc6c853"

# Sample city data (in a real app, use a geocoding API)
city_data = {
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Sydney": {"lat": -33.8688, "lon": 151.2093},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Beijing": {"lat": 39.9042, "lon": 116.4074},
    "Rio de Janeiro": {"lat": -22.9068, "lon": -43.1729},
    "Cairo": {"lat": 30.0444, "lon": 31.2357}
}

# Create columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Search City")
    city_input = st.selectbox(
        "Select or type a city:",
        options=list(city_data.keys()),
        index=0,
        key="city_select"
    )

    # Display weather info
    if 'weather_data' in st.session_state:
        data = st.session_state.weather_data
        st.subheader(f"Weather in {st.session_state.selected_city}")

        col_a, col_b = st.columns([1, 2])
        with col_a:
            if 'weather_icon' in st.session_state:
                st.image(st.session_state.weather_icon, width=100)
        with col_b:
            st.markdown(f"**{data['weather'][0]['main']}**")
            st.caption(data['weather'][0]['description'].capitalize())

        temp_celsius = data['main']['temp'] - 273.15
        st.metric("Temperature", f"{temp_celsius:.1f} °C")
        st.metric("Humidity", f"{data['main']['humidity']}%")
        st.metric("Wind Speed", f"{data['wind']['speed']} m/s")
        st.metric("Pressure", f"{data['main']['pressure']} hPa")
        st.caption(f"Coordinates: {data['coord']['lat']:.2f}° N, {data['coord']['lon']:.2f}° E")

with col2:
    # Get coordinates for selected city
    selected_city = st.session_state.city_select
    city_lat = city_data[selected_city]["lat"]
    city_lon = city_data[selected_city]["lon"]

    # Convert lat/lon to Three.js coordinates
    phi = (90 - city_lat) * (math.PI / 180)
    theta = (city_lon + 180) * (math.PI / 180)

    # HTML/JavaScript for the 3D globe
    threejs_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>3D Earth Globe</title>
        <style>
            body {{ margin: 0; }}
            #globe-container {{
                width: 100%;
                height: 600px;
                overflow: hidden;
                position: relative;
            }}
            canvas {{ display: block; }}
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
                scene.add(marker);

                // Position marker for selected city
                const lat = {city_lat};
                const lon = {city_lon};
                const phi = (90 - lat) * (Math.PI / 180);
                const theta = (lon + 180) * (Math.PI / 180);

                marker.position.set(
                    -Math.sin(phi) * Math.cos(theta),
                    Math.cos(phi),
                    Math.sin(phi) * Math.sin(theta)
                );

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
                function onWindowResize() {{
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

    # Display the globe
    components.html(threejs_html, height=600)

# Get weather data when city changes
if 'selected_city' not in st.session_state or st.session_state.selected_city != st.session_state.city_select:
    st.session_state.selected_city = st.session_state.city_select
    city = st.session_state.city_select
    lat = city_data[city]["lat"]
    lon = city_data[city]["lon"]

    try:
        # Get weather data
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        st.session_state.weather_data = response.json()

        # Get weather icon
        icon_id = st.session_state.weather_data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        st.session_state.weather_icon = Image.open(BytesIO(requests.get(icon_url).content))

        # Force rerun to update display
        st.rerun()

    except Exception as e:
        st.error(f"Error fetching weather data: {str(e)}")