from flask import Flask
from flask_cors import CORS
import os

def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static')
    )
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    CORS(app)
    
    print(f"Template folder: {app.template_folder}")
    
    from app.routes import main
    app.register_blueprint(main)
    
    return app
| Set-Content -Path "app\__init__.py" -Encoding UTF8