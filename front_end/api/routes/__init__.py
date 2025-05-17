from flask import Blueprint

# Define the main blueprint for views
blueprint = Blueprint('main', __name__)

# Import view modules to register their routes
from api.routes.views import dashboard, rtmp, magnet, session, internal

# Import sub-blueprints
from .verify_proxy import verify_bp
from .dynamic_loader import dynamic_bp

__all__ = ['blueprint', 'verify_bp', 'dynamic_bp']
