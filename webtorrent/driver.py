from system.logging import setup_logging
from api import create_app

setup_logging()
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)
