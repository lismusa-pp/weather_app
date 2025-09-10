from datetime import datetime

def format_weather_cli(current, forecast=None, units="metric"):
    lines = []
    name = current.get("name") or "unknown"
    weather = current.get("weather", [{}])[0]
    main = current.get("main", {})
    temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"

    lines.append(f"Weather for {name}")
    lines.append(f"{weather.get('main', '')} - {weather.get('description', '').capitalize()}")
    lines.append(f"Temperature: {main.get('temp')} {temp_unit} (feels like {main.get('feels_like')}{temp_unit})")
    lines.append(f"Humidity: {main.get('humidity')}% | Pressure: {main.get('pressure')} hPa")
    wind = current.get("wind", {})
    lines.append(f"Wind: {wind.get('speed')} m/s, deg {wind.get('deg')}")

    if forecast:
        lines.append("\n3-day forecast:")
        daily = forecast.get("daily", [])[:3]
        for d in daily:
            dt = datetime.utcfromtimestamp(d.get("dt")).strftime("%Y-%m-%d")
            desc = d.get("weather", [{}])[0].get("description", "")
            lo = d.get("temp", {}).get("min")
            hi = d.get("temp", {}).get("max")
            lines.append(f"{dt}: {desc.capitalize()} — {lo}{temp_unit} / {hi}{temp_unit}")

    return "\n".join(lines)
