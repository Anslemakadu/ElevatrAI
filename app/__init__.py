"""
ElevatrAI - Career Development and Skill Analysis Platform

This module implements the application factory pattern for Flask, providing a clean
and modular way to create the application instance. It handles all core initialization
including configuration loading, blueprint registration, and security settings.

Key Components:
- Flask application factory
- Security configurations
- Blueprint registration
- File upload limits

The factory pattern allows for:
- Multiple instances of the app (e.g., testing)
- Dynamic configuration
- Easier unit testing
- Blueprint-based modularization

Author: Anslem Akadu
"""
import os
from flask import Flask

def create_app():
    """
    Create and configure a Flask application instance using the factory pattern.
    
    This factory function encapsulates all the initialization logic for the ElevatrAI
    platform, including security settings, blueprints, and upload configurations.
    
    Returns:
        Flask: A configured Flask application instance ready to serve requests
        
    Example:
        To create an application instance:
        >>> from app import create_app
        >>> app = create_app()
        >>> app.run()
    """
    app = Flask(__name__)
    
    # Security Configuration
    # In production, SECRET_KEY must be set as an environment variable
    app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-in-prod')
    
    # File Upload Configuration
    # Limit upload size to 16MB to prevent memory issues
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Register route blueprints
    # Blueprints help organize routes into logical modules
    from app.routes import main_routes
    app.register_blueprint(main_routes)
    
    # TODO: Add error handlers for common HTTP errors (404, 500)
    # TODO: Add logging configuration for production
    # TODO: Add monitoring/metrics endpoints
    
    return app

app = create_app()

if __name__ == "__main__":
    
    # Load environment-specific settings
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "production") == "development"
    
    # Security: Only bind to localhost in development mode
    # In production, we'll bind to all interfaces for container/cloud compatibility
    host = '127.0.0.1' if debug else '0.0.0.0'
    
    # Start the development server
    # Note: For production, use gunicorn (see Procfile)
    app.run(host=host, port=port, debug=debug)
    
    