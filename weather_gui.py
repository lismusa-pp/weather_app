import threading
import io
from datetime import datetime

import requests
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk, messagebox

from api_client import geocode_city, get_current_weather, get_forecast
from config import ICON_URL, API_KEY


def start_gui():
    root = tk.Tk()
    root.title("Weather App — Python")
    root.geometry("520x440")
    frm = ttk.Frame(root, padding=12)
    frm.pack(fill="both", expand=True)

    # --- Inputs ---
    ttk.Label(frm, text="City:").grid(column=0, row=0, sticky="w")
    city_entry = ttk.Entry(frm, width=30)
    city_entry.grid(column=1, row=0, sticky="w")
    city_entry.insert(0, "London")

    units_var = tk.StringVar(value="metric")
    ttk.Radiobutton(frm, text="Celsius", variable=units_var, value="metric").grid(column=0, row=1, sticky="w")
    ttk.Radiobutton(frm, text="Fahrenheit", variable=units_var, value="imperial").grid(column=1, row=1, sticky="w")
    ttk.Radiobutton(frm, text="Kelvin", variable=units_var, value="standard").grid(column=2, row=1, sticky="w")

    # --- Results frame ---
    result_frame = ttk.LabelFrame(frm, text="Result", padding=8)
    result_frame.grid(column=0, row=3, columnspan=3, pady=12, sticky="nsew")
    result_frame.columnconfigure(1, weight=1)

    icon_label = ttk.Label(result_frame)
    icon_label.grid(column=0, row=0, rowspan=4, padx=(0, 12))

    title_lbl = ttk.Label(result_frame, text="—", font=(None, 14, "bold"))
    title_lbl.grid(column=1, row=0, sticky="w")

    desc_lbl = ttk.Label(result_frame, text="—")
    desc_lbl.grid(column=1, row=1, sticky="w")

    temp_lbl = ttk.Label(result_frame, text="—", font=(None, 12))
    temp_lbl.grid(column=1, row=2, sticky="w")

    extra_lbl = ttk.Label(result_frame, text="—")
    extra_lbl.grid(column=1, row=3, sticky="w")

    status_lbl = ttk.Label(frm, text="Ready")
    status_lbl.grid(column=0, row=5, columnspan=3, sticky="w", pady=(8, 0))

    # --- Helpers ---
    def show_error(msg):
        messagebox.showerror("Error", msg)
        status_lbl.config(text=f"Error: {msg}")

    def fetch_and_show(city, units):
        if API_KEY == "YOUR_API_KEY_HERE" or not API_KEY:
            show_error("API key not set. See README or set OWM_API_KEY environment variable.")
            return

        try:
            status_lbl.config(text="Fetching...")
            lat, lon, location = geocode_city(city)
            current = get_current_weather(lat, lon, units=units)
            forecast = get_forecast(lat, lon, units=units)

            # Basic info
            weather = current.get("weather", [{}])[0]
            main = current.get("main", {})

            title_lbl.config(text=location)
            desc_lbl.config(text=f"{weather.get('main','')} — {weather.get('description','').capitalize()}")
            temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
            temp_lbl.config(text=f"{main.get('temp')} {temp_unit} (feels {main.get('feels_like')}{temp_unit})")
            extra_lbl.config(text=f"Humidity {main.get('humidity')}%  Pressure {main.get('pressure')} hPa")

            # Fetch and show icon (if available)
            icon = weather.get("icon")
            if icon:
                try:
                    img_data = requests.get(ICON_URL.format(icon), timeout=6).content
                    pil = Image.open(io.BytesIO(img_data))
                    # resize for consistent display
                    pil = pil.resize((80, 80), Image.ANTIALIAS)
                    imgtk = ImageTk.PhotoImage(pil)
                    icon_label.configure(image=imgtk)
                    icon_label.image = imgtk  # keep reference
                except Exception:
                    icon_label.configure(image="")
                    icon_label.image = None

            status_lbl.config(text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            show_error(str(e))

    # --- Events ---
    def on_search():
        city = city_entry.get().strip()
        if not city:
            show_error("Please enter a city name")
            return
        units = units_var.get()
        # Run network calls in a worker thread to keep UI responsive
        threading.Thread(target=fetch_and_show, args=(city, units), daemon=True).start()

    search_btn = ttk.Button(frm, text="Search", command=on_search)
    search_btn.grid(column=2, row=0, sticky="w")

    # Enter key triggers search
    root.bind("<Return>", lambda e: on_search())

    root.mainloop()


if __name__ == "__main__":
    start_gui()
