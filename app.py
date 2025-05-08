import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import streamlit.components.v1 as components
import math
import time

# Page setup
st.set_page_config(page_title="Weather Globe 🌍", layout="wide")

st.title("🌍 City Locator Globe")
st.markdown("""
Search for a city by name to locate it on the globe.
- Type a city name and press Enter
- The globe will automatically rotate to show the location
- Weather information will be displayed
""")

# API keys (use `st.secrets` in production)
OPENWEATHER_API_KEY = "5dc93fe1be4655d1693091ba3dc6c853"  # Replace with your key
NOMINATIM_USER_AGENT = "CityLocatorApp/1.0 (vencislavmarev21a@gmail.com)"  # Must be a valid email


def get_city_coordinates(city_name):
    """Fetch latitude and longitude for a city using Nominatim API"""
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': city_name,
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': NOMINATIM_USER_AGENT  # Required to avoid 403 error
    }

    try:
        time.sleep(1)  # Respect Nominatim's rate limit (1 request per second)
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data:
            return {
                'lat': float(data[0]['lat']),
                'lon': float(data[0]['lon']),
                'display_name': data[0]['display_name']
            }
        else:
            st.error(f"No coordinates found for {city_name}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching coordinates: {str(e)}")
        return None


def get_weather_data(lat, lon):
    """Fetch weather data from OpenWeatherMap"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()

        # Get weather icon
        icon_id = weather_data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        weather_icon = Image.open(BytesIO(requests.get(icon_url).content))

        return weather_data, weather_icon
    except Exception as e:
        st.error(f"Error fetching weather data: {str(e)}")
        return None, None


# Initialize session state
if 'city_data' not in st.session_state:
    st.session_state.city_data = {
        "London": {"lat": 51.5074, "lon": -0.1278, "display_name": "London, UK"}
    }

# Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Search City")
    city_input = st.text_input(
        "Enter a city name:",
        value="London",
        key="city_input"
    )

    if st.button("Locate") or 'city_input' in st.session_state:
        if city_input:
            with st.spinner(f"Searching for {city_input}..."):
                city_info = get_city_coordinates(city_input)

                if city_info:
                    st.session_state.city_data[city_input] = {
                        "lat": city_info['lat'],
                        "lon": city_info['lon'],
                        "display_name": city_info['display_name']
                    }
                    st.session_state.selected_city = city_input

                    # Fetch weather data
                    weather_data, weather_icon = get_weather_data(
                        city_info['lat'],
                        city_info['lon']
                    )

                    if weather_data:
                        st.session_state.weather_data = weather_data
                        st.session_state.weather_icon = weather_icon
                        st.rerun()

    # Display weather info if available
    if 'weather_data' in st.session_state and 'selected_city' in st.session_state:
        data = st.session_state.weather_data
        city_name = st.session_state.selected_city
        display_name = st.session_state.city_data[city_name]['display_name']

        st.subheader(f"Weather in {city_name}")
        st.caption(display_name)

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
    # Get selected city (default to London if none selected)
    selected_city = st.session_state.get('selected_city', "London")
    city_info = st.session_state.city_data.get(selected_city)

    if city_info:
        city_lat = city_info["lat"]
        city_lon = city_info["lon"]

        # Simplified Three.js Globe (to avoid CORS issues)
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

            // Create Earth (using a simple color instead of texture to avoid CORS)
            const earthGeometry = new THREE.SphereGeometry(1, 32, 32);
            const earthMaterial = new THREE.MeshPhongMaterial({{
                color: 0x1a66ff,
                specular: 0x111111,
                shininess: 5
            }});
            const earth = new THREE.Mesh(earthGeometry, earthMaterial);
            scene.add(earth);

            // Add marker for selected city
            const markerGeometry = new THREE.SphereGeometry(0.03, 16, 16);
            const markerMaterial = new THREE.MeshBasicMaterial({{ color: 0xff0000 }});
            const marker = new THREE.Mesh(markerGeometry, markerMaterial);

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

            // Add marker as a child of the earth so it rotates with it
            earth.add(marker);

            // Point camera at the marker
            camera.lookAt(marker.position);

            // Lighting
            const ambientLight = new THREE.AmbientLight(0x333333);
            scene.add(ambientLight);

            const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
            directionalLight.position.set(5, 3, 5);
            scene.add(directionalLight);

            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);
                earth.rotation.y += 0.001;
                controls.update();
                renderer.render(scene, camera);
            }}

            animate();
        </script>
    </div>
</body>
</html>
        """
        components.html(threejs_html, height=600)