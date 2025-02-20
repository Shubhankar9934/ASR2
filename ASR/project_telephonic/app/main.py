# project_telephonic/app/main.py
from flask import Flask
from flask_cors import CORS
import logging
from project_telephonic.utils.logger import setup_logger
from project_telephonic.app.routes import bp as api_bp

def create_app():
    setup_logger()
    app = Flask(__name__)
    CORS(app)
    app.register_blueprint(api_bp, url_prefix="/api")
    return app

if __name__ == "__main__":
    app = create_app()
    logging.info("Starting Flask server on 0.0.0.0:5000. Press Ctrl+C to stop.")
    app.run(host="0.0.0.0", port=5000, debug=False)
