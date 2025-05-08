import requests
import streamlit as st

API_KEY = "5dc93fe1be4655d1693091ba3dc6c853"  # Replace with your OpenWeatherMap API key
CITY = "Plovdiv"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"

try:
    response = requests.get(URL)
    response.raise_for_status()
    data = response.json()

    city_name = st.text_input("Enter City Name")
    temp_kelvin = data['main']['temp']
    temp_celsius = temp_kelvin - 273.15


    st.title("Weather App")
    st.text(f"City: {city_name}")
    st.text(f"Temperature: {temp_celsius:.2f}°C")

    print(f"\nCity: {city_name}")
    print(f"Temperature: {temp_celsius:.2f}°C")



except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except (KeyError, ValueError) as e:
    print(f"Error processing data: {e}")
