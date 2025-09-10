import argparse
from api_client import geocode_city, get_current_weather, get_forecast
from weather_cli import format_weather_cli
from weather_gui import start_gui
from config import API_KEY

def main():
    parser = argparse.ArgumentParser(description="Weather app using OpenWeatherMap")
    parser.add_argument("--city", help="City name (quotes if contains spaces)")
    parser.add_argument("--units", choices=["metric", "imperial", "standard"], default="metric")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode and print weather")
    args = parser.parse_args()

    if API_KEY == "YOUR_API_KEY_HERE":
        print("Warning: API key not set. Set environment variable OWM_API_KEY or edit config.py")

    if args.cli and args.city:
        try:
            lat, lon, _ = geocode_city(args.city)
            current = get_current_weather(lat, lon, units=args.units)
            forecast = get_forecast(lat, lon, units=args.units)
            print(format_weather_cli(current, forecast, units=args.units))
        except Exception as e:
            print("Error:", e)
        return

    # Default: GUI
    start_gui()

if __name__ == "__main__":
    main()
