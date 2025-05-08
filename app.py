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
    # Europe
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Berlin": {"lat": 52.5200, "lon": 13.4050},
    "Madrid": {"lat": 40.4168, "lon": -3.7038},
    "Rome": {"lat": 41.9028, "lon": 12.4964},
    "Moscow": {"lat": 55.7558, "lon": 37.6173},
    "Istanbul": {"lat": 41.0082, "lon": 28.9784},
    "Vienna": {"lat": 48.2082, "lon": 16.3738},
    "Prague": {"lat": 50.0755, "lon": 14.4378},
    "Amsterdam": {"lat": 52.3676, "lon": 4.9041},
    "Brussels": {"lat": 50.8503, "lon": 4.3517},
    "Athens": {"lat": 37.9838, "lon": 23.7275},
    "Sofia": {"lat": 42.6977, "lon": 23.3219},
    "Plovdiv": {"lat": 42.1354, "lon": 24.7453},
    "Bucharest": {"lat": 44.4268, "lon": 26.1025},
    "Warsaw": {"lat": 52.2297, "lon": 21.0122},
    "Budapest": {"lat": 47.4979, "lon": 19.0402},
    "Lisbon": {"lat": 38.7223, "lon": -9.1393},
    "Stockholm": {"lat": 59.3293, "lon": 18.0686},
    "Oslo": {"lat": 59.9139, "lon": 10.7522},

    # North America
    "New York": {"lat": 40.7128, "lon": -74.0060},
    "Los Angeles": {"lat": 34.0522, "lon": -118.2437},
    "Chicago": {"lat": 41.8781, "lon": -87.6298},
    "Toronto": {"lat": 43.6532, "lon": -79.3832},
    "Vancouver": {"lat": 49.2827, "lon": -123.1207},
    "Mexico City": {"lat": 19.4326, "lon": -99.1332},
    "Miami": {"lat": 25.7617, "lon": -80.1918},
    "Houston": {"lat": 29.7604, "lon": -95.3698},
    "Montreal": {"lat": 45.5017, "lon": -73.5673},

    # South America
    "Rio de Janeiro": {"lat": -22.9068, "lon": -43.1729},
    "Sao Paulo": {"lat": -23.5505, "lon": -46.6333},
    "Buenos Aires": {"lat": -34.6037, "lon": -58.3816},
    "Lima": {"lat": -12.0464, "lon": -77.0428},
    "Bogota": {"lat": 4.7110, "lon": -74.0721},
    "Santiago": {"lat": -33.4489, "lon": -70.6693},

    # Asia
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Beijing": {"lat": 39.9042, "lon": 116.4074},
    "Shanghai": {"lat": 31.2304, "lon": 121.4737},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694},
    "Seoul": {"lat": 37.5665, "lon": 126.9780},
    "Singapore": {"lat": 1.3521, "lon": 103.8198},
    "Bangkok": {"lat": 13.7563, "lon": 100.5018},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Dubai": {"lat": 25.2048, "lon": 55.2708},
    "Jerusalem": {"lat": 31.7683, "lon": 35.2137},

    # Africa
    "Cairo": {"lat": 30.0444, "lon": 31.2357},
    "Nairobi": {"lat": -1.2864, "lon": 36.8172},
    "Cape Town": {"lat": -33.9249, "lon": 18.4241},
    "Johannesburg": {"lat": -26.2041, "lon": 28.0473},
    "Casablanca": {"lat": 33.5731, "lon": -7.5898},

    # Oceania
    "Sydney": {"lat": -33.8688, "lon": 151.2093},
    "Melbourne": {"lat": -37.8136, "lon": 144.9631},
    "Auckland": {"lat": -36.8485, "lon": 174.7633},
    "Brisbane": {"lat": -27.4698, "lon": 153.0251},
    "Perth": {"lat": -31.9505, "lon": 115.8605}
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
    phi = (90 - city_lat) * (math.pi / 180)
    theta = (city_lon + 180) * (math.pi / 180)

    # HTML/JavaScript for the 3D globe
    threejs_html = f"""
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
            const markerGeometry = new THREE.SphereGeometry(0.03, 3, 3);
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