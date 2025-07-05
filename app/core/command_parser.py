# In app/core/command_parser.py
import re
from app.features import openai_handler, system, weather, fun, lights
from app.core import custom_commands
from app.features import app_launcher
from app.features import openai_lights
from app.features import todo
from app.features import briefing
from app.features import network_tools
from app.features import media_control

def parse_command(command_text: str) -> dict:
    """
    Parses the user's command and routes it to the appropriate function.
    """
    command = command_text.lower()

    if "hello" in command or "hi" in command:
        return {'response_text': 'Hello! How can I assist you today?', 'speak_response': True}
    
    elif "daily briefing" in command or "morning briefing" in command:
        response = briefing.generate_daily_briefing()
        return {'response_text': response, 'speak_response': True}

    # --- Media Control Commands (Now Silent) ---
    elif "play" in command and "pause" in command or "toggle media" in command:
        return {'response_text': media_control.play_pause_media(), 'speak_response': False}
    elif "next track" in command or "next song" in command:
        return {'response_text': media_control.next_track(), 'speak_response': False}
    elif "previous track" in command or "previous song" in command:
        return {'response_text': media_control.previous_track(), 'speak_response': False}
    elif "volume up" in command:
        return {'response_text': media_control.volume_up(), 'speak_response': False}
    elif "volume down" in command:
        return {'response_text': media_control.volume_down(), 'speak_response': False}
    elif "mute" in command:
        return {'response_text': media_control.mute_unmute_volume(), 'speak_response': False}

    elif "start movie mode" in command or "start work mode" in command or "start code mode" in command:
        return custom_commands.handle_custom_command(command)

    elif "turn on my pc" in command or "wake my pc" in command:
        return {'response_text': system.wake_on_lan_pc(), 'speak_response': True}

    # --- Network Tools ---
    elif command.startswith("ping"):
        host = command.replace("ping", "").strip()
        response = network_tools.ping_host(host)
        return {'response_text': response, 'speak_response': False}

    elif "speed test" in command or "internet speed" in command:
        response = network_tools.run_speed_test()
        return {'response_text': response, 'speak_response': True}

    # --- To-Do List Commands ---
    elif "clear my to-do list" in command:
        response = todo.clear_tasks()
        return {'response_text': response, 'speak_response': True}
    
    elif "what's on my to-do list" in command or "show my to-do list" in command:
        response = todo.get_tasks()
        return {'response_text': response, 'speak_response': True}

    elif command.startswith("add to my to-do list"):
        task = command.replace("add to my to-do list", "").strip()
        response = todo.add_task(task)
        return {'response_text': response, 'speak_response': True}

    # --- Lights, Weather, Music, etc. ---
    elif any(keyword in command for keyword in ["light", "lights", "lamp", "hue", "dim", "brighten", "color"]):
        return openai_lights.handle_light_command(command_text)

    elif "weather" in command:
        return {'response_text': weather.get_weather(), 'speak_response': True}

    elif "open youtube music" in command or command == "play music":
        return {'response_text': system.open_youtube_music(), 'speak_response': True}
    
    # --- Other System Commands ---
    elif "cpu status" in command or "cpu usage" in command:
        return {'response_text': system.get_cpu_usage(), 'speak_response': True}
    elif "ram usage" in command or "memory status" in command:
        return {'response_text': system.get_ram_usage(), 'speak_response': True}
    elif "cpu temperature" in command:
        return {'response_text': system.get_cpu_temperature(), 'speak_response': True}
    elif "gpu info" in command:
        return {'response_text': system.get_gpu_info(), 'speak_response': True}
    elif "what time is it" in command or "current time" in command:
        return {'response_text': system.get_current_datetime_info(), 'speak_response': True}
    
    elif "joke" in command:
        return {'response_text': fun.tell_joke(), 'speak_response': True}
    elif "tell me a fact" in command or "random fact" in command:
        return {'response_text': fun.get_random_fact(), 'speak_response': True}

    elif "shutdown computer" in command:
        return {'response_text': system.shutdown_system(), 'speak_response': True}
    elif "reboot computer" in command:
        return {'response_text': system.reboot_system(), 'speak_response': True}

    elif "go to my site" in command or "show my site" in command or command == "beautech.nl":
        system.open_web_page("http://beautech.nl") 
        return {'response_text': "", 'speak_response': False}

    elif command.startswith("open website") or command.startswith("go to") or command.startswith("look up"):
        url_match = re.match(r"^(?:open website|go to|look up)\s+(.+)$", command)
        if url_match:
            url = url_match.group(1).strip()
            if not url.startswith(("http://", "https://")):
                url = "http://" + url 
            system.open_web_page(url)
            return {'response_text': "", 'speak_response': False}
        else:
            return {'response_text': "Please specify a website to open.", 'speak_response': True}

    app_launch_match = re.match(r"^(open|launch|start)\s+(.+)$", command)
    if app_launch_match:
        app_name = app_launch_match.group(2).strip()
        response_text = app_launcher.launch_app(app_name)
        return {'response_text': response_text, 'speak_response': True}

    else:
        return {'response_text': openai_handler.ask_openai(command), 'speak_response': True}
