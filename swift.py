import pygame
import time
import requests
from datetime import datetime
import sys
import os

def get_resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_chance_of_rain():
    # Hassocks latitude and longitude
    lat = 50.92
    lon = -0.14
    
    # Open-Meteo is a free API that does not require a key
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation_probability&forecast_days=1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Get the precipitation probability for the current hour
        current_hour = datetime.now().hour
        chance_of_rain = data['hourly']['precipitation_probability'][current_hour]
        return chance_of_rain
        
    except Exception as e:
        print(f"Could not retrieve weather data: {e}")
        # Return 0% chance of rain if the check fails, to prevent playing in potentially bad weather
        return 0

def is_within_time_window(start,end):
    sh,sm = start.split(":")
    eh,em = end.split(":")
    now = datetime.now()
    start_time = now.replace(hour=int(sh), minute=int(sm), second=0, microsecond=0)
    end_time = now.replace(hour=int(eh), minute=int(em), second=0, microsecond=0)
    
    within =  start_time <= now <= end_time
    return within

def run_swift_caller(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    
    is_playing = False
    
    print("Swift caller program started. Press Ctrl+C to exit.")
    
    while True:
        is_morning = is_within_time_window("6:30","11:30")
        is_evening = is_within_time_window("16:00","20:30")
        if is_morning or is_evening:
            chance_of_rain = get_chance_of_rain()
            print(f"[{datetime.now().strftime('%H:%M')}] Time is within window. Chance of rain in Hassocks: {chance_of_rain}%")
            
            if chance_of_rain < 50:
                if not is_playing:
                    print("Conditions met. Starting playback.")
                    pygame.mixer.music.play(loops=-1)
                    is_playing = True
            else:
                if is_playing:
                    print("Rain chance is 50% or higher. Stopping playback.")
                    pygame.mixer.music.stop()
                    is_playing = False
        else:
            if is_playing:
                print(f"[{datetime.now().strftime('%H:%M')}] Not morning or evening. Stopping playback.")
                pygame.mixer.music.stop()
                is_playing = False
                
        # Wait 10 minutes (600 seconds) before checking the conditions again
        time.sleep(600)

if __name__ == "__main__":
    # Ensure swift.mp3 is in the same directory as this script
    run_swift_caller(get_resource_path("swift.mp3"))
