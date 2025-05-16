from api import create_app
from system.logging import setup_logger
from utils.files import ensure_static_dirs

# Setup logging and directories before creating app
setup_logger()
ensure_static_dirs()

# Create the Flask app instance
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
