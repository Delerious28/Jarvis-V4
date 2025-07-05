# In app/core/custom_commands.py
import subprocess
import os
import time

# IMPORTANT: These imports are essential for your custom commands to work.
from app.features import system
from app.features import app_launcher
from app.features import lights # Assuming lights.py is in app/features

def handle_custom_command(command: str) -> dict:
    """
    Handles custom 'mode' commands like "start movie mode", "start work mode", "start code mode".
    This function defines what happens when each mode is activated.
    You need to CUSTOMIZE the actions within each 'if' block.

    Args:
        command (str): The specific command issued (e.g., "start movie mode").

    Returns:
        dict: A dictionary containing 'response_text' (what Jarvis says)
              and 'speak_response' (boolean indicating if Jarvis should speak).
    """
    response_text = "" # Default to no response text
    speak_response = False # Default to no spoken response for modes

    if "start movie mode" in command:
        print("Custom Commands: Movie mode activated.")
        
        # --- CUSTOMIZE YOUR MOVIE MODE ACTIONS BELOW ---
        # ALL LIGHT ACTIONS TARGET THE "Slaapkamer" GROUP
        lights.turn_light_on("Slaapkamer") 
        lights.change_light_brightness("Slaapkamer", 13) # 5% brightness
        lights.change_light_color("Slaapkamer", "orange") # Orange color

        # Open movies.html - YOU MUST REPLACE THE PLACEHOLDER PATH BELOW!
        # This uses your default web browser. If a browser is already open,
        # it will typically open in a new tab or window within that existing instance.
        # There's no simple way in Python to check if a specific URL is *already* open in a tab.
        # Example on Windows: "file:///C:/Users/YourUser/Path/To/Your/Project/templates/movies.html"
        # Example on macOS/Linux: "file:///Users/YourUser/Path/To/Your/Project/templates/movies.html"
        # Use forward slashes (/) even on Windows for file:/// URLs.
        movies_html_path = "app/templates/movies.html" # ADJUST THIS PATH!
        system.open_web_page(movies_html_path)
        
        # Example: Open a streaming service in a browser
        # system.open_web_page("https://www.netflix.com") 
        # Or launch an application from your app_config.json
        # app_launcher.launch_app("VLC Media Player") 
        # -----------------------------------------------
        
    elif "start work mode" in command:
        print("Custom Commands: Work mode activated.")
        
        # --- CUSTOMIZE YOUR WORK MODE ACTIONS BELOW ---
        # ALL LIGHT ACTIONS TARGET THE "Slaapkamer" GROUP
        lights.turn_light_on("Slaapkamer")
        lights.change_light_brightness("Slaapkamer", 127) # 50% brightness
        
        # Open Microsoft Teams
        app_launcher.launch_app("Microsoft Teams")
        
        # Example: Open other specific work applications
        # app_launcher.launch_app("Visual Studio Code")
        # app_launcher.launch_app("Microsoft Outlook")
        
        # Example: Open work-related websites
        # system.open_web_page("https://teams.microsoft.com") # Use this if launching app doesn't work or you prefer web
        # -----------------------------------------------
        
    elif "start code mode" in command:
        print("Custom Commands: Code mode activated.")
        
        # --- CUSTOMIZE YOUR CODE MODE ACTIONS BELOW ---
        # ALL LIGHT ACTIONS TARGET THE "Slaapkamer" GROUP
        lights.turn_light_on("Slaapkamer")
        lights.change_light_color("Slaapkamer", "blue")
        lights.change_light_brightness("Slaapkamer", 180)
        
        # Example 2: Open IDE/text editor
        app_launcher.launch_app("PyCharm")
        
        # Example 3: Open documentation websites
        system.open_web_page("https://docs.python.org/3/")
        # -----------------------------------------------
        
    else:
        response_text = "I'm not sure which mode you want to start. Please specify 'movie mode', 'work mode', or 'code mode'."
        speak_response = True # Keep speaking for unclear commands

    return {'response_text': response_text, 'speak_response': speak_response}