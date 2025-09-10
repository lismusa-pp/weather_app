import requests
from config import API_KEY, BASE_WEATHER

city = "London,UK"
params = {
    "q": city,
    "appid": API_KEY,
    "units": "metric"
}

try:
    response = requests.get(BASE_WEATHER, params=params, timeout=10)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", e)
