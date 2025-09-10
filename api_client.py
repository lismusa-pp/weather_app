import time, requests
from datetime import datetime
from cache_manager import cache_get, cache_set
from config import API_KEY, BASE_GEOCODE, BASE_WEATHER, BASE_ONECALL

def fetch_json(url, params, retries=2, backoff=0.5):
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, params=params, timeout=8)
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            if attempt == retries:
                raise
            time.sleep(backoff * (2 ** attempt))

def geocode_city(city_name, limit=1):
    cache_key = f"geocode:{city_name.lower()}"
    cached = cache_get(cache_key, max_age_seconds=24 * 3600)
    if cached: return cached

    params = {"q": city_name, "limit": limit, "appid": API_KEY}
    data = fetch_json(BASE_GEOCODE, params)
    if not data: raise ValueError("City not found")

    entry = data[0]
    result = (entry["lat"], entry["lon"], f"{entry.get('name')}, {entry.get('country')}")
    cache_set(cache_key, result)
    return result

def get_current_weather(lat, lon, units="metric"):
    cache_key = f"current:{lat}:{lon}:{units}"
    cached = cache_get(cache_key, max_age_seconds=120)
    if cached: return cached

    params = {"lat": lat, "lon": lon, "units": units, "appid": API_KEY}
    data = fetch_json(BASE_WEATHER, params)
    cache_set(cache_key, data)
    return data

def get_forecast(lat, lon, units="metric", exclude="minutely,hourly,alerts"):
    cache_key = f"forecast:{lat}:{lon}:{units}"
    cached = cache_get(cache_key, max_age_seconds=600)
    if cached: return cached

    params = {"lat": lat, "lon": lon, "exclude": exclude, "units": units, "appid": API_KEY}
    data = fetch_json(BASE_ONECALL, params)
    cache_set(cache_key, data)
    return data
