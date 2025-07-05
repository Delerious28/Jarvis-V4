# In app/__init__.py
from flask import Flask
import os

def create_app():
    app = Flask(__name__)

    # Ensure the data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Import and register blueprints
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
