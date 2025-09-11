import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from api_client import geocode_city, get_current_weather

def start_gui():
    root = tk.Tk()
    root.title("Weather App")
    root.configure(bg="#1e3c72")
    root.state("zoomed")  # Start maximized
    root.resizable(True, True)

    # Fullscreen toggle
    fullscreen = [False]
    def toggle_fullscreen(event=None):
        fullscreen[0] = not fullscreen[0]
        root.attributes("-fullscreen", fullscreen[0])
    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

    # -------- Canvas for Gradient --------
    canvas = tk.Canvas(root, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    def draw_gradient(offset=0):
        canvas.delete("gradient")
        is_day = 6 <= datetime.now().hour <= 18
        color1 = "#74b9ff" if is_day else "#0f2027"
        color2 = "#a29bfe" if is_day else "#2c5364"
        for i in range(height):
            r1, g1, b1 = root.winfo_rgb(color1)
            r2, g2, b2 = root.winfo_rgb(color2)
            r = int(r1 + (r2 - r1) * (i+offset) / height) >> 8
            g = int(g1 + (g2 - g1) * (i+offset) / height) >> 8
            b = int(b1 + (b2 - b1) * (i+offset) / height) >> 8
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, width, i, tags=("gradient",), fill=hex_color)
        root.after(100, lambda: draw_gradient((offset+1)%height))  # animate gradient

    draw_gradient()

    # -------- Toolbar --------
    toolbar = tk.Frame(root, bg="#1e3c72")
    canvas.create_window(width//2, 80, window=toolbar)

    city_entry = tk.Entry(toolbar, font=("Helvetica", 14), width=25, relief="flat", bd=0)
    city_entry.grid(row=0, column=0, padx=5, ipady=5)
    city_entry.insert(0, "London")
    city_entry.configure(highlightthickness=2, highlightbackground="white", highlightcolor="#74b9ff")

    def style_btn(btn, bg="#2c3e50", fg="white"):
        btn.config(
            font=("Helvetica", 12, "bold"),
            bg=bg,
            fg=fg,
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2"
        )
        btn.bind("<Enter>", lambda e: btn.config(bg="#1e3c72"))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    search_btn = tk.Button(toolbar, text="🔍 Search")
    style_btn(search_btn)
    search_btn.grid(row=0, column=1, padx=5)

    loc_btn = tk.Button(toolbar, text="🌍 My Location")
    style_btn(loc_btn, bg="#34495e")
    loc_btn.grid(row=0, column=2, padx=5)

    refresh_btn = tk.Button(toolbar, text="🔄 Refresh")
    style_btn(refresh_btn, bg="#34495e")
    refresh_btn.grid(row=0, column=3, padx=5)

    # -------- Main Weather Section --------
    temp_label = tk.Label(root, text="--°", font=("Helvetica", 80, "bold"),
                          fg="white", bg="#1e3c72")
    canvas.create_window(width//2, height//4, window=temp_label)

    condition_label = tk.Label(root, text="", font=("Helvetica", 22),
                               fg="white", bg="#1e3c72")
    canvas.create_window(width//2, height//4 + 80, window=condition_label)

    datetime_label = tk.Label(root, text="", font=("Helvetica", 14),
                              fg="white", bg="#1e3c72")
    canvas.create_window(width//2, height//4 + 120, window=datetime_label)

    # -------- Bottom Forecast Panel --------
    panel = tk.Frame(root, bg="#ffffff", bd=0, relief="flat")
    canvas.create_window(width//2, height*0.7, window=panel, width=width*0.85, height=height*0.35)

    # Current details
    result_label = tk.Label(panel, text="", font=("Helvetica", 14),
                            bg="white", fg="#2c3e50", justify="left")
    result_label.pack(pady=10)

    # Mini forecast slots
    forecast_frame = tk.Frame(panel, bg="white")
    forecast_frame.pack(pady=10)

    forecast_labels = []
    for i in range(4):
        lbl = tk.Label(forecast_frame, text="--°\n--:--", font=("Helvetica", 12),
                       bg="#ecf0f1", fg="#2c3e50", width=15, height=6, relief="ridge", bd=2)
        lbl.grid(row=0, column=i, padx=10)
        # Hover animation for forecast cards
        lbl.bind("<Enter>", lambda e, l=lbl: l.config(bg="#dcdde1"))
        lbl.bind("<Leave>", lambda e, l=lbl: l.config(bg="#ecf0f1"))
        forecast_labels.append(lbl)

    # -------- Fetch Weather --------
    def fetch_weather(city=None):
        try:
            now = datetime.now()
            datetime_label.config(text=now.strftime("%A, %d %B %Y | %H:%M"))

            if not city:
                city = city_entry.get()
            if not city:
                messagebox.showerror("Error", "Enter a city name")
                return

            # Animation: fade-out previous text
            temp_label.config(text="--°", fg="#bdc3c7")
            condition_label.config(text="Loading...", fg="#bdc3c7")

            lat, lon, name = geocode_city(city)
            weather = get_current_weather(lat, lon)

            desc = weather["weather"][0]["description"].title()
            temp = round(weather["main"]["temp"])
            feels_like = round(weather["main"]["feels_like"])
            humidity = weather["main"]["humidity"]
            pressure = weather["main"]["pressure"]
            wind_speed = weather["wind"]["speed"]

            # Animation: fade-in new temperature
            def animate_text(label, text, steps=10, delay=50):
                def step(i=0):
                    if i > steps:
                        return
                    intensity = int(255 * i / steps)
                    color = f"#{intensity:02x}{intensity:02x}{intensity:02x}"
                    label.config(text=text, fg=color)
                    label.after(delay, lambda: step(i+1))
                step()
            animate_text(temp_label, f"{temp}°")
            animate_text(condition_label, desc)

            result_label.config(
                text=f"📍 {name}\n\n"
                     f"🌡️ Feels like: {feels_like}°C\n"
                     f"💧 Humidity: {humidity}%\n"
                     f"📊 Pressure: {pressure} hPa\n"
                     f"💨 Wind: {wind_speed} m/s"
            )

            # Mini forecast placeholders
            for i, lbl in enumerate(forecast_labels):
                lbl.config(text=f"{temp+i}°\n{(now.hour+i)%24}:00")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            condition_label.config(text="❌ Error")

    # Button actions
    search_btn.config(command=lambda: fetch_weather())
    refresh_btn.config(command=lambda: fetch_weather(city_entry.get()))
    loc_btn.config(command=lambda: fetch_weather("New York"))

    city_entry.bind("<Return>", lambda e: fetch_weather())

    fetch_weather("London")  # Initial load

    root.mainloop()


if __name__ == "__main__":
    start_gui()
