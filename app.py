import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import streamlit.components.v1 as components
import json

# Page setup
st.set_page_config(page_title="Weather Globe 🌍", layout="wide")

st.title("🌍 Interactive Weather Globe")
st.markdown("""
Click on any location on the globe to see weather information for that area.
- Drag to rotate the view
- Scroll to zoom in/out
- Click on any point to select a location
""")


# Load city data (latitude/longitude)
@st.cache_data
def load_city_data():
    # This is a simplified version - in a real app you'd want a more comprehensive dataset
    with open("cities.json") as f:
        return json.load(f)


# Weather API function
def get_weather(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


# API key (in a real app, you'd want to secure this better)
api_key = "5dc93fe1be4655d1693091ba3dc6c853"


# Main app
def main():
    # Create two columns - left for weather, right for globe
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Weather Information")
        weather_placeholder = st.empty()

    with col2:
        # 3D Globe with click interaction
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
            <div id="info">Click on the globe to select a location</div>
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

                // Marker for selected city
                const markerGeometry = new THREE.SphereGeometry(0.02, 16, 16);
                const markerMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
                const marker = new THREE.Mesh(markerGeometry, markerMaterial);
                scene.add(marker);
                marker.visible = false;

                // Raycaster for click detection
                const raycaster = new THREE.Raycaster();
                const mouse = new THREE.Vector2();

                function onMouseClick(event) {
                    // Calculate mouse position in normalized device coordinates
                    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
                    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

                    // Update the raycaster
                    raycaster.setFromCamera(mouse, camera);

                    // Calculate objects intersecting the picking ray
                    const intersects = raycaster.intersectObject(earth);

                    if (intersects.length > 0) {
                        const point = intersects[0].point;
                        marker.position.copy(point);
                        marker.visible = true;

                        // Convert 3D point to lat/lon
                        const lat = 90 - (Math.acos(point.y / point.length()) * (180 / Math.PI);
                        const lon = ((270 + (Math.atan2(point.x, point.z)) * (180 / Math.PI)) % 360 - 180;

                        // Send data back to Streamlit
                        window.parent.postMessage({
                            type: 'globeClick',
                            lat: lat,
                            lon: lon
                        }, '*');
                    }
                }

                window.addEventListener('click', onMouseClick, false);

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

        # Display the globe
        globe = components.html(threejs_html, height=600)

    # Handle messages from the globe
    def handle_globe_message(msg):
        if msg.data.type == 'globeClick':
            lat = msg.data.lat
            lon = msg.data.lon

            try:
                # Get weather data
                weather_data = get_weather(lat, lon, api_key)

                # Extract info
                city_name = weather_data['name']
                temp_celsius = weather_data['main']['temp'] - 273.15
                weather_main = weather_data['weather'][0]['main']
                weather_description = weather_data['weather'][0]['description'].capitalize()
                humidity = weather_data['main']['humidity']
                wind_speed = weather_data['wind']['speed']
                pressure = weather_data['main']['pressure']
                cloudiness = weather_data['clouds']['all']
                icon_id = weather_data['weather'][0]['icon']

                # Get weather icon
                icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
                icon_response = requests.get(icon_url)
                icon_img = Image.open(BytesIO(icon_response.content))

                # Display weather info
                with weather_placeholder.container():
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

                    st.markdown(f"**Coordinates:** {lat:.2f}° N, {lon:.2f}° E")

            except Exception as e:
                weather_placeholder.error(f"Error getting weather data: {str(e)}")

    # Register the message handler
    components.html(
        """
        <script>
            window.addEventListener('message', function(event) {
                if (event.data.type === 'globeClick') {
                    window.parent.postMessage(event.data, '*');
                }
            }, false);
        </script>
        """,
        height=0
    )

    # Listen for messages from the iframe
    components.html(
        """
        <script>
            window.addEventListener('message', function(event) {
                if (event.data.type === 'globeClick') {
                    const msg = {data: event.data};
                    window.parent.streamlitBridge.setComponentValue(msg);
                }
            }, false);
        </script>
        """,
        height=0
    )


if __name__ == "__main__":
    main()