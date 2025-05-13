from flask import Blueprint

blueprint = Blueprint('main', __name__)

# Register views from individual modules
from .views import dashboard, rtmp, magnet, session, internal
