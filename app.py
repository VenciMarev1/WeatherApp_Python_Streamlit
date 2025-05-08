import streamlit as st
import requests
import matplotlib.pyplot as plt

# Set up Streamlit page
st.set_page_config(page_title="Weather Prognosis", layout="centered")
st.title("🌤️ Live Weather Prognosis")

# Input for city and API key
city = st.text_input("Enter a city name:", "London")
api_key = st.text_input("Enter your OpenWeatherMap API key:", type="password")

if city and api_key:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract weather details
        city_name = data['name']
        temp_celsius = data['main']['temp'] - 273.15
        weather_description = data['weather'][0]['description'].capitalize()
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        pressure = data['main']['pressure']
        cloudiness = data['clouds']['all']

        # Display results
        st.subheader(f"Weather in {city_name}")
        weather_data = [
            ["Temperature (°C)", f"{temp_celsius:.2f}"],
            ["Weather", weather_description],
            ["Humidity (%)", humidity],
            ["Wind Speed (m/s)", wind_speed],
            ["Pressure (hPa)", pressure],
            ["Cloudiness (%)", cloudiness]
        ]

        # Plot table using matplotlib
        fig, ax = plt.subplots()
        ax.axis('off')
        table = ax.table(cellText=weather_data, colLabels=["Parameter", "Value"],
                         cellLoc='left', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.2)
        st.pyplot(fig)

    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
    except (KeyError, ValueError) as e:
        st.error(f"Error processing data: {e}")