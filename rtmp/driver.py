from api import create_app
from system.logging import setup_logging
from utils.files import ensure_static_dirs
setup_logging()
ensure_static_dirs()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
