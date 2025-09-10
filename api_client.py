import requests
from config import API_KEY, BASE_WEATHER, BASE_GEOCODE, BASE_ONECALL

def geocode_city(city):
    """Return lat, lon, formatted name"""
    params = {"q": city, "limit": 1, "appid": API_KEY}
    resp = requests.get(BASE_GEOCODE, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError("City not found")
    return data[0]["lat"], data[0]["lon"], f"{data[0]['name']}, {data[0]['country']}"

def get_current_weather(lat, lon, units="metric"):
    """Return current weather JSON"""
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": units}
    resp = requests.get(BASE_WEATHER, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_forecast(lat, lon, units="metric"):
    """Return 7-day forecast JSON"""
    params = {"lat": lat, "lon": lon, "exclude":"minutely,hourly,alerts", "appid": API_KEY, "units": units}
    resp = requests.get(BASE_ONECALL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()
