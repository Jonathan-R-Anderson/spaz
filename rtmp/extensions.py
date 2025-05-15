from flask_sqlalchemy import SQLAlchemy
from redis import Redis

db = SQLAlchemy()
redis_client = Redis(host='localhost', port=6379, db=0)
