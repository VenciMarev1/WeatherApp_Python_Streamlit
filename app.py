import requests
import pandas as pd
import streamlit as st
from datetime import datetime

API_KEY = "5dc93fe1be4655d1693091ba3dc6c853"
CITY = "Plovdiv"
URL = f"http://api.openweathermap.org/data/2.5/forecast?id=524901&appid={API_KEY}"

response = requests.get(URL)
data = response.json()
def get_weather_data():
    response = requests.get(URL)
    data = response.json()
    weather = []

    for entry in data["list"]:
        date = datetime.fromtimestamp(entry["dt"]).date()
        temp = entry["main"]["temp"]
        rain = entry.get("rain", {}).get("3h", 0)
        humidity = entry["main"]["humidity"]
        weather.append({
            "date": date,
            "temp": temp,
            "rain": rain,
            "humidity": humidity
        })

    df = pd.DataFrame(weather)
    df = df.groupby("date").agg({
        "temp": "mean",
        "rain": "sum",
        "humidity": "mean"
    })
    return df

NORMALS = {
    "April": {"temp": 14, "rain_days": 7},
    "May": {"temp": 18, "rain_days": 9}
}

'''
if  > NORMALS["April"]["temp"] + 2:
    st.warning("⚠️ Температурите са необичайно високи!")
else:
    st.success("✅ Температурите са в норма.")
'''

print(data)