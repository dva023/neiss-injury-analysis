from flask import Flask
from flask_cors import CORS

from config import Config


def create_app(config_class=Config) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)

    # Register blueprints
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    return app
