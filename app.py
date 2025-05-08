import streamlit as st
import requests
from PIL import Image
from io import BytesIO

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
        st.image("https://media.giphy.com/media/3oEjI6SIIHBdRxXI40/giphy.gif", use_container_width=True)

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
    except (KeyError, ValueError) as e:
        st.error(f"Error processing data: {e}")