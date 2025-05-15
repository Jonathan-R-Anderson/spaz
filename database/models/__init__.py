from .user import Users
from .magnet import MagnetURL

__all__ = ['Users', 'MagnetURL']

# Also ensure the modules are loaded for SQLAlchemy to register them
from . import user
from . import magnet
