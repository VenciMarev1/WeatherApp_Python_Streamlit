import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Weather Dashboard 🌦️", layout="wide")
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: 600;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

threejs_html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>3D Earth Globe</title>
    <style>
      body { margin: 0; overflow: hidden; }
      canvas { display: block; }
    </style>
  </head>
  <body>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      document.body.appendChild(renderer.domElement);

      const geometry = new THREE.SphereGeometry(1, 64, 64);
      const texture = new THREE.TextureLoader().load('https://raw.githubusercontent.com/ajaytripathi2000/3D-Earth-Model-Using-Three.js/main/earthmap1k.jpg');
      const bumpMap = new THREE.TextureLoader().load('https://raw.githubusercontent.com/ajaytripathi2000/3D-Earth-Model-Using-Three.js/main/earthbump1k.jpg');
      const material = new THREE.MeshPhongMaterial({
        map: texture,
        bumpMap: bumpMap,
        bumpScale: 0.05
      });
      const sphere = new THREE.Mesh(geometry, material);
      scene.add(sphere);

      const light = new THREE.PointLight(0xffffff, 1);
      light.position.set(5, 3, 5);
      scene.add(light);

      camera.position.z = 3;

      function animate() {
        requestAnimationFrame(animate);
        sphere.rotation.y += 0.002;
        renderer.render(scene, camera);
      }

      animate();

      window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      });
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