import tkinter as tk
from tkinter import messagebox
from api_client import geocode_city, get_current_weather

def start_gui():
    """Enhanced version of your original weather GUI"""
    root = tk.Tk()
    root.title("Weather App")
    root.geometry("500x400")
    root.configure(bg='#1e3c72')
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (500 // 2)
    y = (root.winfo_screenheight() // 2) - (400 // 2)
    root.geometry(f"500x400+{x}+{y}")

    # Title
    title_label = tk.Label(
        root, 
        text="🌤️ Weather App", 
        font=("Helvetica", 20, "bold"),
        bg='#1e3c72', 
        fg='white'
    )
    title_label.pack(pady=20)

    # City input
    tk.Label(
        root, 
        text="City:", 
        font=("Helvetica", 12),
        bg='#1e3c72', 
        fg='white'
    ).pack()
    
    city_entry = tk.Entry(
        root, 
        font=("Helvetica", 12),
        width=20,
        relief='flat',
        bd=5
    )
    city_entry.pack(pady=10)
    city_entry.insert(0, "London")

    # Result display
    result_label = tk.Label(
        root, 
        text="", 
        justify="left",
        font=("Helvetica", 11),
        bg='white',
        fg='#1e3c72',
        relief='flat',
        bd=0,
        wraplength=400,
        width=40,
        height=10
    )
    result_label.pack(pady=20, padx=20, fill='both', expand=True)

    def fetch_weather():
        city = city_entry.get()
        if not city:
            messagebox.showerror("Error", "Enter a city name")
            return
        try:
            # Update result to show loading
            result_label.config(text="🔄 Loading weather data...")
            root.update_idletasks()
            
            lat, lon, name = geocode_city(city)
            weather = get_current_weather(lat, lon)
            
            desc = weather["weather"][0]["description"].title()
            temp = round(weather["main"]["temp"])
            feels_like = round(weather["main"]["feels_like"])
            humidity = weather["main"]["humidity"]
            pressure = weather["main"]["pressure"]
            wind_speed = weather["wind"]["speed"]
            
            # Format the result beautifully
            result_text = f"""📍 {name}

🌡️ Temperature: {temp}°C
🌡️ Feels like: {feels_like}°C
☁️ Condition: {desc}

💧 Humidity: {humidity}%
📊 Pressure: {pressure} hPa
💨 Wind Speed: {wind_speed} m/s"""
            
            result_label.config(text=result_text)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            result_label.config(text="❌ Failed to fetch weather data")

    # Search button
    search_btn = tk.Button(
        root, 
        text="🔍 Search Weather", 
        command=fetch_weather,
        font=("Helvetica", 12, "bold"),
        bg='#74b9ff',
        fg='white',
        relief='flat',
        bd=0,
        padx=20,
        pady=10,
        cursor='hand2'
    )
    search_btn.pack(pady=10)
    
    # Bind Enter key to search
    city_entry.bind('<Return>', lambda e: fetch_weather())
    
    # Hover effects
    def on_enter(e):
        search_btn.config(bg='#2a5298')
    def on_leave(e):
        search_btn.config(bg='#74b9ff')
    
    search_btn.bind('<Enter>', on_enter)
    search_btn.bind('<Leave>', on_leave)
    
    root.mainloop()

if __name__ == "__main__":
    start_gui()