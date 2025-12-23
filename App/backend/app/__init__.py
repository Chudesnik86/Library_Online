"""
Flask application factory
"""
from flask import Flask, request, jsonify
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
    from app.database import init_db, import_sample_data, create_default_admin, migrate_to_new_structure
    init_db()
    create_default_admin()
    import_sample_data()
    migrate_to_new_structure()  # Migrate existing data to new structure
    
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
    
    # Global error handler for API routes to ensure JSON responses
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all exceptions and return JSON response"""
        import traceback
        error_details = traceback.format_exc()
        print(f"Unhandled exception: {error_details}")
        
        # Check if this is an API route
        if request.path.startswith('/api'):
            return jsonify({
                'success': False,
                'error': str(e),
                'type': type(e).__name__
            }), 500
        
        # For non-API routes, let Flask handle it normally
        raise
    
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

