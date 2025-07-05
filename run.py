# In run.py
from app import create_app #

app = create_app() #

if __name__ == '__main__':
    # Note: Setting debug=True is for development only.
    # For production, use a proper WSGI server like Gunicorn or Waitress.
    app.run(host='0.0.0.0', port=5000, debug=True) #