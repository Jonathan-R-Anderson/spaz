# app.py
from flask import Flask
from config import Config
from extensions import db, redis_client
from models import User, MagnetURL
from blueprints.routes import blueprint

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

app.register_blueprint(blueprint)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003, debug=True)
