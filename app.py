"""
Flask application setup for the Gemini Batch Prediction web interface.
"""
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from sqlalchemy.orm import DeclarativeBase


# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
session = Session()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    # Set session to use filesystem instead of signed cookies
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_DIR"] = "flask_session"
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = 1800  # 30 minutes
    # Use SQLite as a fallback if DATABASE_URL is not set
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///gemini_app.db"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    session.init_app(app)
    
    with app.app_context():
        # Register blueprints
        from routes.main import main_bp
        from routes.auth import auth_bp
        from routes.transcripts import transcripts_bp
        from routes.questions import questions_bp
        from routes.video_questions import video_questions_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(transcripts_bp, url_prefix='/transcripts')
        app.register_blueprint(questions_bp, url_prefix='/questions')
        app.register_blueprint(video_questions_bp, url_prefix='/video-questions')
        
        # Import models and create tables
        import models
        db.create_all()
        
        # Load user callback for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            return models.User.query.get(int(user_id))
            
        return app


# Create app instance for WSGI servers
app = create_app()