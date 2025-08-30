"""
ElevatrAI Application Entry Point

This is the main entry point for the ElevatrAI career development platform. It initializes
and configures the Flask application with appropriate environment settings for both
development and production environments.

Key Features:
- Configurable port and debug settings via environment variables
- Secure host binding (localhost for development, all interfaces for production)
- Environment-aware configuration loading

Environment Variables:
    SECRET_KEY: Flask session encryption key (required in production)
    FLASK_ENV: 'development' or 'production' (default: production)
    PORT: Port number to run the server on (default: 5000)

Usage:
    # Development
    $ export FLASK_ENV=development
    $ python run.py

    # Production
    $ export FLASK_ENV=production
    $ gunicorn 'run:app'

Author: Anslem Akadu
Project: ElevatrAI - AI-Powered Career Development Platform
"""

# import os
# from app import create_app

# # Initialize the Flask application with our factory pattern
# app = create_app()

# if __name__ == "__main__":
    
#     # Load environment-specific settings
#     port = int(os.getenv("PORT", 5000))
#     debug = os.getenv("FLASK_ENV", "production") == "development"
    
#     # Security: Only bind to localhost in development mode
#     # In production, we'll bind to all interfaces for container/cloud compatibility
#     host = '127.0.0.1' if debug else '0.0.0.0'
    
#     # Start the development server
#     # Note: For production, use gunicorn (see Procfile)
#     app.run(host=host, port=port, debug=debug)
    


