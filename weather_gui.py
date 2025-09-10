import tkinter as tk
from tkinter import messagebox
from api_client import geocode_city, get_current_weather

def start_gui():
    root = tk.Tk()
    root.title("Weather App")
    root.geometry("400x300")

    tk.Label(root, text="City:").pack()
    city_entry = tk.Entry(root)
    city_entry.pack()
    city_entry.insert(0, "London")

    result_label = tk.Label(root, text="", justify="left")
    result_label.pack(pady=20)

    def fetch_weather():
        city = city_entry.get()
        if not city:
            messagebox.showerror("Error", "Enter a city name")
            return
        try:
            lat, lon, name = geocode_city(city)
            weather = get_current_weather(lat, lon)
            desc = weather["weather"][0]["description"]
            temp = weather["main"]["temp"]
            result_label.config(text=f"{name}\n{desc}\nTemperature: {temp}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(root, text="Search", command=fetch_weather).pack()
    root.mainloop()

if __name__ == "__main__":
    start_gui()
