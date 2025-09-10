import os


API_KEY = os.getenv("OWM_API_KEY") or "21ba1d0ec910a8f415c466c05f21f6f3"

# Base URLs
BASE_GEOCODE = "http://api.openweathermap.org/geo/1.0/direct"
BASE_WEATHER = "https://api.openweathermap.org/data/2.5/weather"
BASE_ONECALL = "https://api.openweathermap.org/data/2.5/onecall"
ICON_URL = "https://openweathermap.org/img/wn/{}@2x.png"
