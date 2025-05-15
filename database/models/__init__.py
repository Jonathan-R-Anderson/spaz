# models/__init__.py

# These two lines force SQLAlchemy to evaluate the model classes
from . import user
from . import magnet

# These make them importable elsewhere
from .user import Users
from .magnet import MagnetURL

__all__ = ['Users', 'MagnetURL']
