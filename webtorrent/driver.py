from api import create_app
from system.logging import setup_logging

setup_logging()
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
