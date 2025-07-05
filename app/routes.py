# In app/routes.py
from flask import Blueprint, render_template, request, jsonify, send_file
from app.core.command_parser import parse_command
from app.features import lights, system, weather
import json
import os
from gtts import gTTS
from io import BytesIO
from app.features import todo
# --- New Import ---

# Create a Blueprint instance
bp = Blueprint('main', __name__)

# Define the path for the UI config file
UI_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'ui_config.json')

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/api/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command_text = data.get('command')
    if not command_text:
        return jsonify({'error': 'No command provided'}), 400
    response = parse_command(command_text)
    return jsonify(response)



@bp.route('/api/tts', methods=['GET'])
def get_text_to_speech():
    text = request.args.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    try:
        audio_fp = BytesIO()
        tts = gTTS(text=text, lang='en')
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return send_file(audio_fp, mimetype='audio/mpeg')
    except Exception as e:
        print(f"TTS Generation Error: {e}")
        return jsonify({'error': 'Failed to generate speech'}), 500

@bp.route('/api/status', methods=['GET'])
def get_system_status():
    status = {
        'cpu': system.get_cpu_usage(),
        'ram': system.get_ram_usage(),
        'temp': system.get_cpu_temperature(),
        'weather': weather.get_weather()
    }
    return jsonify(status)

@bp.route('/api/todo', methods=['GET'])
def get_todo_list():
    tasks = todo.get_tasks_for_api()
    return jsonify(tasks)

@bp.route('/api/todo/clear', methods=['POST'])
def clear_todo_list():
    todo.clear_tasks()
    return jsonify({'success': True, 'message': 'To-do list cleared.'})

@bp.route('/api/lights', methods=['GET'])
def get_lights_data():
    all_light_names = lights.get_all_light_names()
    if isinstance(all_light_names, str):
        return jsonify({'error': all_light_names}), 500
    try:
        with open(UI_CONFIG_PATH, 'r') as f:
            config = json.load(f)
            visible_lights = config.get('visible_lights', [])
    except (FileNotFoundError, json.JSONDecodeError):
        visible_lights = []
    return jsonify({
        'all_lights': all_light_names,
        'visible_lights': visible_lights
    })

@bp.route('/api/lights/config', methods=['POST'])
def update_lights_config():
    data = request.get_json()
    new_visible_lights = data.get('visible_lights')
    if new_visible_lights is None:
        return jsonify({'error': 'No visible_lights list provided'}), 400
    try:
        with open(UI_CONFIG_PATH, 'w') as f:
            json.dump({'visible_lights': new_visible_lights}, f, indent=2)
        return jsonify({'success': True, 'message': 'Configuration saved.'})
    except IOError as e:
        return jsonify({'error': f'Failed to write to config file: {e}'}), 500
