from flask import Flask
import logging

try:
    from flask_cors import CORS
except ImportError:
    raise ImportError("flask-cors not found. Please install with: pip install flask-cors")

def create_app():
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize components
    from app.nlp_utils import load_skills
    from app.recommender import get_skill_gap, recommend_roles

    # Register blueprints
    from app.routes import main_routes
    app.register_blueprint(main_routes)

    return app


