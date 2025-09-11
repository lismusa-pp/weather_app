import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
import os
import random
from api_client import geocode_city, get_current_weather

ICON_PATH = "icons"

def load_icon(name, size=(100,100)):
    path = os.path.join(ICON_PATH, name)
    img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

def start_gui():
    root = tk.Tk()
    root.title("Weather App")
    root.state("zoomed")
    root.configure(bg="#1e3c72")
    root.resizable(True, True)

    fullscreen = [False]
    root.bind("<F11>", lambda e: root.attributes("-fullscreen", not root.attributes("-fullscreen")))
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    canvas = tk.Canvas(root, highlightthickness=0, width=width, height=height)
    canvas.pack(fill="both", expand=True)

    current_gradient = ["#74b9ff", "#a29bfe"]

    # ------------------- Animated Gradient -------------------
    def draw_gradient(offset=0):
        canvas.delete("gradient")
        for i in range(height):
            r1,g1,b1=root.winfo_rgb(current_gradient[0])
            r2,g2,b2=root.winfo_rgb(current_gradient[1])
            r=int(r1+(r2-r1)*(i+offset)/height)>>8
            g=int(g1+(g2-g1)*(i+offset)/height)>>8
            b=int(b1+(b2-b1)*(i+offset)/height)>>8
            canvas.create_line(0,i,width,i,tags=("gradient",),fill=f"#{r:02x}{g:02x}{b:02x}")
        root.after(100, lambda: draw_gradient((offset+1)%height))
    draw_gradient()

    # ------------------- Particles -------------------
    particles = []
    stars = []

    def create_particles(n=30):
        for _ in range(n):
            x=random.randint(0,width)
            y=random.randint(0,height)
            size=random.randint(2,5)
            p=canvas.create_oval(x,y,x+size,y+size,fill="white",outline="",tags="particle")
            particles.append((p, random.uniform(0.3,1.2)))

    def move_particles():
        for i, (p, speed) in enumerate(particles):
            canvas.move(p, 0, -speed)
            x1,y1,x2,y2=canvas.coords(p)
            if y2<0:
                canvas.move(p,0,height+10)
        root.after(50, move_particles)

    def create_stars(n=50):
        for _ in range(n):
            x=random.randint(0,width)
            y=random.randint(0,height//2)
            size=random.randint(1,2)
            s=canvas.create_oval(x,y,x+size,y+size,fill="white",outline="",tags="star")
            stars.append((s, random.choice([0.05,0.1,0.15,0.2])))

    def twinkle_stars():
        for s, speed in stars:
            c=canvas.itemcget(s,"fill")
            # Randomly fade
            if random.random()<0.05:
                new_color="white" if c=="#000000" else "#000000"
                canvas.itemconfig(s,fill=new_color)
        root.after(300, twinkle_stars)

    create_particles()
    move_particles()
    create_stars()
    twinkle_stars()

    # ------------------- Toolbar -------------------
    toolbar = tk.Frame(root, bg="#1e3c72")
    canvas.create_window(width//2, 80, window=toolbar)
    city_entry = tk.Entry(toolbar, font=("Helvetica",14), width=25, relief="flat", bd=0)
    city_entry.grid(row=0,column=0,padx=5,ipady=5)
    city_entry.insert(0,"London")
    city_entry.configure(highlightthickness=2, highlightbackground="white", highlightcolor="#74b9ff")

    def style_btn(btn,bg="#2c3e50",fg="white"):
        btn.config(font=("Helvetica",12,"bold"), bg=bg, fg=fg, relief="flat", bd=0, padx=18, pady=10, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg="#1e3c72"))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    search_btn = tk.Button(toolbar,text="🔍 Search"); style_btn(search_btn); search_btn.grid(row=0,column=1,padx=5)
    loc_btn = tk.Button(toolbar,text="🌍 My Location"); style_btn(loc_btn,bg="#34495e"); loc_btn.grid(row=0,column=2,padx=5)
    refresh_btn = tk.Button(toolbar,text="🔄 Refresh"); style_btn(refresh_btn,bg="#34495e"); refresh_btn.grid(row=0,column=3,padx=5)

    # ------------------- Main labels -------------------
    temp_label = tk.Label(root,text="--°",font=("Helvetica",80,"bold"), fg="white", bg="#1e3c72")
    canvas.create_window(width//2,height//4,window=temp_label)
    condition_label = tk.Label(root,text="",font=("Helvetica",22), fg="white", bg="#1e3c72")
    canvas.create_window(width//2,height//4+80,window=condition_label)
    datetime_label = tk.Label(root,text="",font=("Helvetica",14), fg="white", bg="#1e3c72")
    canvas.create_window(width//2,height//4+120,window=datetime_label)

    icon_label = tk.Label(root,bg="#1e3c72")
    canvas.create_window(width//2,height//4-80,window=icon_label)

    # ------------------- Forecast panel -------------------
    panel = tk.Frame(root,bg="#ffffff",bd=0,relief="flat")
    canvas.create_window(width//2,height*0.7,window=panel,width=width*0.85,height=height*0.35)
    result_label = tk.Label(panel,text="",font=("Helvetica",14), bg="white", fg="#2c3e50", justify="left")
    result_label.pack(pady=10)
    forecast_frame = tk.Frame(panel,bg="white")
    forecast_frame.pack(pady=10)
    forecast_labels = []
    for i in range(4):
        lbl = tk.Label(forecast_frame,text="--°\n--:--", font=("Helvetica",12), bg="#ecf0f1", fg="#2c3e50", width=15, height=6, relief="ridge", bd=2)
        lbl.grid(row=0,column=i,padx=10)
        forecast_labels.append(lbl)

    # ------------------- Weather Effects -------------------
    cloud_items = []
    rain_items = []

    def create_clouds(n=5):
        for _ in range(n):
            x=random.randint(0,width); y=random.randint(50,height//2)
            c=canvas.create_oval(x,y,x+100,y+50,fill="#ecf0f1",outline="")
            cloud_items.append(c)
    def move_clouds():
        for c in cloud_items:
            canvas.move(c,1,0)
            x,y,_,_=canvas.coords(c)
            if x>width: canvas.move(c,-width-100,0)
        root.after(50, move_clouds)

    def create_rain(n=50):
        for _ in range(n):
            x=random.randint(0,width); y=random.randint(0,height//2)
            r=canvas.create_line(x,y,x,y+10,fill="#3498db",width=2)
            rain_items.append(r)
    def move_rain():
        for r in rain_items:
            canvas.move(r,0,10)
            x,y,_,_=canvas.coords(r)
            if y>height: canvas.move(r,0,-height)
        root.after(50, move_rain)

    def clear_effects():
        for c in cloud_items: canvas.delete(c)
        for r in rain_items: canvas.delete(r)
        cloud_items.clear(); rain_items.clear()

    # ------------------- Fetch Weather -------------------
    def fetch_weather(city=None):
        try:
            now=datetime.now()
            datetime_label.config(text=now.strftime("%A, %d %B %Y | %H:%M"))
            if not city: city=city_entry.get()
            if not city: messagebox.showerror("Error","Enter a city name"); return

            temp_label.config(text="--°", fg="#bdc3c7")
            condition_label.config(text="Loading...", fg="#bdc3c7")

            lat, lon, name=geocode_city(city)
            weather=get_current_weather(lat,lon)
            desc=weather["weather"][0]["description"].title()
            temp=round(weather["main"]["temp"]); feels_like=round(weather["main"]["feels_like"])
            humidity=weather["main"]["humidity"]; pressure=weather["main"]["pressure"]; wind_speed=weather["wind"]["speed"]
            main_weather=weather["weather"][0]["main"].lower()

            # Weather icon
            icon_file="sun.png"
            clear_effects()
            if "cloud" in main_weather: icon_file="cloud.png"; create_clouds(); move_clouds()
            elif "rain" in main_weather: icon_file="rain.png"; create_rain(); move_rain()
            elif "snow" in main_weather: icon_file="snow.png"

            icon_img=load_icon(icon_file)
            icon_label.config(image=icon_img)
            icon_label.image=icon_img

            temp_label.config(text=f"{temp}°", fg="white")
            condition_label.config(text=desc, fg="white")
            result_label.config(
                text=f"📍 {name}\n\n🌡️ Feels like: {feels_like}°C\n💧 Humidity: {humidity}%\n📊 Pressure: {pressure} hPa\n💨 Wind: {wind_speed} m/s"
            )

            for i,lbl in enumerate(forecast_labels):
                lbl.config(text=f"{temp+i}°\n{(now.hour+i)%24}:00")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            condition_label.config(text="❌ Error")

    search_btn.config(command=lambda: fetch_weather())
    refresh_btn.config(command=lambda: fetch_weather(city_entry.get()))
    loc_btn.config(command=lambda: fetch_weather("New York"))
    city_entry.bind("<Return>", lambda e: fetch_weather())
    fetch_weather("London")

    root.mainloop()

if __name__=="__main__":
    start_gui()
