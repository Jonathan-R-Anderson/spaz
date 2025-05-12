
from shared import (
    db, app
)
from blueprints.routes import blueprint

app.register_blueprint(blueprint)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5003, debug=True)
