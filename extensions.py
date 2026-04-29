"""
Shared Flask extensions — initialized here, imported everywhere.
This prevents circular imports by defining db outside of app.py.
"""

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance (bound to app later via db.init_app(app))
db = SQLAlchemy()
