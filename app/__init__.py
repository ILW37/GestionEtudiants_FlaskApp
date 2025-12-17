from flask import Flask
from flask_cors import CORS
from app.config import Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app
