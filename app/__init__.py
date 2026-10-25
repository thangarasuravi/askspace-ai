"""AskSpace AI Application Factory."""

import os
from pathlib import Path
from flask import Flask
from app.config import Config
from app.extensions import db


def create_app(config_class=Config) -> Flask:
    """Initialize and configure AskSpace AI Flask application."""
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder='static',
        template_folder='templates'
    )
    app.config.from_object(config_class)

    # Ensure instance directory exists
    instance_dir = Path(app.config.get('INSTANCE_PATH', app.instance_path))
    instance_dir.mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from app.routes.pages import pages_bp
    from app.routes.chat import chat_bp
    from app.routes.conversations import conversations_bp
    from app.routes.notebook import notebook_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(conversations_bp, url_prefix='/api')
    app.register_blueprint(notebook_bp, url_prefix='/api')
    app.register_blueprint(settings_bp, url_prefix='/api')

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response

    # Initialize database tables
    with app.app_context():
        from app.models.conversation import Conversation
        from app.models.message import Message
        from app.models.notebook import NotebookEntry
        from app.models.preference import UserPreference
        
        db.create_all()

        # Seed initial default preference
        if not UserPreference.query.filter_by(preference_key='theme').first():
            UserPreference.set('theme', 'dark')

    return app
