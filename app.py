import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Weather Globe 🌍", layout="wide")

st.title("🌍 Interactive Weather Globe")
st.markdown("""
Click on any location on the globe to see weather information for that area.
- Drag to rotate the view
- Scroll to zoom in/out
- Click on any point to select a location
""")

# API key (in production, use st.secrets)
api_key = "5dc93fe1be4655d1693091ba3dc6c853"

# Create columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Weather Information")
    weather_placeholder = st.empty()  # Placeholder for weather info

with col2:
    # HTML/JavaScript for the 3D globe
    threejs_html = """
           <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>3D Earth Globe</title>
            <style>
                body { margin: 0; }
                #globe-container {
                    width: 100%;
                    height: 600px;
                    overflow: hidden;
                    position: relative;
                }
                canvas { display: block; }
                #info {
                    position: absolute;
                    top: 10px;
                    width: 100%;
                    text-align: center;
                    color: white;
                    font-family: Arial, sans-serif;
                    pointer-events: none;
                    z-index: 100;
                    text-shadow: 1px 1px 2px black;
                }
            </style>
        </head>
        <body>
            <div id="globe-container">
                <div id="info">Click on the globe to select a location</div>
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
                    const renderer = new THREE.WebGLRenderer({ antialias: true });
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
                    const earthMaterial = new THREE.MeshPhongMaterial({
                        map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_atmos_2048.jpg'),
                        bumpMap: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_normal_2048.jpg'),
                        bumpScale: 0.05,
                        specularMap: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_specular_2048.jpg'),
                        specular: new THREE.Color('grey'),
                        shininess: 5
                    });
                    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
                    scene.add(earth);
        
                    // Add clouds
                    const cloudGeometry = new THREE.SphereGeometry(1.01, 64, 64);
                    const cloudMaterial = new THREE.MeshPhongMaterial({
                        map: new THREE.TextureLoader().load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_clouds_1024.png'),
                        transparent: true,
                        opacity: 0.4
                    });
                    const clouds = new THREE.Mesh(cloudGeometry, cloudMaterial);
                    scene.add(clouds);
        
                    // Add stars
                    const starGeometry = new THREE.BufferGeometry();
                    const starMaterial = new THREE.PointsMaterial({
                        color: 0xffffff,
                        size: 0.05
                    });
        
                    const starVertices = [];
                    for (let i = 0; i < 10000; i++) {
                        starVertices.push(
                            (Math.random() - 0.5) * 2000,
                            (Math.random() - 0.5) * 2000,
                            (Math.random() - 0.5) * 2000
                        );
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
        
                    // Marker for selected location
                    const markerGeometry = new THREE.SphereGeometry(0.02, 16, 16);
                    const markerMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
                    const marker = new THREE.Mesh(markerGeometry, markerMaterial);
                    scene.add(marker);
                    marker.visible = false;
        
                    // Click handler
                    const raycaster = new THREE.Raycaster();
                    const mouse = new THREE.Vector2();
        
                    function onClick(event) {
                        // Calculate mouse position
                        const rect = renderer.domElement.getBoundingClientRect();
                        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
                        // Raycast
                        raycaster.setFromCamera(mouse, camera);
                        const intersects = raycaster.intersectObject(earth);
        
                        if (intersects.length > 0) {
                            const point = intersects[0].point;
                            marker.position.copy(point);
                            marker.visible = true;
        
                            // Convert to lat/lon
                            const lat = 90 - (Math.acos(point.y / point.length()) * (180 / Math.PI));
                            const lon = ((270 + (Math.atan2(point.x, point.z)) * (180 / Math.PI)) % 360 - 180);
        
                            // Send to Streamlit
                            const data = {lat: lat, lon: lon};
                            parent.window.postMessage({
                                isStreamlitMessage: true,
                                type: "globeClick",
                                data: data
                            }, "*");
                        }
                    }
        
                    renderer.domElement.addEventListener('click', onClick);
        
                    // Animation loop
                    function animate() {
                        requestAnimationFrame(animate);
                        earth.rotation.y += 0.001;
                        clouds.rotation.y += 0.0015;
                        controls.update();
                        renderer.render(scene, camera);
                    }
        
                    // Handle resize
                    function onWindowResize() {
                        camera.aspect = container.clientWidth / container.clientHeight;
                        camera.updateProjectionMatrix();
                        renderer.setSize(container.clientWidth, container.clientHeight);
                    }
        
                    window.addEventListener('resize', onWindowResize);
        
                    animate();
                </script>
            </div>
        </body>
        </html>
    """

    # Display the globe
    globe = components.html(threejs_html, height=600)


# Function to display weather information
def show_weather(lat, lon):
    try:
        # Get weather data
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract weather info
        city_name = data.get('name', 'Selected Location')
        temp_celsius = data['main']['temp'] - 273.15
        weather_main = data['weather'][0]['main']
        weather_desc = data['weather'][0]['description'].capitalize()
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        pressure = data['main']['pressure']
        icon_id = data['weather'][0]['icon']

        # Get weather icon
        icon_url = f"http://openweathermap.org/img/wn/{icon_id}@2x.png"
        icon_img = Image.open(BytesIO(requests.get(icon_url).content))

        # Display weather info
        with weather_placeholder.container():
            st.markdown(f"## {city_name}")
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.image(icon_img, width=100)
            with col_b:
                st.markdown(f"**{weather_main}**")
                st.caption(weather_desc)

            st.metric("Temperature", f"{temp_celsius:.1f} °C")
            st.metric("Humidity", f"{humidity}%")
            st.metric("Wind Speed", f"{wind_speed} m/s")
            st.metric("Pressure", f"{pressure} hPa")
            st.caption(f"Coordinates: {lat:.2f}° N, {lon:.2f}° E")

    except Exception as e:
        weather_placeholder.error(f"Error fetching weather data: {str(e)}")


# JavaScript to Python communication
components.html(
    """
    <script>
    window.addEventListener('message', function(event) {
        if (event.data.isStreamlitMessage && event.data.type === "globeClick") {
            const data = event.data.data;
            window.parent.postMessage({
                isStreamlitMessage: true,
                type: "streamlit",
                data: data
            }, "*");
        }
    });
    </script>
    """,
    height=0
)

# Handle messages from the iframe
if 'globe_data' not in st.session_state:
    st.session_state.globe_data = None


def handle_message(msg):
    if msg.get('isStreamlitMessage') and msg.get('type') == "streamlit":
        st.session_state.globe_data = msg['data']
        show_weather(msg['data']['lat'], msg['data']['lon'])


try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx

    ctx = get_script_run_ctx()
    if ctx and hasattr(ctx, 'request') and hasattr(ctx.request, '_request_data'):
        msg = ctx.request._request_data.get('globeClick')
        if msg:
            handle_message(msg)
except:
    pass