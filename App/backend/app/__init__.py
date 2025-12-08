"""
Flask application factory
"""
from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__,
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    
    # Load configuration
    app.config.from_object('config')
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    from app.database import init_db, import_sample_data, create_default_admin
    init_db()
    create_default_admin()
    import_sample_data()
    
    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.user_routes import user_bp
    from app.routes.api_routes import api_bp
    from app.routes.main_routes import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Swagger UI configuration
    SWAGGER_URL = '/swagger'
    API_URL = '/api/swagger.json'
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Library Online API",
            'docExpansion': 'list',
            'defaultModelsExpandDepth': 3,
            'defaultModelExpandDepth': 3,
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    return app

