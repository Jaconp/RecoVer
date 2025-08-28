import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)

print("Starting application initialization...")

class Base(DeclarativeBase):
    pass

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key-for-development")

# Apply proxy fix for HTTPS
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
database_url = os.environ.get("DATABASE_URL")
print(f"Database URL (masked): {'*' * (len(database_url) if database_url else 0)}")

# Fix potential "postgres://" to "postgresql://" conversion for SQLAlchemy 1.4+
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    print("Fixed database URL prefix")

# Configure the app
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Initialize extensions
db = SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Initialize the application
with app.app_context():
    print("Creating database tables...")
    try:
        # Import models (must be after db initialization)
        import models
        
        # Create database tables if they don't exist
        db.create_all()
        print("Database tables created successfully")
        
        # Register routes and blueprints
        from routes import register_routes
        from auth import auth as auth_blueprint
        
        # Register blueprints
        app.register_blueprint(auth_blueprint)
        
        # Handle Google auth with fallbacks for missing credentials
        try:
            from google_auth import google_auth as google_auth_blueprint
            app.register_blueprint(google_auth_blueprint)
            print("Google auth blueprint registered")
        except Exception as e:
            print(f"Google auth blueprint registration failed: {e}")
            # Continue without Google auth if there's an issue
        
        # Register routes
        register_routes(app)
        print("Routes registered successfully")
        
    except Exception as e:
        print(f"Error during application initialization: {e}")
        import traceback
        traceback.print_exc()

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    try:
        from models import User
        return User.query.get(int(user_id))
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
print("Application initialization completed")
