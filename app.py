"""
KLP (Kanhaiya Lal Polytechnic) Roorkee - Student Result Website
Main Flask application entry point.
"""

import os
from flask import Flask
from extensions import db
from routes.main import main_bp
from routes.admin import admin_bp
from routes.result import result_bp

# ─── App Factory ─────────────────────────────────────────────────────────────

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Secret key for session management (from environment or fallback)
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'klp-roorkee-secret-2024')

    # SQLite database stored in the project directory
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'klp_database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Suppress deprecation warning

    # Initialize database with app
    db.init_app(app)

    # Register route blueprints
    app.register_blueprint(main_bp)       # Public pages (home, about, departments, etc.)
    app.register_blueprint(admin_bp)      # Admin panel for uploading data
    app.register_blueprint(result_bp)     # Student result lookup

    # Create all database tables on startup
    with app.app_context():
        db.create_all()

    return app


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=False)
