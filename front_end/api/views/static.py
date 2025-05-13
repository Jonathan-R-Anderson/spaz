from flask import send_from_directory
from ..routes import blueprint
import os, logging




@blueprint.route('/css/<filename>')
def serve_css(filename):
    logging.debug(f"Serving CSS file: {filename}")
    return send_from_directory(os.path.join('hosted', 'css'), filename)

@blueprint.route('/js/<filename>')
def serve_js(filename):
    logging.debug(f"Serving JS file: {filename}")
    return send_from_directory(os.path.join('hosted', 'js'), filename)