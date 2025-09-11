import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
import os, random
from api_client import geocode_city, get_current_weather

# -------------------- Paths --------------------
ICON_PATH = "icons"
BG_PATH = "background.jpg"  # your high-res background

def load_icon(name, size=(100,100)):
    path = os.path.join(ICON_PATH, name)
    img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
    return img

def start_gui():
    root = tk.Tk()
    root.title("Weather App")
    root.state("zoomed")
    root.resizable(True, True)

    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # ------------------- Background Image -------------------
    bg_orig_full = Image.open(BG_PATH)
    bg_w, bg_h = bg_orig_full.size
    screen_ratio = width / height
    img_ratio = bg_w / bg_h
    if img_ratio > screen_ratio:
        new_height = height
        new_width = int(bg_w * (height / bg_h))
    else:
        new_width = width
        new_height = int(bg_h * (width / bg_w))
    bg_img_orig = bg_orig_full.resize((new_width, new_height), Image.Resampling.LANCZOS)
    left = (new_width - width) // 2
    top = (new_height - height) // 2
    bg_img_orig = bg_img_orig.crop((left, top, left + width, top + height))
    bg_img = ImageTk.PhotoImage(bg_img_orig)
    canvas_bg = canvas.create_image(0, 0, anchor="nw", image=bg_img)
    canvas.bg_img = bg_img

    # ------------------- Gradient Overlay -------------------
    gradient_schedule = [
        (6, 9, "#FFA500", "#FFD580"),
        (9, 18, "#74b9ff", "#a29bfe"),
        (18, 20, "#FF7F50", "#2c3e50"),
        (20, 6, "#0f2027", "#2c5364")
    ]
    def get_current_gradient():
        now_hour = datetime.now().hour
        for start, end, top, bottom in gradient_schedule:
            if start < end:
                if start <= now_hour < end: return top, bottom
            else:
                if now_hour >= start or now_hour < end: return top, bottom
        return "#74b9ff", "#a29bfe"

    def draw_gradient_smooth():
        canvas.delete("gradient")
        top_color, bottom_color = get_current_gradient()
        for i in range(height):
            r1,g1,b1=root.winfo_rgb(top_color)
            r2,g2,b2=root.winfo_rgb(bottom_color)
            r=int(r1 + (r2 - r1) * i / height) >> 8
            g=int(g1 + (g2 - g1) * i / height) >> 8
            b=int(b1 + (b2 - b1) * i / height) >> 8
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(0, i, width, i, tags="gradient", fill=hex_color)
        canvas.tag_lower("gradient", canvas_bg)
        root.after(1000, draw_gradient_smooth)
    draw_gradient_smooth()

    # ------------------- Toolbar -------------------
    toolbar = tk.Frame(root, bg="#1e3c72")
    canvas.create_window(width//2, 80, window=toolbar)
    city_entry = tk.Entry(toolbar,font=("Helvetica",14),width=25,relief="flat",bd=0)
    city_entry.grid(row=0,column=0,padx=5,ipady=5); city_entry.insert(0,"London")
    city_entry.configure(highlightthickness=2,highlightbackground="white",highlightcolor="#74b9ff")

    def style_btn(btn,bg="#2c3e50",fg="white"):
        btn.config(font=("Helvetica",12,"bold"), bg=bg, fg=fg, relief="flat", bd=0, padx=18, pady=10, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg="#1e3c72"))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    search_btn = tk.Button(toolbar,text="🔍 Search"); style_btn(search_btn); search_btn.grid(row=0,column=1,padx=5)
    loc_btn = tk.Button(toolbar,text="🌍 My Location"); style_btn(loc_btn,bg="#34495e"); loc_btn.grid(row=0,column=2,padx=5)
    refresh_btn = tk.Button(toolbar,text="🔄 Refresh"); style_btn(refresh_btn,bg="#34495e"); refresh_btn.grid(row=0,column=3,padx=5)

    # ------------------- Main Weather Labels -------------------
    temp_label = tk.Label(root,text="--°",font=("Helvetica",80,"bold"), fg="white", bg="#1e3c72")
    canvas.create_window(width//2,height//4,window=temp_label)
    condition_label = tk.Label(root,text="",font=("Helvetica",22), fg="white", bg="#1e3c72")
    canvas.create_window(width//2,height//4+80,window=condition_label)
    datetime_label = tk.Label(root,text="",font=("Helvetica",14), fg="white", bg="#1e3c72")
    canvas.create_window(width//2,height//4+120,window=datetime_label)

    icon_label = tk.Label(root,bg="#1e3c72")
    canvas.create_window(width//2,height//4-80,window=icon_label)
    sun_img_orig = load_icon("sun.png",(120,120))
    sun_angle = 0
    def rotate_sun():
        nonlocal sun_angle
        sun_angle = (sun_angle+2)%360
        rotated = sun_img_orig.rotate(sun_angle,resample=Image.Resampling.BICUBIC)
        icon_label.image = ImageTk.PhotoImage(rotated)
        icon_label.config(image=icon_label.image)
        root.after(50, rotate_sun)

    # ------------------- Modern Rounded Bottom Panel -------------------
    panel_width = int(width*0.7)
    panel_height = int(height*0.4)
    panel_x = width//2 - panel_width//2
    panel_y = int(height*0.55)
    panel_radius = 25

    shadow = canvas.create_rectangle(panel_x+5, panel_y+5, panel_x+panel_width+5, panel_y+panel_height+5,
                                     fill="#dcdcdc", outline="", width=0)
    def create_rounded_panel(x, y, w, h, r, color):
        points = [
            x+r, y, x+w-r, y, x+w, y, x+w, y+r,
            x+w, y+h-r, x+w, y+h, x+w-r, y+h, x+r, y+h,
            x, y+h, x, y+h-r, x, y+r, x, y
        ]
        return canvas.create_polygon(points, smooth=True, fill=color, outline="")

    panel_bg = create_rounded_panel(panel_x, panel_y, panel_width, panel_height, panel_radius, "#ffffff")

    # ------------------- Panel Content -------------------
    content_pad = 30
    current_y = panel_y + content_pad

    # Location
    location_label = tk.Label(root, text="", font=("Helvetica", 18, "bold"), bg="#ffffff", fg="#2c3e50")
    canvas.create_window(width//2, current_y, window=location_label)
    current_y += 50

    # Temperature + Condition
    temp_cond_frame = tk.Frame(root, bg="#ffffff")
    canvas.create_window(width//2, current_y, window=temp_cond_frame)
    temp_label_panel = tk.Label(temp_cond_frame, text="--°", font=("Helvetica", 48, "bold"), bg="#ffffff", fg="#2c3e50")
    temp_label_panel.pack(side="left")
    condition_label_panel = tk.Label(temp_cond_frame, text="", font=("Helvetica", 20), bg="#ffffff", fg="#2c3e50")
    condition_label_panel.pack(side="left", padx=20)
    current_y += 100

    # Additional info
    info_frame = tk.Frame(root, bg="#ffffff")
    canvas.create_window(width//2, current_y, window=info_frame)
    info_labels = {}
    for key in ["Feels like", "Humidity", "Pressure", "Wind"]:
        lbl = tk.Label(info_frame, text=f"{key}: --", font=("Helvetica", 14), bg="#ffffff", fg="#2c3e50", width=20, anchor="w")
        lbl.pack(pady=2)
        info_labels[key] = lbl
    current_y += 100

    # ------------------- Mini forecast boxes -------------------
    forecast_canvas = tk.Canvas(root, width=panel_width, height=panel_height//3, bg="#ffffff", highlightthickness=0)
    canvas.create_window(width//2, panel_y+panel_height - panel_height//6, window=forecast_canvas)

    forecast_labels=[]
    forecast_box_width = 120
    forecast_box_height = 90
    forecast_box_radius = 15
    spacing = 20

    def create_forecast_box(canvas, x, y, w, h, r, bg="#ecf0f1"):
        points = [
            x+r, y, x+w-r, y, x+w, y, x+w, y+r,
            x+w, y+h-r, x+w, y+h, x+w-r, y+h, x+r, y+h,
            x, y+h, x, y+h-r, x, y+r, x, y
        ]
        return canvas.create_polygon(points, smooth=True, fill=bg, outline="")

    for i in range(4):
        fx = i*(forecast_box_width + spacing) - ((4-1)*(forecast_box_width+spacing))//2
        fy = 10
        box = create_forecast_box(forecast_canvas, fx, fy, forecast_box_width, forecast_box_height, forecast_box_radius)
        lbl = tk.Label(forecast_canvas, text="--°\n--:--", font=("Helvetica", 12), bg="#ecf0f1", fg="#2c3e50")
        forecast_canvas.create_window(fx+forecast_box_width//2, fy+forecast_box_height//2, window=lbl)
        forecast_labels.append(lbl)

    # ------------------- Weather Effects -------------------
    cloud_items, rain_items = [], []

    def create_clouds(n=5):
        for _ in range(n):
            x=random.randint(0,width); y=random.randint(0,height//2)
            c=canvas.create_oval(x,y,x+100,y+50,fill="#ecf0f1",outline="")
            cloud_items.append(c)
    def move_clouds():
        for c in cloud_items:
            canvas.move(c,1,0); x,y,_,_=canvas.coords(c)
            if x>width: canvas.move(c,-width-100,0)
        root.after(50, move_clouds)
    def create_rain(n=50):
        for _ in range(n):
            x=random.randint(0,width); y=random.randint(0,height//2)
            r=canvas.create_line(x,y,x,y+10,fill="#3498db",width=2); rain_items.append(r)
    def move_rain():
        for r in rain_items:
            canvas.move(r,0,10); x,y,_,_=canvas.coords(r)
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
            temp_label_panel.config(text="--°")
            condition_label_panel.config(text="")
            for k in info_labels: info_labels[k].config(text=f"{k}: --")

            lat, lon, name = geocode_city(city)
            weather = get_current_weather(lat, lon)
            desc = weather["weather"][0]["description"].title()
            temp = round(weather["main"]["temp"])
            feels_like = round(weather["main"]["feels_like"])
            humidity = weather["main"]["humidity"]
            pressure = weather["main"]["pressure"]
            wind_speed = weather["wind"]["speed"]
            main_weather = weather["weather"][0]["main"].lower()

            # Weather effects
            icon_file="sun.png"
            clear_effects()
            if "cloud" in main_weather: icon_file="cloud.png"; create_clouds(); move_clouds()
            elif "rain" in main_weather: icon_file="rain.png"; create_rain(); move_rain()
            elif "snow" in main_weather: icon_file="snow.png"

            img = load_icon(icon_file,(120,120))
            icon_label.image = ImageTk.PhotoImage(img)
            icon_label.config(image=icon_label.image)

            temp_label.config(text=f"{temp}°", fg="white")
            condition_label.config(text=desc, fg="white")
            location_label.config(text=f"📍 {name}")
            temp_label_panel.config(text=f"{temp}°")
            condition_label_panel.config(text=desc)
            info_labels["Feels like"].config(text=f"Feels like: {feels_like}°C")
            info_labels["Humidity"].config(text=f"Humidity: {humidity}%")
            info_labels["Pressure"].config(text=f"Pressure: {pressure} hPa")
            info_labels["Wind"].config(text=f"Wind: {wind_speed} m/s")

            for i,lbl in enumerate(forecast_labels):
                lbl.config(text=f"{temp+i}°\n{(now.hour+i)%24}:00")

            if "sun" in icon_file.lower(): rotate_sun()

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
